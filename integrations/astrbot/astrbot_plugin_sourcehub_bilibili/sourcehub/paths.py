"""资料目录投影（Storage Path Projection）：可读路径不改变逻辑 Item 身份。"""

from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from .envelope import Envelope

SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")
PATH_UNSAFE_PATTERN = re.compile(r'[\\/:*?"<>|\s]+')
PATH_SEPARATOR = "-"
DEFAULT_TITLE = "未命名"
MAX_TITLE_LENGTH = 80
UNKNOWN_CAPTURE_DAY = "unknown"


def item_storage_path(envelope: Envelope) -> str:
    """返回相对 items/ 的可读存储路径；最后一段始终含稳定 ID。"""
    platform, kind, identity = envelope.item_id.split(":", 2)
    day = capture_day(envelope.received_at)
    if platform == "qq":
        return f"qq/{day}/items/{kind}{PATH_SEPARATOR}{identity}"
    title = _title(envelope)
    return f"bilibili/{day}/{kind}/{safe_title(title)}{PATH_SEPARATOR}{identity}"


def capture_day(received_at: str) -> str:
    if not received_at:
        return UNKNOWN_CAPTURE_DAY
    timestamp = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
    return timestamp.astimezone(SHANGHAI_TIMEZONE).date().isoformat()


def safe_title(title: str) -> str:
    cleaned = PATH_UNSAFE_PATTERN.sub(PATH_SEPARATOR, title).strip(PATH_SEPARATOR)
    return (cleaned[:MAX_TITLE_LENGTH].rstrip(PATH_SEPARATOR) or DEFAULT_TITLE)


def _title(envelope: Envelope) -> str:
    if envelope.extra.get("title"):
        return str(envelope.extra["title"])
    for node in envelope.content:
        title = (node.extra or {}).get("title")
        if title:
            return str(title)
    return DEFAULT_TITLE
