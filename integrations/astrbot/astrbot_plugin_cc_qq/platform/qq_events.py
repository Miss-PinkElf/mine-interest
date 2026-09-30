"""将 AstrBot QQ 事件变成平台无关输入（QQ Event Adapter）。"""

from __future__ import annotations

from typing import Optional

from ..constants import (
    DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS,
    EMPTY_MESSAGE_REPLY,
    ONEBOT_MILLISECOND_TIMESTAMP_THRESHOLD,
    QQ_PLATFORM_NAME,
    STALE_MESSAGE_MAX_AGE_SECONDS_KEY,
)
from ..contracts import ConversationKey, ConversationKind, IncomingMessage


SUPPORTED_TEXT_SEGMENTS = frozenset(("Plain", "At"))


def onebot_event_time(event) -> int | None:
    """只读 OneBot 原始 time。AstrBot 的 message_obj.timestamp 是收到时刻，不能用来判断过期。"""
    message_obj = getattr(event, "message_obj", None)
    raw = getattr(message_obj, "raw_message", None)
    if not isinstance(raw, dict):
        return None
    value = raw.get("time")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    return int(value)


def stale_max_age_from_config(config: dict) -> int:
    raw = config.get(STALE_MESSAGE_MAX_AGE_SECONDS_KEY, DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        return DEFAULT_STALE_MESSAGE_MAX_AGE_SECONDS
    return raw


def should_ignore_as_stale(event_time: int | None, now: int, max_age_seconds: int) -> bool:
    if max_age_seconds == 0 or event_time is None:
        return False
    if event_time > ONEBOT_MILLISECOND_TIMESTAMP_THRESHOLD:
        event_time //= 1000
    age = now - event_time
    if age < 0:
        return False
    return age > max_age_seconds


def empty_text_reply(kind: ConversationKind) -> str | None:
    if kind is ConversationKind.PRIVATE:
        return None
    return EMPTY_MESSAGE_REPLY


def _segment_text(segments: list, self_id: str) -> str:
    """只移除当前机器人的 @，保留其他提及与普通文本。"""
    parts = []
    for segment in segments:
        segment_type = type(segment).__name__
        if segment_type == "Plain":
            parts.append(str(getattr(segment, "text", "") or ""))
        elif segment_type == "At":
            target = str(getattr(segment, "qq", "") or "").strip()
            if target and target != self_id:
                label = str(getattr(segment, "name", "") or target).strip()
                parts.append(f"@{label} ")
    return "".join(parts).strip()


def _mentions_bot(segments: list, self_id: str) -> bool:
    if not self_id:
        return False
    return any(
        type(segment).__name__ == "At"
        and str(getattr(segment, "qq", "") or "").strip() == self_id
        for segment in segments
    )


def parse_qq_event(event) -> Optional[IncomingMessage]:
    """仅接收 QQ OneBot 消息；缺少稳定身份的事件不进入代理。"""
    if event.get_platform_name() != QQ_PLATFORM_NAME:
        return None

    platform_id = str(event.get_platform_id() or "").strip()
    sender_id = str(event.get_sender_id() or "").strip()
    if not platform_id or not sender_id:
        return None

    is_private = bool(event.is_private_chat())
    kind = ConversationKind.PRIVATE if is_private else ConversationKind.GROUP
    conversation_id = sender_id if is_private else str(event.get_group_id() or "").strip()
    if not conversation_id:
        return None

    message_obj = getattr(event, "message_obj", None)
    message_id = getattr(event, "message_id", None) or getattr(message_obj, "message_id", None)
    segments = event.get_messages() or []
    self_id = str(getattr(message_obj, "self_id", "") or "").strip()
    if self_id and sender_id == self_id:
        return None
    has_unsupported_segments = any(
        type(segment).__name__ not in SUPPORTED_TEXT_SEGMENTS for segment in segments
    )
    text = _segment_text(segments, self_id) if segments else str(event.get_message_str() or "").strip()

    return IncomingMessage(
        conversation=ConversationKey(platform_id, kind, conversation_id),
        sender_id=sender_id,
        sender_name=str(event.get_sender_name() or sender_id),
        message_id=str(message_id or ""),
        text=text,
        origin=str(getattr(event, "unified_msg_origin", "") or ""),
        has_unsupported_segments=has_unsupported_segments,
        mentions_bot=not is_private and _mentions_bot(segments, self_id),
        event_time=onebot_event_time(event),
    )
