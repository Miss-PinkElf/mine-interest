"""平台无关消息与代理事件契约（Message and Agent Contracts）。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConversationKind(str, Enum):
    GROUP = "group"
    PRIVATE = "private"


class AgentEventKind(str, Enum):
    STARTED = "started"
    TEXT = "text"
    TOOL = "tool"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ConversationKey:
    platform_id: str
    kind: ConversationKind
    conversation_id: str

    def storage_key(self) -> str:
        """JSON 数组编码保留边界，避免平台 ID 或群号与分隔符冲突。"""
        return json.dumps(
            [self.platform_id, self.kind.value, self.conversation_id],
            ensure_ascii=False,
            separators=(",", ":"),
        )


@dataclass(frozen=True)
class IncomingMessage:
    conversation: ConversationKey
    sender_id: str
    sender_name: str
    message_id: str
    text: str
    origin: str
    has_unsupported_segments: bool = False


@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    role: str
    reason: str = ""
    settings: Optional[SessionSettings] = None


@dataclass(frozen=True)
class SessionSettings:
    work_dir: str
    agent_type: str
    model: str = ""


@dataclass(frozen=True)
class AgentEvent:
    kind: AgentEventKind
    content: str = ""
    agent_session_id: Optional[str] = None


@dataclass(frozen=True)
class AgentRequest:
    conversation: ConversationKey
    work_dir: str
    message: str
    model: str = ""
    agent_session_id: Optional[str] = None


@dataclass(frozen=True)
class SessionRecord:
    id: int
    conversation: ConversationKey
    agent_type: str
    work_dir: str
    status: str
    agent_session_id: Optional[str] = None
