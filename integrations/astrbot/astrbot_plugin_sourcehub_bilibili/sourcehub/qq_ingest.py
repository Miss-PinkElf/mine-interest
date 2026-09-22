"""把 OneBot / 检查插件消息变成 IncomingMessage。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .constants import (
    GAP_EVENT_ID_MISSING,
    NODE_FORWARD,
    NODE_FILE,
    NODE_IMAGE,
    NODE_TEXT,
    NODE_UNKNOWN,
    PLATFORM_QQ,
)
from .envelope import ContentNode
from .grouping import IncomingMessage


def parse_onebot_message(payload: dict[str, Any]) -> IncomingMessage:
    event_id = str(payload.get("message_id") or "")
    gaps = []
    if not event_id:
        gaps.append(GAP_EVENT_ID_MISSING)
    nodes: list[ContentNode] = []
    texts: list[str] = []
    is_forward = False
    for segment in payload.get("message") or []:
        if not isinstance(segment, dict):
            continue
        node, text, forward = _parse_segment(segment)
        if node is None:
            continue
        nodes.append(node)
        if text:
            texts.append(text)
        if forward:
            is_forward = True
    received = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_time = None
    if payload.get("time"):
        source_time = datetime.fromtimestamp(int(payload["time"]), tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    raw = dict(payload)
    if gaps:
        raw["gaps"] = gaps
    return IncomingMessage(
        platform=PLATFORM_QQ,
        conversation_id=str(payload.get("group_id") or payload.get("conversation_id") or ""),
        event_id=event_id,
        sender_id=str(payload.get("user_id") or payload.get("sender_id") or ""),
        source_time=source_time,
        received_at=received,
        text="".join(texts),
        nodes=nodes,
        is_forward=is_forward,
        raw=raw,
    )


def _parse_segment(segment: dict[str, Any]):
    kind = segment.get("type")
    data = segment.get("data") or {}
    if kind == "text":
        text = str(data.get("text") or "")
        return ContentNode(type=NODE_TEXT, text=text), text, False
    if kind == "image":
        url = str(data.get("url") or data.get("file") or "")
        return ContentNode(type=NODE_IMAGE, url=url), "", False
    if kind == "file":
        url = str(data.get("url") or data.get("file_url") or data.get("file") or "")
        return ContentNode(type=NODE_FILE, url=url, extra={"name": data.get("name") or ""}), "", False
    if kind == "forward":
        children = []
        for inner in data.get("content") or []:
            if not isinstance(inner, dict):
                continue
            for inner_segment in inner.get("message") or []:
                if not isinstance(inner_segment, dict):
                    continue
                child, _, _ = _parse_segment(inner_segment)
                if child is not None:
                    children.append(child)
        return ContentNode(type=NODE_FORWARD, extra={"id": data.get("id")}, children=children), "", True
    return ContentNode(type=NODE_UNKNOWN, extra=segment), "", False
