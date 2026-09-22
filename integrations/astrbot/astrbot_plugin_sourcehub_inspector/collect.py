"""检查插件把群消息写入统一 Vault。"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .sourcehub.constants import DEFAULT_MEDIA_MAX_BYTES, DEFAULT_SESSION_END, DEFAULT_SESSION_START
from .sourcehub.constants import GROUPING_SINGLE, SPOOL_DIR
from .sourcehub.daily import DailyLedger
from .sourcehub.download import fetch_bytes
from .sourcehub.grouping import GroupingEngine
from .sourcehub.media import persist_image_nodes
from .sourcehub.media_jobs import MediaJobQueue
from .sourcehub.qq_ingest import parse_onebot_message
from .sourcehub.rules import RulePack
from .sourcehub.vault import Vault

SPOOL_FILE = "qq_sessions.json"
MAX_CONCURRENT_MEDIA_DOWNLOADS = 2
MEDIA_JOB_NODE_PATH = "all_images"
_media_queues: dict[str, MediaJobQueue] = {}
_media_workers: dict[str, asyncio.Task] = {}


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
    daily_ledger: DailyLedger | None = None,
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
        if daily_ledger is not None and envelope.grouping.get("type") == GROUPING_SINGLE:
            daily_ledger.append(incoming, now)
            vault.append_daily_message(envelope)
            continue
        vault.upsert(envelope)
        item_ids.append(envelope.item_id)
        _enqueue_media(envelope.item_id, vault, max_bytes)
    return item_ids


def finalize_daily_collection(vault: Vault, ledger: DailyLedger, conversation_id: str, day: str) -> str | None:
    """手动与定时整理共用的唯一入口，成功落库后才推进日账本游标。"""
    envelope = ledger.finalize(conversation_id, day)
    if envelope is None:
        return None
    vault.upsert(envelope)
    ledger.mark_finalized(conversation_id, day, envelope.grouping["member_event_ids"])
    return envelope.item_id


def _enqueue_media(item_id: str, vault: Vault, max_bytes: int) -> None:
    """先持久入队，再由单个 worker 有限并发下载，事件处理路径不等待网络。"""
    queue_key = str(vault.root)
    queue = _media_queues.setdefault(
        queue_key,
        MediaJobQueue(vault.root / SPOOL_DIR, concurrency=MAX_CONCURRENT_MEDIA_DOWNLOADS),
    )
    queue.enqueue(item_id, MEDIA_JOB_NODE_PATH, "")
    task = _media_workers.get(queue_key)
    if task is None or task.done():
        _media_workers[queue_key] = asyncio.create_task(_drain_media_jobs(queue, vault, max_bytes))


async def _drain_media_jobs(queue: MediaJobQueue, vault: Vault, max_bytes: int) -> None:
    async def enrich(job) -> None:
        envelope = vault.get(job.item_id)
        if envelope is None:
            return

        def work() -> None:
            persist_image_nodes(envelope, vault, max_bytes, fetch_bytes)
            vault.upsert(envelope)

        await asyncio.to_thread(work)

    # drain 会保存每个任务状态；循环处理 worker 运行期间追加的新任务。
    while queue.pending():
        await queue.drain(enrich)


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
