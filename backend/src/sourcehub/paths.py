"""资料目录投影（Storage Path Projection）：可读路径不改变逻辑 Item 身份。"""

from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from .envelope import Envelope
from .constants import DEFAULT_SESSION_END, DEFAULT_SESSION_START, NODE_FILE, NODE_IMAGE

SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")
PATH_UNSAFE_PATTERN = re.compile(r'[\\/:*?"<>|\s]+')
PATH_SEPARATOR = "-"
DEFAULT_TITLE = "未命名"
MAX_TITLE_LENGTH = 80
UNKNOWN_CAPTURE_DAY = "unknown"
QQ_PATH_KIND = {"daily": "message", "message": "message", "forward": "forward", "session": "session"}
QQ_DEFAULT_TITLE = {"message": "消息", "forward": "转发", "session": "会话"}
QQ_MARKERS = {DEFAULT_SESSION_START, DEFAULT_SESSION_END}
QQ_IMAGE_TITLE = "图片"


def item_storage_path(envelope: Envelope) -> str:
    """返回相对 items/ 的可读存储路径；最后一段始终含稳定 ID。"""
    platform, kind, identity = envelope.item_id.split(":", 2)
    day = capture_day(envelope.received_at)
    if platform == "qq":
        path_kind = QQ_PATH_KIND.get(kind, kind)
        stable_id = PATH_UNSAFE_PATTERN.sub(PATH_SEPARATOR, identity).strip(PATH_SEPARATOR)
        title = safe_title(_qq_title(envelope, path_kind))
        return f"qq/{day}/{path_kind}/{title}{PATH_SEPARATOR}{stable_id}"
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


def _qq_title(envelope: Envelope, path_kind: str) -> str:
    if envelope.extra.get("title"):
        return str(envelope.extra["title"])

    def readable(nodes):
        for node in nodes:
            first_line = (node.text or "").strip().splitlines()
            if first_line and first_line[0].strip() not in QQ_MARKERS:
                yield first_line[0].strip()
            yield from readable(node.children)

    title = next(readable(envelope.content), "")
    if title:
        return title
    for node in envelope.content:
        if node.type == NODE_FILE and node.extra.get("name"):
            return str(node.extra["name"])
        if node.type == NODE_IMAGE:
            return QQ_IMAGE_TITLE
    return QQ_DEFAULT_TITLE.get(path_kind, DEFAULT_TITLE)
