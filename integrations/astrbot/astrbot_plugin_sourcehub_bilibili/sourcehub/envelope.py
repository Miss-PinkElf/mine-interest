"""捕获封套（Capture Envelope）与路径编码。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .constants import SCHEMA_VERSION


@dataclass
class ContentNode:
    type: str
    text: str | None = None
    url: str | None = None
    sha256: str | None = None
    children: list[ContentNode] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def is_forward(self) -> bool:
        return self.type == "forward"

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "type": self.type,
            "text": self.text,
            "url": self.url,
            "sha256": self.sha256,
            "children": [child.to_dict() for child in self.children],
            "extra": self.extra,
        }
        return {key: value for key, value in payload.items() if value not in (None, [], {})}


@dataclass
class Envelope:
    schema_version: str
    platform: str
    conversation_id: str
    item_id: str
    event_id: str
    sender_id: str
    source_time: str | None
    received_at: str
    content: list[ContentNode]
    attachments: list[dict[str, Any]]
    gaps: list[str]
    grouping: dict[str, Any]
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["content"] = [node.to_dict() if isinstance(node, ContentNode) else node for node in self.content]
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Envelope:
        nodes = [node_from_dict(item) for item in data.get("content") or []]
        return cls(
            schema_version=str(data.get("schema_version") or SCHEMA_VERSION),
            platform=str(data.get("platform") or ""),
            conversation_id=str(data.get("conversation_id") or ""),
            item_id=str(data.get("item_id") or ""),
            event_id=str(data.get("event_id") or ""),
            sender_id=str(data.get("sender_id") or ""),
            source_time=data.get("source_time"),
            received_at=str(data.get("received_at") or ""),
            content=nodes,
            attachments=list(data.get("attachments") or []),
            gaps=list(data.get("gaps") or []),
            grouping=dict(data.get("grouping") or {}),
            extra=dict(data.get("extra") or {}),
        )


def node_from_dict(data: dict[str, Any]) -> ContentNode:
    children = [node_from_dict(item) for item in data.get("children") or []]
    return ContentNode(
        type=str(data.get("type") or "unknown"),
        text=data.get("text"),
        url=data.get("url"),
        sha256=data.get("sha256"),
        children=children,
        extra=dict(data.get("extra") or {}),
    )


def item_relpath(item_id: str) -> str:
    """逻辑 item_id 用冒号，目录用斜杠分段。"""
    return "/".join(part for part in item_id.split(":") if part)
