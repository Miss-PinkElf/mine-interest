"""QQ 媒体引用展开、落盘与受信路径校验（Media Materialization）。

本模块顶层只依赖标准库与 PIL，AstrBot 相关导入全部延迟到函数内部，
这样单元测试可以在未安装 AstrBot 的 Python 环境里运行。
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import re
import shutil
import time
from dataclasses import dataclass, replace
from pathlib import Path

from PIL import Image as PILImage

from .constants import (
    DEFAULT_MAX_INCOMING_IMAGES,
    IMAGE_MARKER_MAX_COUNT,
    IMAGE_MARKER_PATTERN,
    IMAGE_ONLY_PROMPT,
    MAX_FORWARD_CHARS,
    MAX_IMAGE_BYTES,
    MEDIA_EXTENSION_BY_FORMAT,
)
from .contracts import IncomingMessage

IMAGE_MARKER = re.compile(IMAGE_MARKER_PATTERN)


@dataclass(frozen=True)
class MaterializeResult:
    """媒体处理结果：图片已替换为本地路径，失败与截断数量供上层提示。"""

    message: IncomingMessage
    failed: int = 0
    truncated: int = 0


def conversation_media_dir(media_root: Path, conversation_key: str, message_id: str) -> Path:
    """按会话与消息隔离媒体目录，避免不同会话或消息互相覆盖。"""
    digest = hashlib.sha1(conversation_key.encode("utf-8")).hexdigest()[:12]
    date_part = time.strftime("%Y%m%d")
    safe_message_id = "".join(
        char for char in message_id if char.isalnum() or char in ("-", "_")
    ) or "unknown"
    return Path(media_root) / digest / date_part / safe_message_id


def resolve_trusted_path(raw: str, work_dir: str, media_root: Path | str) -> str | None:
    """图片路径必须位于工作目录或插件媒体目录内；返回绝对路径供发送。"""
    if not raw:
        return None
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        if not work_dir:
            return None
        candidate = Path(work_dir) / candidate
    target = Path(os.path.realpath(candidate))
    for root in (work_dir, media_root):
        if not root:
            continue
        real_root = Path(os.path.realpath(Path(root).expanduser()))
        if target == real_root or real_root in target.parents:
            return str(target)
    return None


def is_trusted_path(raw: str, work_dir: str, media_root: Path | str) -> bool:
    """图片发送与读取只信任工作目录或插件媒体目录内的真实路径。"""
    return resolve_trusted_path(raw, work_dir, media_root) is not None


def validate_image(path: Path, max_bytes: int = MAX_IMAGE_BYTES) -> str | None:
    """校验文件是受支持的图片并返回目标扩展名；不通过返回 None。"""
    try:
        if not path.is_file() or path.stat().st_size > max_bytes:
            return None
        with PILImage.open(path) as image:
            image_format = (image.format or "").upper()
            image.verify()
    except (OSError, ValueError):
        return None
    return MEDIA_EXTENSION_BY_FORMAT.get(image_format)


def copy_verified_image(
    source: Path, target_dir: Path, index: int, max_bytes: int = MAX_IMAGE_BYTES
) -> str | None:
    """把校验通过的图片复制进媒体目录，返回本地绝对路径。"""
    extension = validate_image(source, max_bytes)
    if extension is None:
        return None
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{index:02d}{extension}"
    try:
        shutil.copyfile(source, target)
    except OSError:
        return None
    return str(target)


def cleanup_old_media(
    media_root: Path, retention_days: int, now: float | None = None
) -> int:
    """删除超过保留期的媒体目录，返回删除的目录数量。"""
    root = Path(media_root)
    if not root.is_dir() or retention_days <= 0:
        return 0
    deadline = (now if now is not None else time.time()) - retention_days * 86400
    removed = 0
    for date_dir in root.glob("*/*"):
        try:
            if date_dir.is_dir() and date_dir.stat().st_mtime < deadline:
                shutil.rmtree(date_dir)
                removed += 1
        except OSError:
            continue
    return removed


async def _expand_forward_ids(event, forward_ids: tuple[str, ...]) -> tuple[str, list[str]]:
    """用 AstrBot 现成工具展开合并转发；失败时返回空内容而不是中断整条消息。"""
    if not forward_ids or event is None:
        return "", []
    try:
        from astrbot.core.utils.quoted_message.chain_parser import OneBotPayloadParser
        from astrbot.core.utils.quoted_message.onebot_client import OneBotClient

        client = OneBotClient(event)
        parser = OneBotPayloadParser()
    except Exception:
        return "", []

    texts: list[str] = []
    images: list[str] = []
    for forward_id in forward_ids:
        try:
            payload = await client.get_forward_msg(forward_id)
            if not payload:
                continue
            parsed = parser.parse_get_forward_payload(payload)
        except Exception:
            continue
        if parsed.get("text"):
            texts.append(str(parsed["text"]))
        images.extend(str(ref) for ref in (parsed.get("image_refs") or []) if ref)
    text = "\n".join(texts)[:MAX_FORWARD_CHARS]
    return text, images


async def _resolve_image_candidates(event, ref: str) -> list[str]:
    """用 OneBot get_image 把 NapCat 文件名换成本地路径。

    AstrBot 自带的 ImageResolver 优先返回 gchat URL，而该 URL 会很快过期，
    因此这里直接取 get_image 返回的本地 file 路径。
    """
    if event is None:
        return []
    try:
        from astrbot.core.utils.quoted_message.onebot_client import OneBotClient

        client = OneBotClient(event)
    except Exception:
        return []
    candidates: list[str] = []
    for params in ({"file": ref}, {"file_id": ref}):
        try:
            data = await client.call("get_image", params)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for key in ("file", "url"):
            value = data.get(key)
            if isinstance(value, str) and value:
                candidates.append(value)
        if candidates:
            break
    return candidates


async def _store_image(
    ref: str, target_dir: Path, index: int, event=None
) -> str | None:
    """先按原引用落盘，失败后再用 get_image 换成本地路径重试。"""
    candidates = [ref]
    candidates.extend(await _resolve_image_candidates(event, ref))
    for candidate in dict.fromkeys(candidates):
        try:
            from astrbot.core.message.components import Image as QQImage

            source = await QQImage(file=candidate).convert_to_file_path()
        except Exception:
            continue
        stored = await asyncio.to_thread(copy_verified_image, Path(source), target_dir, index)
        if stored:
            return stored
    return None


async def materialize(
    event,
    message: IncomingMessage,
    media_root: Path,
    *,
    enabled: bool = True,
    max_images: int = DEFAULT_MAX_INCOMING_IMAGES,
) -> MaterializeResult:
    """展开转发、下载图片并替换为本地路径；媒体关闭时保留原文。"""
    if not enabled:
        return MaterializeResult(message)

    forward_text, forward_refs = await _expand_forward_ids(event, message.forward_ids)

    direct_refs = list(message.image_refs)
    quoted_refs = list(message.quoted_image_refs)
    forward_refs = list(forward_refs)

    target_dir = conversation_media_dir(
        media_root,
        message.conversation.storage_key(),
        message.message_id,
    )
    groups: dict[str, list[str]] = {"direct": [], "quoted": [], "forward": []}
    failed = 0
    truncated = 0
    accepted = 0
    slot = 0
    for group, refs in (
        ("direct", direct_refs),
        ("quoted", quoted_refs),
        ("forward", forward_refs),
    ):
        for ref in refs:
            if accepted >= max_images:
                truncated += 1
                continue
            slot += 1
            path = await _store_image(ref, target_dir, slot, event)
            if path is None:
                failed += 1
                continue
            groups[group].append(path)
            accepted += 1

    return MaterializeResult(
        message=replace(
            message,
            images=tuple(groups["direct"]),
            quoted_images=tuple(groups["quoted"]),
            forward_text=forward_text,
            forward_images=tuple(groups["forward"]),
        ),
        failed=failed,
        truncated=truncated,
    )


def agent_images(message: IncomingMessage) -> tuple[str, ...]:
    """汇总本轮要交给代理的全部本地图片路径。"""
    return tuple(
        (*message.images, *message.quoted_images, *message.forward_images)
    )


def _image_lines(paths: tuple[str, ...]) -> str:
    return "\n".join(f"- {path}" for path in paths)


def build_agent_prompt(message: IncomingMessage) -> str:
    """把正文、图片路径、引用与转发内容组装成一次代理输入。"""
    sections: list[str] = []
    text = message.text.strip()
    if text:
        sections.append(text)
    elif message.images or message.quoted_images or message.forward_images:
        sections.append(IMAGE_ONLY_PROMPT)

    if message.images:
        sections.append(f"[用户发送的图片]\n{_image_lines(message.images)}")

    if message.quoted_text or message.quoted_images:
        quoted_parts: list[str] = []
        if message.quoted_text:
            quoted_parts.append(message.quoted_text)
        if message.quoted_images:
            quoted_parts.append(
                f"[被引用消息中的图片]\n{_image_lines(message.quoted_images)}"
            )
        sections.append("[被引用的消息]\n" + "\n".join(quoted_parts))

    if message.forward_text or message.forward_images:
        forward_parts: list[str] = []
        if message.forward_text:
            forward_parts.append(message.forward_text)
        if message.forward_images:
            forward_parts.append(
                f"[转发消息中的图片]\n{_image_lines(message.forward_images)}"
            )
        sections.append("[转发的消息]\n" + "\n".join(forward_parts))

    if agent_images(message):
        sections.append("如需查看图片，请使用 Read 工具读取上面的本地路径。")

    return "\n\n".join(section for section in sections if section).strip()


def parse_reply_parts(
    content: str, work_dir: str = "", media_root: Path | str | None = None
) -> tuple[list[tuple[str, str]], int]:
    """把代理回复拆成文本段与图片段；不可信路径被剔除并计数。"""
    parts: list[tuple[str, str]] = []
    ignored = 0
    image_count = 0
    last = 0
    for match in IMAGE_MARKER.finditer(content):
        text = content[last:match.start()]
        if text:
            parts.append(("text", text))
        path = match.group(1).strip()
        resolved = (
            resolve_trusted_path(path, work_dir, media_root)
            if path and image_count < IMAGE_MARKER_MAX_COUNT
            else None
        )
        if resolved:
            parts.append(("image", resolved))
            image_count += 1
        else:
            ignored += 1
        last = match.end()
    tail = content[last:]
    if tail:
        parts.append(("text", tail))
    return parts, ignored
