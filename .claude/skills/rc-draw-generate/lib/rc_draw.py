#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Right Code 画图 CLI。

流程：提交异步任务 -> 轮询 /v1/tasks/{task_id} -> 下载图片 URL。
仅使用 Python 标准库，macOS / Linux / Windows 通用。

协议路由：
  - 内置别名 / gemini 前缀 / nano-banana 前缀 -> Gemini generateContent
  - 其余（gpt-image-* 等）                    -> OpenAI Images generations / edits

多 key：通过 RC_PROFILE_<SLUG>_* 配置多个档案，--profile 选择，--fallback 可选容灾。
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = SKILL_DIR / ".env"
DEFAULT_OUT_DIR = SKILL_DIR / "gen-images"
DEFAULT_PROMPT_FILE = SKILL_DIR / "prompts" / "prompt-image.md"

DEFAULT_BASE_URL = "https://rightapi.ai"
DEFAULT_MODEL = "gpt-image-2"

OPENAI_QUALITIES = ("auto", "low", "medium", "high")
OPENAI_25_QUALITIES = OPENAI_QUALITIES + ("xhigh", "max")
GEMINI_IMAGE_SIZES = ("1K", "2K", "4K")

# 内置模型 -> 协议别名；档案 ALIASES 可覆盖
MODEL_PROTOCOL_ALIASES = {
    "nano-banana": "gemini",
    "nano-banana-2": "gemini",
    "nano-banana-2-lite": "gemini",
    "nano-banana-pro": "gemini",
    "nano-banana-2.1": "gemini",
}

PROFILE_ENV_RE = re.compile(
    r"^RC_PROFILE_([A-Za-z0-9_]+)_(NAME|BASE_URL|KEY|MODEL|MODELS|ALIASES)$"
)

# 常用比例 -> OpenAI 像素尺寸（均为 16 的倍数，符合文档约束）
RATIO_TO_SIZE = {
    "1:1": "1024x1024",
    "4:3": "1024x768",
    "3:4": "768x1024",
    "3:2": "1536x1024",
    "2:3": "1024x1536",
    "16:9": "2048x1152",
    "9:16": "1152x2048",
    "21:9": "2016x864",
    "4:5": "1024x1280",
    "5:4": "1280x1024",
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class ApiError(Exception):
    """带 HTTP 状态与任务号的业务异常。"""

    def __init__(self, message, status=None, body=None, task_id=None, resumable=False):
        super().__init__(message)
        self.status = status
        self.body = body
        self.task_id = task_id
        self.resumable = resumable


def log(message):
    print(message, file=sys.stderr)


def elapsed_text(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, rest = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {rest}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {rest}s"


def human_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024


def load_env_file(path):
    """读取 KEY=VALUE 形式的 .env，忽略注释与空行。"""
    data = {}
    if not path.is_file():
        return data
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            data[key] = value
    return data


def resolve(cli_value, env, key, default=None):
    """优先级：CLI > 已导出环境变量 > .env > 默认值。"""
    if cli_value is not None and cli_value != "":
        return cli_value
    if os.environ.get(key):
        return os.environ[key]
    if env.get(key):
        return env[key]
    return default


def merge_env(env):
    """让已导出的 RC_* 环境变量覆盖 .env。"""
    merged = dict(env)
    for key, value in os.environ.items():
        if key.startswith("RC_"):
            merged[key] = value
    return merged


def detect_protocol(model, aliases=None):
    """模型名 -> 协议；别名优先于前缀判断。"""
    name = (model or "").strip().lower()
    if aliases and name in aliases:
        return aliases[name]
    if name in MODEL_PROTOCOL_ALIASES:
        return MODEL_PROTOCOL_ALIASES[name]
    if name.startswith("gemini") or name.startswith("nano-banana"):
        return "gemini"
    return "openai"


def parse_aliases(text):
    """解析 `模型:协议,模型:协议`。"""
    aliases = {}
    for item in (text or "").split(","):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            log(f"[warn] 忽略无效别名：{item}（格式应为 模型:openai|gemini）")
            continue
        model, protocol = item.split(":", 1)
        model = model.strip().lower()
        protocol = protocol.strip().lower()
        if model and protocol in ("openai", "gemini"):
            aliases[model] = protocol
        else:
            log(f"[warn] 忽略无效别名：{item}（协议只能是 openai / gemini）")
    return aliases


def normalize_profile_slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", (name or "").strip()).strip("_").upper()


def load_profiles(env):
    """从 RC_PROFILE_<SLUG>_* 解析档案；没有档案时生成 DEFAULT 兼容单 key。"""
    raw = {}
    for key, value in env.items():
        match = PROFILE_ENV_RE.match(key)
        if not match:
            continue
        slug, field = match.groups()
        raw.setdefault(slug.upper(), {})[field] = value

    profiles = {}
    for slug, fields in raw.items():
        profiles[slug] = {
            "slug": slug,
            "name": fields.get("NAME") or slug,
            "base_url": (fields.get("BASE_URL") or "").rstrip("/"),
            "key": fields.get("KEY") or "",
            "model": fields.get("MODEL") or "",
            "models": [
                item.strip()
                for item in (fields.get("MODELS") or "").split(",")
                if item.strip()
            ],
            "aliases": parse_aliases(fields.get("ALIASES")),
        }

    if not profiles:
        profiles["DEFAULT"] = {
            "slug": "DEFAULT",
            "name": "default",
            "base_url": "",
            "key": "",
            "model": "",
            "models": [],
            "aliases": {},
        }
    return profiles


def find_profile(profiles, query):
    """按 slug / 展示名 / 归一化名称查找档案。"""
    if not query:
        return None
    query = query.strip()
    lowered = query.lower()
    normalized = normalize_profile_slug(query)
    for slug, profile in profiles.items():
        if slug == normalized or profile["name"].lower() == lowered:
            return slug
    for slug, profile in profiles.items():
        if normalized and normalize_profile_slug(profile["name"]) == normalized:
            return slug
    return None


def profile_choices(profiles):
    return ", ".join(
        f"{item['slug']}({item['name']})"
        if item["name"] != item["slug"]
        else item["slug"]
        for item in profiles.values()
    )


def resolve_profile(profile, args, env):
    """返回 (base_url, api_key, model)，模型不随容灾候选切换。"""
    base_url = (
        args.base_url
        or profile["base_url"]
        or resolve(None, env, "RC_BASE_URL", DEFAULT_BASE_URL)
    ).rstrip("/")
    api_key = profile["key"] or resolve(None, env, "RC_API_KEY", None)
    model = (
        args.model
        or profile["model"]
        or resolve(None, env, "RC_MODEL", DEFAULT_MODEL)
    )
    return base_url, api_key, model


def is_fallback_error(error):
    """只有提交阶段的临时/鉴权/路由问题才值得换档案。"""
    if error.task_id:
        return False
    if error.status is None:
        return True
    return error.status in (401, 403, 404, 429) or 500 <= error.status < 600


def validate_size(size):
    """按文档校验 OpenAI 像素尺寸。"""
    if not size or size == "auto":
        return
    match = re.fullmatch(r"(\d+)x(\d+)", size.strip().lower())
    if not match:
        raise ApiError(f"size 格式错误：{size}。应为 auto 或 宽x高，如 1024x1024")
    width, height = int(match.group(1)), int(match.group(2))
    if width % 16 or height % 16:
        raise ApiError(f"size={size} 不合法：宽和高都必须是 16 的倍数")
    if width > 3840 or height > 3840:
        raise ApiError(f"size={size} 不合法：最大边长不能超过 3840")
    if max(width, height) > 3 * min(width, height):
        raise ApiError(f"size={size} 不合法：长边与短边比不能超过 3:1")
    pixels = width * height
    if pixels < 655360 or pixels > 8294400:
        raise ApiError(
            f"size={size} 不合法：总像素需在 655,360 到 8,294,400 之间（当前 {pixels}）"
        )
    if pixels > 2560 * 1440:
        log(f"[warn] size={size} 属于实验性大图，耗时更长、失败率更高")


def validate_quality(model, quality):
    if not quality:
        return
    allowed = OPENAI_25_QUALITIES if "2.5" in model else OPENAI_QUALITIES
    if quality not in allowed:
        raise ApiError(
            f"quality={quality} 不被 {model} 支持；可选：{', '.join(allowed)}"
        )


def validate_image_size(image_size):
    if not image_size:
        return
    normalized = image_size.strip().upper()
    if normalized not in GEMINI_IMAGE_SIZES:
        raise ApiError(
            f"imageSize={image_size} 不合法；Gemini 只支持 {', '.join(GEMINI_IMAGE_SIZES)}"
        )
    return normalized


def guess_mime(path):
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "image/png"


def read_data_url(path):
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{guess_mime(path)};base64,{encoded}"


def read_inline_data(path):
    return {
        "inline_data": {
            "mime_type": guess_mime(path),
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def download_bytes(url, no_proxy, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    opener = build_opener(no_proxy)
    try:
        with opener.open(req, timeout=timeout) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as error:
        raise ApiError(f"下载图片失败（HTTP {error.code}）：{url}")
    except urllib.error.URLError as error:
        raise ApiError(f"下载图片失败：{error.reason}（{url}）")
    except TimeoutError:
        raise ApiError(f"下载图片超时（{timeout}s）：{url}")


def build_opener(no_proxy):
    if no_proxy:
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener()


def request_json(method, url, api_key, payload=None, timeout=60, no_proxy=False):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    opener = build_opener(no_proxy)
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", "replace")[:4000]
        raise ApiError(
            explain_http_error(error.code, error_body),
            status=error.code,
            body=error_body,
        )
    except urllib.error.URLError as error:
        raise ApiError(f"网络请求失败：{error.reason}。可尝试加 --no-proxy 直连")
    except TimeoutError:
        raise ApiError(f"请求超时（{timeout}s）：{url}")

    text = raw.decode("utf-8", "replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ApiError(f"响应不是合法 JSON：{text[:500]}")


def explain_http_error(status, body):
    hints = {
        400: "参数错误：检查 model / prompt / size / aspectRatio 等字段",
        401: "鉴权失败：检查当前档案的 KEY（或 RC_API_KEY）是否正确",
        403: "无权限：Key 被禁用，或分组未开通该模型",
        404: "路径或模型名不存在",
        429: "触发限流或余额不足",
    }
    hint = hints.get(status)
    if hint is None and 500 <= status < 600:
        hint = "上游临时不可用，稍后再试"
    hint = hint or "请求失败"
    detail = body.strip()
    if detail:
        return f"HTTP {status} · {hint}\n响应：{detail}"
    return f"HTTP {status} · {hint}"


def redact_payload(value):
    """dry-run / verbose 输出时隐藏 base64 大字段。"""
    if isinstance(value, dict):
        return {key: redact_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_payload(item) for item in value]
    if isinstance(value, str):
        if value.startswith("data:") and ";base64," in value:
            return f"<data-url, {len(value)} chars>"
        if len(value) > 200:
            return f"<{len(value)} chars>"
    return value


def build_payload(args, model, prompt, local_images, remote_images, image_size, protocol):
    """构造两种协议的请求体，返回 (protocol, endpoint_path, payload, mode)。"""
    has_images = bool(local_images or remote_images)
    if protocol == "gemini":
        parts = [{"text": prompt}]
        for path in local_images:
            parts.append(read_inline_data(path))
        for url in remote_images:
            data, content_type = download_bytes(url, args.no_proxy, timeout=120)
            mime = (content_type or "").split(";")[0].strip() or "image/png"
            parts.append(
                {
                    "inline_data": {
                        "mime_type": mime,
                        "data": base64.b64encode(data).decode("ascii"),
                    }
                }
            )
        generation_config = {}
        if args.ratio:
            generation_config["imageConfig"] = {
                "aspectRatio": args.ratio,
                "imageSize": image_size or "1K",
            }
        elif image_size:
            generation_config["imageConfig"] = {"imageSize": image_size}
        payload = {
            "async": True,
            "contents": [{"role": "user", "parts": parts}],
        }
        if generation_config:
            payload["generationConfig"] = generation_config
        mode = "gemini_edit" if has_images else "gemini_text"
        endpoint = f"/v1beta/models/{urllib.parse.quote(model, safe='')}:generateContent"
        return "gemini", endpoint, payload, mode

    payload = {"model": model, "prompt": prompt, "n": args.n, "async": True}
    if args.size:
        payload["size"] = args.size
    if args.quality and not args.no_quality:
        payload["quality"] = args.quality
    if args.format:
        payload["output_format"] = args.format
    if args.background:
        payload["background"] = args.background
    if args.moderation:
        payload["moderation"] = args.moderation

    if has_images:
        refs = [read_data_url(path) for path in local_images] + list(remote_images)
        payload["image"] = refs
        endpoint = "/v1/images/edits"
        mode = "image_edit"
    else:
        endpoint = "/v1/images/generations"
        mode = "text"
    return "openai", endpoint, payload, mode


def error_message(result):
    error = result.get("error")
    if isinstance(error, dict):
        return error.get("message") or json.dumps(error, ensure_ascii=False)
    if error:
        return str(error)
    message = result.get("message")
    return str(message) if message else json.dumps(result, ensure_ascii=False)[:500]


def is_complete(result):
    return "data" in result or "candidates" in result


def submit_task(base_url, endpoint, payload, api_key, no_proxy, timeout=180):
    result = request_json(
        "POST",
        base_url + endpoint,
        api_key,
        payload=payload,
        timeout=timeout,
        no_proxy=no_proxy,
    )
    if result.get("status") == "failed":
        raise ApiError(f"提交即失败：{error_message(result)}")
    task_id = result.get("task_id")
    if not task_id:
        # 非异步形态的兜底：直接返回结果
        return None, result
    return str(task_id), result


def poll_task(base_url, task_id, api_key, interval, timeout, no_proxy):
    deadline = time.time() + timeout
    last_progress = None
    consecutive_errors = 0
    while True:
        try:
            result = request_json(
                "GET",
                f"{base_url}/v1/tasks/{urllib.parse.quote(task_id, safe='')}",
                api_key,
                timeout=30,
                no_proxy=no_proxy,
            )
            consecutive_errors = 0
        except ApiError as error:
            transient = error.status is None or 500 <= (error.status or 0)
            consecutive_errors += 1
            if not transient or consecutive_errors > 5:
                raise
            log(f"[warn] 轮询暂时失败，{interval}s 后重试：{error}")
            if time.time() + interval >= deadline:
                raise ApiError(
                    f"轮询超时（{timeout}s），任务 {task_id} 仍在处理中；可用 --task-id {task_id} 续查",
                    task_id=task_id,
                    resumable=True,
                )
            time.sleep(interval)
            continue

        status = result.get("status")
        if status in ("failed", "expired", "canceled"):
            labels = {"failed": "失败", "expired": "已过期", "canceled": "已取消"}
            raise ApiError(f"任务{labels[status]}：{error_message(result)}")
        if is_complete(result):
            return result

        progress = result.get("progress")
        if progress != last_progress:
            label = "排队中" if status == "queued" else "生成中"
            suffix = f" {progress}%" if progress is not None else ""
            log(f"[poll] {label}{suffix} · task={task_id}")
            last_progress = progress

        remaining = deadline - time.time()
        if remaining <= 0:
            raise ApiError(
                f"轮询超时（{timeout}s），任务 {task_id} 仍在处理中；可用 --task-id {task_id} 续查",
                task_id=task_id,
                resumable=True,
            )
        time.sleep(min(interval, remaining))


def extract_urls(result, protocol):
    urls = []
    # 续查（--task-id）时可能没显式指定模型，按响应形状兜底识别
    if "candidates" in result:
        protocol = "gemini"
    elif "data" in result:
        protocol = "openai"
    if protocol == "gemini":
        candidates = result.get("candidates") or []
        for candidate in candidates:
            content = candidate.get("content") or {}
            for part in content.get("parts") or []:
                text = part.get("text") or ""
                urls.extend(re.findall(r"https?://[^\s)\]\"']+", text))
    else:
        for item in result.get("data") or []:
            url = item.get("url")
            if url:
                urls.append(url)
        if not urls and result.get("data"):
            raise ApiError(
                "上游返回了 data 但没有 url（文档说明只返回图片 URL）；请加 --raw 排查"
            )
    # 去重并保序
    seen = set()
    unique = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def unique_path(directory, stem, ext):
    candidate = directory / f"{stem}.{ext}"
    index = 2
    while candidate.exists():
        candidate = directory / f"{stem}-{index}.{ext}"
        index += 1
    return candidate


def pick_extension(url, content_type, fallback):
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
    }
    # 先信服务端 Content-Type，再信 URL 后缀，最后才用请求里声明的格式
    if content_type:
        mime = content_type.split(";")[0].strip().lower()
        if mime in mapping:
            return mapping[mime]
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower().lstrip(".")
    if suffix in ("png", "jpg", "jpeg", "webp"):
        return "jpg" if suffix == "jpeg" else suffix
    if fallback:
        return fallback.lower().lstrip(".")
    return "png"


def open_files(paths):
    if not paths:
        return
    for path in paths:
        try:
            if sys.platform == "darwin":
                os.system(f'open "{path}" >/dev/null 2>&1')
            elif os.name == "nt":
                os.startfile(str(path))  # type: ignore[attr-defined]
            else:
                os.system(f'xdg-open "{path}" >/dev/null 2>&1')
        except Exception:
            pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="Right Code 画图：异步提交、轮询、下载图片 URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  run.sh \"一只戴太空头盔的橘猫\"\n"
            "  run.sh -i ref.png \"把背景换成夜晚雪山，保留主体\"\n"
            "  run.sh -i a.png -i b.png \"把第一张图的商品放进第二张图的场景\"\n"
            "  run.sh -m gemini-3-pro-image-preview --ratio 16:9 --image-size 2K \"未来城市雨夜\"\n"
            "  run.sh --profile IMAGE_HIGH \"指定 key 档案\"\n"
            "  run.sh --profile IMAGE_HIGH --fallback \"提交失败时切换其他档案\"\n"
            "  run.sh --list-profiles   # 查看档案（不显示 key）\n"
            "  run.sh --task-id task_xxx   # 续查已有任务\n"
        ),
    )
    parser.add_argument("prompt", nargs="*", help="提示词；省略时读取 prompts/prompt-image.md")
    parser.add_argument("-p", "--profile", help="配置档案（RC_PROFILE_<SLUG>_*）")
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="提交阶段失败时依次尝试其他档案；拿到 task_id 后绝不切换",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="列出已配置档案与可用模型（不显示 key）",
    )
    parser.add_argument("-m", "--model", help=f"模型名，默认 {DEFAULT_MODEL}")
    parser.add_argument("-i", "--image", action="append", default=[], help="本地参考图，可重复")
    parser.add_argument("--image-url", action="append", default=[], help="公网参考图 URL，可重复")
    parser.add_argument("--size", help="OpenAI 输出尺寸，如 1024x1024 / auto")
    parser.add_argument("--ratio", help="Gemini 宽高比，如 16:9；OpenAI 会自动映射到像素尺寸")
    parser.add_argument("--image-size", help="Gemini 分辨率档位：1K / 2K / 4K")
    parser.add_argument("-q", "--quality", help="OpenAI 质量：auto/low/medium/high/xhigh/max")
    parser.add_argument("--no-quality", action="store_true", help="不发送 quality 字段")
    parser.add_argument("-n", "--n", type=int, default=1, help="OpenAI 生成数量，默认 1")
    parser.add_argument("--format", help="输出格式：png / jpeg / webp（仅 OpenAI）")
    parser.add_argument("--background", help="OpenAI 背景策略，默认 auto；不支持 transparent")
    parser.add_argument("--moderation", help="OpenAI 审核强度：auto / low")
    parser.add_argument("--out-dir", help="图片输出目录，默认 skill 内 gen-images/")
    parser.add_argument("--timeout", type=int, help="整体轮询上限秒数，默认 600")
    parser.add_argument("--poll-interval", type=int, help="轮询间隔秒数，默认 5")
    parser.add_argument("--task-id", help="跳过提交，直接轮询已有任务")
    parser.add_argument("--no-download", action="store_true", help="只打印图片 URL，不下载")
    parser.add_argument("--open", action="store_true", help="下载后用系统程序打开图片")
    parser.add_argument("--no-open", action="store_true", help="兼容旧脚本；默认就不打开")
    parser.add_argument("--dry-run", action="store_true", help="只打印请求体，不发送")
    parser.add_argument("--no-proxy", action="store_true", help="忽略 HTTP(S)_PROXY 直连")
    parser.add_argument("-v", "--verbose", action="store_true", help="打印请求摘要")
    parser.add_argument("--base-url", help="覆盖基础地址")
    parser.add_argument("--env-file", help="覆盖 .env 路径")
    return parser.parse_args()


def print_profiles(profiles, env, default_slug):
    """--list-profiles：只显示元信息，不输出任何 key。"""
    print("---PROFILES---")
    for slug, profile in profiles.items():
        base_url = (
            profile["base_url"]
            or resolve(None, env, "RC_BASE_URL", DEFAULT_BASE_URL)
        ).rstrip("/")
        model = profile["model"] or resolve(None, env, "RC_MODEL", DEFAULT_MODEL)
        has_key = bool(profile["key"] or resolve(None, env, "RC_API_KEY", None))
        marker = " (默认)" if slug == default_slug else ""
        print(f"{slug}{marker}")
        print(f"  name={profile['name']}")
        print(f"  base_url={base_url}")
        print(f"  model={model}")
        print(f"  key={'已配置' if has_key else '缺失'}")
        if profile["models"]:
            print(f"  models={','.join(profile['models'])}")
        if profile["aliases"]:
            print(
                "  aliases="
                + ",".join(f"{key}:{value}" for key, value in profile["aliases"].items())
            )
    print("---END---")


def main():
    started_at = time.time()
    env = merge_env(load_env_file(DEFAULT_ENV_FILE))
    args = parse_args()
    if args.env_file:
        env = merge_env(load_env_file(Path(args.env_file)))

    if args.no_proxy or resolve(None, env, "RC_NO_PROXY", "0") in ("1", "true", "yes"):
        args.no_proxy = True

    timeout = args.timeout or int(resolve(None, env, "RC_TIMEOUT", "600"))
    poll_interval = args.poll_interval or int(resolve(None, env, "RC_POLL_INTERVAL", "5"))
    default_format = resolve(None, env, "RC_OUTPUT_FORMAT", "png")
    out_dir = Path(resolve(args.out_dir, env, "RC_OUT_DIR", str(DEFAULT_OUT_DIR))).expanduser()

    # 档案选择：--profile > RC_DEFAULT_PROFILE > .env 中第一个档案
    profiles = load_profiles(env)
    default_query = args.profile or resolve(None, env, "RC_DEFAULT_PROFILE", None)
    if default_query:
        selected_slug = find_profile(profiles, default_query)
        if not selected_slug:
            raise ApiError(
                f"找不到档案：{default_query}。可用档案：{profile_choices(profiles)}"
            )
    else:
        selected_slug = next(iter(profiles))
    selected_profile = profiles[selected_slug]

    if args.list_profiles:
        print_profiles(profiles, env, selected_slug)
        return 0

    base_url, api_key, model = resolve_profile(selected_profile, args, env)
    protocol = detect_protocol(model, selected_profile["aliases"])

    if selected_profile["models"]:
        available = {item.lower() for item in selected_profile["models"]}
        if model.lower() not in available:
            log(
                f"[warn] 模型 {model} 不在档案 {selected_slug} 的 MODELS 列表中："
                + ", ".join(selected_profile["models"])
            )

    # 尺寸 / 比例 / 质量
    size = resolve(args.size, env, "RC_SIZE", None)
    ratio = resolve(args.ratio, env, "RC_ASPECT_RATIO", None)
    image_size = validate_image_size(resolve(args.image_size, env, "RC_IMAGE_SIZE", None))
    quality = resolve(args.quality, env, "RC_QUALITY", None)
    output_format = resolve(args.format, env, "RC_OUTPUT_FORMAT", default_format)
    used_profile = selected_profile

    if not args.task_id:
        if not api_key and not args.dry_run and not args.fallback:
            raise ApiError(
                f"档案 {selected_slug} 未配置 KEY。请在 .env 里填写 RC_PROFILE_{selected_slug}_KEY"
                " 或全局 RC_API_KEY"
            )
        prompt = " ".join(args.prompt).strip()
        if not prompt and DEFAULT_PROMPT_FILE.is_file():
            lines = [
                line.strip()
                for line in DEFAULT_PROMPT_FILE.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            prompt = " ".join(lines).strip()
        if not prompt:
            raise ApiError("未提供提示词。请传入提示词，或填写 prompts/prompt-image.md")

        local_images = [Path(item).expanduser() for item in args.image]
        missing = [str(path) for path in local_images if not path.is_file()]
        if missing:
            raise ApiError(f"参考图不存在：{', '.join(missing)}")

        if protocol == "gemini":
            if size:
                mapped = {value: key for key, value in RATIO_TO_SIZE.items()}.get(size.lower())
                if mapped:
                    ratio = ratio or mapped
                    log(f"[warn] Gemini 使用 --ratio；已将 size={size} 映射为 {mapped}")
                else:
                    log(f"[warn] Gemini 忽略 --size={size}，请改用 --ratio / --image-size")
                size = None
            if ratio and not re.fullmatch(r"\d+:\d+", ratio):
                raise ApiError(f"ratio={ratio} 格式错误；应形如 16:9、3:4")
            if quality and not args.no_quality:
                log("[warn] Gemini 通过 imageSize 控制质量，忽略 quality")
                quality = None
            if args.n > 1:
                log("[warn] Gemini 协议固定返回单张结果，忽略 --n")
        else:
            if image_size:
                log(f"[warn] OpenAI 协议忽略 --image-size={image_size}，请用 --size")
                image_size = None
            if output_format not in ("png", "jpeg", "webp"):
                raise ApiError(f"format={output_format} 不合法；可选 png / jpeg / webp")
            if ratio:
                if not size:
                    if ratio not in RATIO_TO_SIZE:
                        raise ApiError(
                            f"OpenAI 不支持 ratio={ratio}；请改用 --size，可选比例：{', '.join(RATIO_TO_SIZE)}"
                        )
                    size = RATIO_TO_SIZE[ratio]
                    log(f"[info] ratio={ratio} 映射为 size={size}")
                else:
                    log(f"[warn] 已指定 --size，忽略 --ratio={ratio}")
            validate_size(size)
            validate_quality(model, quality)
            if args.n < 1:
                raise ApiError("--n 必须 >= 1")

        protocol, endpoint, payload, mode = build_payload(
            args, model, prompt, local_images, args.image_url, image_size, protocol
        )
        if quality and not args.no_quality and protocol == "openai":
            payload["quality"] = quality
        if protocol == "openai" and size:
            payload["size"] = size
        if protocol == "openai" and output_format:
            payload["output_format"] = output_format

        if args.verbose or args.dry_run:
            log(f"[request] {mode} · POST {base_url}{endpoint}")
            log(json.dumps(redact_payload(payload), ensure_ascii=False, indent=2))
        if args.dry_run:
            print("---RESULT---")
            print("ok=true")
            print("dry_run=true")
            print(f"protocol={protocol}")
            print(f"mode={mode}")
            print(f"model={model}")
            print(f"profile={selected_slug}")
            print(f"endpoint={endpoint}")
            print("---END---")
            return 0

        candidates = [selected_profile]
        if args.fallback:
            candidates += [
                profile for slug, profile in profiles.items() if slug != selected_slug
            ]
        log(
            f"[submit] {mode} · {model} · profile={selected_slug}"
            + (f" · fallback={len(candidates) - 1}" if args.fallback else "")
        )

        submit_timeout = int(resolve(None, env, "RC_SUBMIT_TIMEOUT", "180"))
        task_id = None
        immediate = None
        last_error = None
        used_profile = None

        for index, candidate in enumerate(candidates):
            candidate_base, candidate_key, _ = resolve_profile(candidate, args, env)
            if not candidate_key:
                if args.fallback and index + 1 < len(candidates):
                    log(f"[warn] 档案 {candidate['slug']} 缺少 KEY，跳过")
                    continue
                raise ApiError(
                    f"档案 {candidate['slug']} 未配置 KEY。请在 .env 里填写 "
                    f"RC_PROFILE_{candidate['slug']}_KEY 或全局 RC_API_KEY"
                )
            try:
                task_id, immediate = submit_task(
                    candidate_base,
                    endpoint,
                    payload,
                    candidate_key,
                    args.no_proxy,
                    submit_timeout,
                )
                used_profile = candidate
                base_url = candidate_base
                api_key = candidate_key
                if index > 0:
                    log(f"[fallback] 已切换到档案 {candidate['slug']}")
                break
            except ApiError as error:
                last_error = error
                more = index + 1 < len(candidates)
                if not args.fallback or not more or not is_fallback_error(error):
                    raise
                log(
                    f"[warn] 档案 {candidate['slug']} 提交失败（{error}），"
                    f"切换到 {candidates[index + 1]['slug']}"
                )

        if used_profile is None:
            if last_error:
                raise last_error
            raise ApiError("没有可用档案（候选档案均缺少 KEY）")

        if task_id is None:
            result = immediate
            if not is_complete(result):
                raise ApiError(f"提交未返回 task_id：{json.dumps(result, ensure_ascii=False)[:500]}")
        else:
            log(f"[submit] task_id={task_id}")
            result = poll_task(
                base_url, task_id, api_key, poll_interval, timeout, args.no_proxy
            )
    else:
        task_id = args.task_id
        protocol = detect_protocol(model, selected_profile["aliases"])
        endpoint = f"/v1/tasks/{task_id}"
        mode = "resume"
        if not api_key:
            raise ApiError(f"档案 {selected_slug} 未配置 KEY，无法续查任务")
        log(f"[resume] task_id={task_id} · profile={selected_slug}")
        result = poll_task(
            base_url, task_id, api_key, poll_interval, timeout, args.no_proxy
        )

    # 仅续查时按响应形状校正协议；正常提交以实际使用的协议为准
    if mode == "resume":
        if "candidates" in result:
            protocol = "gemini"
        elif "data" in result:
            protocol = "openai"

    urls = extract_urls(result, protocol)
    if not urls:
        raise ApiError(
            f"任务完成但没有解析到图片 URL：{json.dumps(result, ensure_ascii=False)[:800]}"
        )

    downloaded = []
    if not args.no_download:
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        for index, url in enumerate(urls, start=1):
            data, content_type = download_bytes(url, args.no_proxy)
            ext = pick_extension(url, content_type, output_format)
            stem = f"rc-{stamp}" if len(urls) == 1 else f"rc-{stamp}-{index}"
            path = unique_path(out_dir, stem, ext)
            path.write_bytes(data)
            downloaded.append((url, path, len(data)))
            log(f"[download] {path}（{human_size(len(data))}）")

    if args.open and not args.no_open:
        open_files([item[1] for item in downloaded])

    elapsed = time.time() - started_at
    print("---RESULT---")
    print("ok=true")
    print(f"protocol={protocol}")
    print(f"mode={mode}")
    print(f"model={model}")
    print(f"profile={used_profile['slug']}")
    print(f"profile_name={used_profile['name']}")
    print(
        "fallback_used="
        + ("true" if used_profile["slug"] != selected_slug else "false")
    )
    print(f"endpoint={endpoint}")
    if task_id:
        print(f"task_id={task_id}")
    print(f"elapsed_seconds={int(elapsed)}")
    print(f"elapsed_text={elapsed_text(elapsed)}")
    print(f"count={len(urls)}")
    for index, url in enumerate(urls, start=1):
        print(f"url_{index}={url}")
    for index, (url, path, size_bytes) in enumerate(downloaded, start=1):
        try:
            relative = path.relative_to(Path.cwd())
            relative_text = str(relative)
        except ValueError:
            relative_text = str(path)
        print(f"path_{index}={path}")
        print(f"path_rel_{index}={relative_text}")
        print(f"bytes_{index}={size_bytes}")
        print(f"human_size_{index}={human_size(size_bytes)}")
    if len(downloaded) == 1:
        print(f"path={downloaded[0][1]}")
        print(f"bytes={downloaded[0][2]}")
    print("---END---")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ApiError as error:
        print(f"错误：{error}", file=sys.stderr)
        if error.resumable and error.task_id:
            print(f"可用 --task-id {error.task_id} 续查任务", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("已中断。若任务已提交，可保留 task_id 稍后续查。", file=sys.stderr)
        sys.exit(130)
