"""QQ 成条引擎（Grouping Engine）：单条、转发块、会话标记。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .constants import (
    GAP_SESSION_END_MISSING,
    GROUPING_MERGED_FORWARD,
    GROUPING_DAILY,
    GROUPING_SESSION_MARKERS,
    GROUPING_SINGLE,
    NODE_FORWARD,
    NODE_TEXT,
    PLATFORM_QQ,
    SCHEMA_VERSION,
)
from .envelope import ContentNode, Envelope
from .rules import RulePack


@dataclass
class IncomingMessage:
    platform: str
    conversation_id: str
    event_id: str
    sender_id: str
    source_time: str | None
    received_at: str
    text: str
    nodes: list[ContentNode]
    is_forward: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


def text_node(text: str) -> ContentNode:
    return ContentNode(type=NODE_TEXT, text=text)


def _message_to_dict(message: IncomingMessage) -> dict[str, Any]:
    return {
        "platform": message.platform,
        "conversation_id": message.conversation_id,
        "event_id": message.event_id,
        "sender_id": message.sender_id,
        "source_time": message.source_time,
        "received_at": message.received_at,
        "text": message.text,
        "nodes": [node.to_dict() for node in message.nodes],
        "is_forward": message.is_forward,
        "raw": message.raw,
    }


def _message_from_dict(data: dict[str, Any]) -> IncomingMessage:
    from .envelope import node_from_dict

    return IncomingMessage(
        platform=str(data.get("platform") or PLATFORM_QQ),
        conversation_id=str(data.get("conversation_id") or ""),
        event_id=str(data.get("event_id") or ""),
        sender_id=str(data.get("sender_id") or ""),
        source_time=data.get("source_time"),
        received_at=str(data.get("received_at") or ""),
        text=str(data.get("text") or ""),
        nodes=[node_from_dict(item) for item in data.get("nodes") or []],
        is_forward=bool(data.get("is_forward")),
        raw=dict(data.get("raw") or {}),
    )


_MARKER_TRANSLATE = str.maketrans({
    "，": ",",
    "。": ".",
    "．": ".",
})


def marker_key(text: str) -> str:
    """去掉空白，并把中英文逗号/句号收成同一种，便于整句匹配。"""
    return "".join(text.split()).translate(_MARKER_TRANSLATE)


def _is_marker(text: str, marker: str) -> bool:
    return bool(marker) and marker_key(text) == marker_key(marker)


@dataclass
class _OpenSession:
    start_event_id: str
    sender_id: str
    source_time: str | None
    received_at: str
    members: list[IncomingMessage] = field(default_factory=list)
    last_activity: datetime | None = None


class GroupingEngine:
    def __init__(self, pack: RulePack):
        self.pack = pack
        self._sessions: dict[str, _OpenSession] = {}

    def open_session_ids(self) -> list[str]:
        return list(self._sessions.keys())

    def dump_sessions(self) -> dict[str, Any]:
        payload = {}
        for conversation, session in self._sessions.items():
            payload[conversation] = {
                "start_event_id": session.start_event_id,
                "sender_id": session.sender_id,
                "source_time": session.source_time,
                "received_at": session.received_at,
                "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                "members": [_message_to_dict(member) for member in session.members],
            }
        return payload

    def load_sessions(self, payload: dict[str, Any]) -> None:
        self._sessions = {}
        for conversation, raw in (payload or {}).items():
            last = raw.get("last_activity")
            self._sessions[conversation] = _OpenSession(
                start_event_id=str(raw.get("start_event_id") or ""),
                sender_id=str(raw.get("sender_id") or ""),
                source_time=raw.get("source_time"),
                received_at=str(raw.get("received_at") or ""),
                members=[_message_from_dict(item) for item in raw.get("members") or []],
                last_activity=datetime.fromisoformat(last) if last else None,
            )

    def ingest(self, message: IncomingMessage, now: datetime) -> list[Envelope]:
        closed = self.flush_idle(now)
        conversation = message.conversation_id
        if conversation in self._sessions:
            closed.extend(self._handle_open(conversation, message, now))
            return closed
        if _is_marker(message.text, self.pack.session_start):
            self._sessions[conversation] = _OpenSession(
                start_event_id=message.event_id,
                sender_id=message.sender_id,
                source_time=message.source_time,
                received_at=message.received_at,
                last_activity=now,
            )
            return closed
        if _is_marker(message.text, self.pack.session_end):
            return closed
        closed.append(self._single_or_forward(message))
        return closed

    def flush_idle(self, now: datetime) -> list[Envelope]:
        timeout = timedelta(seconds=self.pack.session_idle_seconds)
        done: list[Envelope] = []
        expired = []
        for conversation, session in self._sessions.items():
            if session.last_activity is None:
                continue
            if now - session.last_activity >= timeout:
                done.append(self._close(conversation, missing_end=True))
                expired.append(conversation)
        for conversation in expired:
            self._sessions.pop(conversation, None)
        return done

    def _handle_open(
        self, conversation: str, message: IncomingMessage, now: datetime
    ) -> list[Envelope]:
        if _is_marker(message.text, self.pack.session_start):
            previous = self._close(conversation, missing_end=True)
            self._sessions[conversation] = _OpenSession(
                start_event_id=message.event_id,
                sender_id=message.sender_id,
                source_time=message.source_time,
                received_at=message.received_at,
                last_activity=now,
            )
            return [previous]
        session = self._sessions[conversation]
        if _is_marker(message.text, self.pack.session_end):
            envelope = self._close(conversation, missing_end=False)
            self._sessions.pop(conversation, None)
            return [envelope]
        session.members.append(message)
        session.last_activity = now
        return []

    def _close(self, conversation: str, missing_end: bool) -> Envelope:
        session = self._sessions[conversation]
        content: list[ContentNode] = []
        member_ids: list[str] = []
        for member in session.members:
            member_ids.append(member.event_id)
            if member.is_forward:
                content.append(
                    ContentNode(
                        type=NODE_FORWARD,
                        text=member.text,
                        children=list(member.nodes),
                    )
                )
            else:
                content.extend(member.nodes)
        gaps = [GAP_SESSION_END_MISSING] if missing_end else []
        return Envelope(
            schema_version=SCHEMA_VERSION,
            platform=PLATFORM_QQ,
            conversation_id=conversation,
            item_id=f"qq:session:{session.start_event_id}",
            event_id=session.start_event_id,
            sender_id=session.sender_id,
            source_time=session.source_time,
            received_at=session.received_at,
            content=content,
            attachments=[],
            gaps=gaps,
            grouping={
                "type": GROUPING_SESSION_MARKERS,
                "member_event_ids": member_ids,
                "start_event_id": session.start_event_id,
            },
        )

    def _single_or_forward(self, message: IncomingMessage) -> Envelope:
        if message.is_forward:
            grouping_type = GROUPING_MERGED_FORWARD
            item_id = f"qq:forward:{message.event_id}"
            content = [
                ContentNode(type=NODE_FORWARD, text=message.text, children=list(message.nodes))
            ]
        else:
            grouping_type = GROUPING_SINGLE
            item_id = f"qq:message:{message.event_id}"
            content = list(message.nodes)
        return Envelope(
            schema_version=SCHEMA_VERSION,
            platform=message.platform or PLATFORM_QQ,
            conversation_id=message.conversation_id,
            item_id=item_id,
            event_id=message.event_id,
            sender_id=message.sender_id,
            source_time=message.source_time,
            received_at=message.received_at,
            content=content,
            attachments=[],
            gaps=[],
            grouping={"type": grouping_type, "member_event_ids": [message.event_id]},
        )


def daily_envelope(messages: list[IncomingMessage], day: str) -> Envelope | None:
    """把同群同日尚未整理的普通消息投影为一个确定性日条目。"""
    if not messages:
        return None
    first = messages[0]
    return Envelope(
        schema_version=SCHEMA_VERSION,
        platform=PLATFORM_QQ,
        conversation_id=first.conversation_id,
        item_id=f"qq:daily:{first.conversation_id}:{day}:{first.event_id}",
        event_id=first.event_id,
        sender_id=first.sender_id,
        source_time=first.source_time,
        received_at=first.received_at,
        content=[node for message in messages for node in message.nodes],
        attachments=[],
        gaps=[],
        grouping={"type": GROUPING_DAILY, "member_event_ids": [message.event_id for message in messages], "day": day},
    )
