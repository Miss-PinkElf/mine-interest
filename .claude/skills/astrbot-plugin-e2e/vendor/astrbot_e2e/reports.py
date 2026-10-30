"""运行目录、JSON 报告与失败证据（Report）。"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", str(name)).strip("-")
    return slug or "case"


def create_run_dir(base: Any, case_name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    path = Path(base) / "{}-{}".format(stamp, slugify(case_name))
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path: Any, data: Any) -> None:
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def write_summary(
    run_dir: Any,
    case_name: str,
    status: str,
    results: List[Any],
    duration_seconds: float,
    extra: Dict[str, Any] = None,
) -> Dict[str, Any]:
    summary = {
        "case": case_name,
        "status": status,
        "duration_seconds": round(float(duration_seconds), 3),
        "assertions": [
            {
                "kind": item.kind,
                "ok": item.ok,
                "expected": item.expected,
                "actual": item.actual,
                "detail": item.detail,
            }
            for item in results
        ],
    }
    if extra:
        summary.update(extra)
    write_json(Path(run_dir) / "summary.json", summary)
    return summary


SECRET_KEYS = frozenset({"password", "token", "api_key", "jwt_secret", "secret"})
SECRET_KEYWORDS = ("password", "token", "api_key", "secret", "jwt")
LONG_TEXT_LIMIT = 500


def _is_secret_key(key: Any) -> bool:
    lowered = str(key).lower()
    return lowered in SECRET_KEYS or any(word in lowered for word in SECRET_KEYWORDS)


def _qq_ids(cfg: Dict[str, Any] = None) -> List[str]:
    if not cfg:
        return []
    ids = []
    for section in ("bot", "sender"):
        value = (cfg.get(section) or {}).get("qq")
        if value:
            ids.append(str(value))
    return ids


def _secrets(cfg: Dict[str, Any] = None) -> List[str]:
    if not cfg:
        return []
    found = []
    for section in ("webui", "bot", "sender", "judge", "astrbot"):
        source = cfg.get(section) or {}
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if _is_secret_key(key) and value:
                found.append(str(value))
    return found


def _mask_qq(text: str, qq_ids: List[str]) -> str:
    for qq in qq_ids:
        if not qq or qq not in text:
            continue
        if len(qq) <= 4:
            masked = "***"
        else:
            masked = qq[:2] + "*" * (len(qq) - 4) + qq[-2:]
        text = text.replace(qq, masked)
    return text


def sanitize(value: Any, cfg: Dict[str, Any] = None, redact: bool = True) -> Any:
    if not redact:
        return value
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if _is_secret_key(key):
                result[key] = "***"
            else:
                result[key] = sanitize(item, cfg, redact)
        return result
    if isinstance(value, list):
        return [sanitize(item, cfg, redact) for item in value]
    if isinstance(value, str):
        text = value
        for secret in _secrets(cfg):
            text = text.replace(secret, "***")
        text = _mask_qq(text, _qq_ids(cfg))
        if len(text) > LONG_TEXT_LIMIT:
            text = text[:LONG_TEXT_LIMIT] + "...[truncated {} chars]".format(
                len(text) - LONG_TEXT_LIMIT
            )
        return text
    return value


def render_markdown(suite: Dict[str, Any]) -> str:
    cases = suite.get("cases") or []
    counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0}
    for item in cases:
        status = item.get("status", "ERROR")
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "# AstrBot 插件测试报告",
        "",
        "## 摘要（Summary）",
        "",
        "- 插件：{}".format(suite.get("plugin", "")),
        "- 状态：{}".format(suite.get("status", "")),
        "- 开始时间：{}".format(suite.get("started_at", "")),
        "- 用例：{} 个（通过 {} / 失败 {} / 跳过 {} / 错误 {}）".format(
            len(cases),
            counts.get("PASSED", 0),
            counts.get("FAILED", 0),
            counts.get("SKIPPED", 0),
            counts.get("ERROR", 0),
        ),
        "- 耗时：{} 秒".format(suite.get("duration_seconds", 0)),
        "",
        "## 用例结果（Cases）",
        "",
        "| # | 用例 | 状态 | 证据 |",
        "| --- | --- | --- | --- |",
    ]
    for index, item in enumerate(cases, start=1):
        lines.append(
            "| {} | {} | {} | `{}` |".format(
                index, item.get("case", ""), item.get("status", ""), item.get("run_dir", "")
            )
        )

    failed = [item for item in cases if item.get("status") in ("FAILED", "ERROR")]
    lines.extend(["", "## 失败摘要（Failures）", ""])
    if not failed:
        lines.append("无。")
    else:
        for item in failed:
            lines.append("### {}".format(item.get("case", "")))
            lines.append("")
            lines.append("- 状态：{}".format(item.get("status", "")))
            lines.append("- 证据：`{}`".format(item.get("run_dir", "")))
            for step in item.get("steps") or []:
                if step.get("status") == "PASSED":
                    continue
                for result in step.get("results") or []:
                    if result.get("ok"):
                        continue
                    lines.append(
                        "- 步骤 {} / {}：{}".format(
                            step.get("step"), result.get("kind"), result.get("detail", "")
                        )
                    )
            lines.append("")

    lines.extend(["", "## 操作记录（Ops）", ""])
    ops = suite.get("ops") or []
    if not ops:
        lines.append("无。")
    else:
        for item in ops:
            lines.append("- {}".format(item))
    lines.append("")
    return "\n".join(lines)


def write_suite_report(
    suite_dir: Any,
    suite: Dict[str, Any],
    cfg: Dict[str, Any],
    redact: bool = True,
) -> Dict[str, Any]:
    data = sanitize(suite, cfg, redact=redact)
    write_json(Path(suite_dir) / "report.json", data)
    (Path(suite_dir) / "report.md").write_text(
        render_markdown(data), encoding="utf-8"
    )
    return data
