"""B 站按作品合并（Work Object Merge）。"""

from __future__ import annotations

from typing import Any

from .constants import GROUPING_WORK_OBJECT, PLATFORM_BILIBILI, SCHEMA_VERSION
from .envelope import ContentNode, Envelope


def work_item_id(kind: str, object_id: str) -> str:
    return f"bilibili:{kind}:{object_id}"


def mention_fragment(
    kind: str,
    object_id: str,
    title: str,
    url: str,
    body: str,
    trigger: dict[str, Any],
    parent: dict[str, Any] | None,
    root: dict[str, Any] | None,
    received_at: str,
    conversation_id: str,
    event_id: str,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "object_id": object_id,
        "title": title,
        "url": url,
        "body": body,
        "trigger": trigger,
        "parent": parent,
        "root": root,
        "received_at": received_at,
        "conversation_id": conversation_id,
        "event_id": event_id,
    }


def _comment_node(role: str, payload: dict[str, Any]) -> ContentNode:
    return ContentNode(
        type="text",
        text=str(payload.get("text") or ""),
        extra={"role": role, "rpid": str(payload.get("rpid") or "")},
    )


def _object_node(fragment: dict[str, Any]) -> ContentNode:
    return ContentNode(
        type="text",
        text=str(fragment.get("body") or fragment.get("title") or ""),
        extra={
            "role": "object",
            "url": fragment.get("url"),
            "title": fragment.get("title"),
            "kind": fragment.get("kind"),
            "object_id": fragment.get("object_id"),
        },
    )


def _related_nodes(fragment: dict[str, Any]) -> list[ContentNode]:
    nodes: list[ContentNode] = []
    parent = fragment.get("parent")
    root = fragment.get("root")
    if parent:
        nodes.append(_comment_node("parent", parent))
    if root and (not parent or str(root.get("rpid")) != str(parent.get("rpid"))):
        nodes.append(_comment_node("root", root))
    return nodes


def merge_work_envelope(existing: Envelope | None, fragment: dict[str, Any]) -> Envelope:
    item_id = work_item_id(str(fragment["kind"]), str(fragment["object_id"]))
    object_node = _object_node(fragment)
    trigger = fragment["trigger"]
    trigger_node = _comment_node("trigger", trigger)
    rpid = str(trigger.get("rpid") or fragment.get("event_id") or "")
    related = _related_nodes(fragment)

    if existing is None:
        content = [object_node, trigger_node, *related]
        return Envelope(
            schema_version=SCHEMA_VERSION,
            platform=PLATFORM_BILIBILI,
            conversation_id=str(fragment.get("conversation_id") or ""),
            item_id=item_id,
            event_id=rpid,
            sender_id=str(trigger.get("sender_id") or ""),
            source_time=fragment.get("received_at"),
            received_at=str(fragment.get("received_at") or ""),
            content=content,
            attachments=[],
            gaps=[],
            grouping={"type": GROUPING_WORK_OBJECT, "member_event_ids": [rpid], "object_id": fragment["object_id"]},
        )

    content: list[ContentNode] = []
    object_kept = False
    replaced = False
    for node in existing.content:
        role = (node.extra or {}).get("role")
        if role == "object":
            if not object_kept:
                content.append(object_node)
                object_kept = True
            continue
        if role == "trigger" and str((node.extra or {}).get("rpid") or "") == rpid:
            content.append(trigger_node)
            replaced = True
            continue
        content.append(node)
    if not object_kept:
        content.insert(0, object_node)
    if not replaced:
        content.append(trigger_node)
        content.extend(related)

    members = list(existing.grouping.get("member_event_ids") or [])
    if rpid not in members:
        members.append(rpid)
    grouping = dict(existing.grouping)
    grouping["member_event_ids"] = members
    grouping["type"] = GROUPING_WORK_OBJECT
    return Envelope(
        schema_version=SCHEMA_VERSION,
        platform=PLATFORM_BILIBILI,
        conversation_id=existing.conversation_id,
        item_id=item_id,
        event_id=existing.event_id,
        sender_id=existing.sender_id,
        source_time=existing.source_time,
        received_at=existing.received_at,
        content=content,
        attachments=list(existing.attachments),
        gaps=list(existing.gaps),
        grouping=grouping,
        extra=dict(existing.extra),
    )
