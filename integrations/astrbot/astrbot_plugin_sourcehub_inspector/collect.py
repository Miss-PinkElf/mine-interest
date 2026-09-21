"""检查插件把群消息写入统一 Vault。"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .sourcehub.constants import DEFAULT_MEDIA_MAX_BYTES, DEFAULT_SESSION_END, DEFAULT_SESSION_START
from .sourcehub.download import fetch_bytes
from .sourcehub.grouping import GroupingEngine
from .sourcehub.media import persist_image_nodes
from .sourcehub.qq_ingest import parse_onebot_message
from .sourcehub.rules import RulePack
from .sourcehub.vault import Vault

SPOOL_FILE = "qq_sessions.json"


def build_pack(config: dict) -> RulePack:
    return RulePack(
        session_start=str(config.get("session_start") or DEFAULT_SESSION_START),
        session_end=str(config.get("session_end") or DEFAULT_SESSION_END),
        media_max_bytes=int(config.get("media_max_bytes") or DEFAULT_MEDIA_MAX_BYTES),
        judge_enabled=False,
    )


def event_payload(event, expanded_forwards: dict[str, list]) -> dict[str, Any]:
    message_obj = getattr(event, "message_obj", None)
    raw = getattr(message_obj, "raw_message", None)
    if isinstance(raw, dict) and raw.get("message"):
        payload = dict(raw)
        _inject_forwards(payload.get("message") or [], expanded_forwards)
        return payload
    segments = []
    for component in event.get_messages() or []:
        segments.append(_component_segment(component, expanded_forwards))
    sender = ""
    if hasattr(event, "get_sender_id"):
        sender = event.get_sender_id() or ""
    elif message_obj is not None:
        sender = str(getattr(message_obj, "sender", "") or getattr(message_obj, "user_id", "") or "")
    return {
        "message_id": getattr(event, "message_id", None) or getattr(message_obj, "message_id", None),
        "group_id": event.get_group_id() if hasattr(event, "get_group_id") else "",
        "user_id": sender,
        "time": getattr(message_obj, "time", None),
        "message": segments,
    }


def collect_event(
    event,
    expanded_forwards: dict[str, list],
    vault: Vault,
    engine: GroupingEngine,
    spool_path: Path,
    max_bytes: int,
) -> list[str]:
    payload = event_payload(event, expanded_forwards)
    incoming = parse_onebot_message(payload)
    if not incoming.event_id:
        return []
    now = datetime.now(timezone.utc)
    envelopes = engine.ingest(incoming, now)
    envelopes.extend(engine.flush_idle(now))
    item_ids = []
    spool_path.parent.mkdir(parents=True, exist_ok=True)
    spool_path.write_text(json.dumps(engine.dump_sessions(), ensure_ascii=False, indent=2), encoding="utf-8")
    for envelope in envelopes:
        vault.upsert(envelope)
        item_ids.append(envelope.item_id)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            persist_image_nodes(envelope, vault, max_bytes, fetch_bytes)
            vault.upsert(envelope)
        else:
            loop.create_task(_enrich_media(envelope, vault, max_bytes))
    return item_ids


async def _enrich_media(envelope, vault, max_bytes) -> None:
    def work():
        persist_image_nodes(envelope, vault, max_bytes, fetch_bytes)
        vault.upsert(envelope)

    await asyncio.to_thread(work)


def load_engine(pack: RulePack, spool_path: Path) -> GroupingEngine:
    engine = GroupingEngine(pack)
    if spool_path.exists():
        engine.load_sessions(json.loads(spool_path.read_text(encoding="utf-8")))
    return engine


def _inject_forwards(segments: list, expanded_forwards: dict[str, list]) -> None:
    for segment in segments:
        if not isinstance(segment, dict) or segment.get("type") != "forward":
            continue
        data = segment.setdefault("data", {})
        forward_id = str(data.get("id") or "")
        if forward_id in expanded_forwards and not data.get("content"):
            data["content"] = expanded_forwards[forward_id]


def _component_segment(component, expanded_forwards: dict[str, list]) -> dict[str, Any]:
    name = type(component).__name__
    if name == "Plain":
        return {"type": "text", "data": {"text": getattr(component, "text", "") or ""}}
    if name == "Image":
        url = getattr(component, "url", None) or getattr(component, "file", None) or ""
        return {"type": "image", "data": {"url": str(url)}}
    if name == "Forward":
        forward_id = str(getattr(component, "id", "") or "")
        return {
            "type": "forward",
            "data": {"id": forward_id, "content": expanded_forwards.get(forward_id) or []},
        }
    if name == "At":
        return {"type": "text", "data": {"text": f"@{getattr(component, 'qq', '')}"}}
    return {"type": name.lower(), "data": {"value": str(component)}}
