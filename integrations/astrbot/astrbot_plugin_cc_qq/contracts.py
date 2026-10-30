"""平台无关消息与代理事件契约（Message and Agent Contracts）。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .permissions import PROFILE_WORKSPACE, ROLE_MEMBER


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
    mentions_bot: bool = False
    event_time: int | None = None
    # 需求 5：媒体输入先在解析层收集原始引用，落盘后替换为本地路径。
    image_refs: tuple[str, ...] = ()
    quoted_text: str = ""
    quoted_image_refs: tuple[str, ...] = ()
    forward_ids: tuple[str, ...] = ()
    images: tuple[str, ...] = ()
    quoted_images: tuple[str, ...] = ()
    forward_text: str = ""
    forward_images: tuple[str, ...] = ()

    @property
    def has_media(self) -> bool:
        return bool(
            self.image_refs
            or self.images
            or self.quoted_text
            or self.quoted_image_refs
            or self.quoted_images
            or self.forward_ids
            or self.forward_text
            or self.forward_images
        )


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
    role: str = ROLE_MEMBER
    permission_profile: str = PROFILE_WORKSPACE
    sender_id: str = ""
    origin: str = ""


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
    permission_profile: str = PROFILE_WORKSPACE
    sender_id: str = ""
    origin: str = ""
    claude_settings_path: str = ""
    claude_setting_sources: str = ""
    process_env: dict = field(default_factory=dict)
    images: tuple[str, ...] = ()


@dataclass(frozen=True)
class SessionRecord:
    id: int
    conversation: ConversationKey
    agent_type: str
    work_dir: str
    status: str
    agent_session_id: Optional[str] = None
