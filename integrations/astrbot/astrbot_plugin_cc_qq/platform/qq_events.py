"""将 AstrBot QQ 事件变成平台无关输入（QQ Event Adapter）。"""

from __future__ import annotations

from typing import Optional

from ..constants import QQ_PLATFORM_NAME
from ..contracts import ConversationKey, ConversationKind, IncomingMessage


SUPPORTED_TEXT_SEGMENTS = frozenset(("Plain", "At"))


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
    has_unsupported_segments = any(
        type(segment).__name__ not in SUPPORTED_TEXT_SEGMENTS for segment in segments
    )

    return IncomingMessage(
        conversation=ConversationKey(platform_id, kind, conversation_id),
        sender_id=sender_id,
        sender_name=str(event.get_sender_name() or sender_id),
        message_id=str(message_id or ""),
        text=str(event.get_message_str() or "").strip(),
        origin=str(getattr(event, "unified_msg_origin", "") or ""),
        has_unsupported_segments=has_unsupported_segments,
    )
