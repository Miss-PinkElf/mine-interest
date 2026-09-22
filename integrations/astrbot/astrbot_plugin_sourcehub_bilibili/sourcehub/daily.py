"""QQ 日收集账本（Daily Ledger）：持久保存尚未成条的普通消息。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .envelope import node_from_dict
from .grouping import IncomingMessage, daily_envelope
from .vault import atomic_write

DAILY_LEDGER_DIRECTORY = "qq_daily"
LEDGER_MESSAGES_KEY = "messages"
LEDGER_FINALIZED_IDS_KEY = "finalized_event_ids"


class DailyLedger:
    """按会话与北京时间日期保存普通 QQ 消息，供同一整理器消费。"""

    def __init__(self, spool_root: Path, timezone_name: str = "Asia/Shanghai"):
        self.root = spool_root / DAILY_LEDGER_DIRECTORY
        self.timezone = ZoneInfo(timezone_name)

    def append(self, message: IncomingMessage, received_at: datetime) -> str:
        day = received_at.astimezone(self.timezone).date().isoformat()
        payload = self._read(message.conversation_id, day)
        messages = payload[LEDGER_MESSAGES_KEY]
        if not any(item.get("event_id") == message.event_id for item in messages):
            messages.append(_message_to_dict(message))
            self._write(message.conversation_id, day, payload)
        return day

    def pending(self, conversation_id: str, day: str) -> list[IncomingMessage]:
        payload = self._read(conversation_id, day)
        finalized = set(payload[LEDGER_FINALIZED_IDS_KEY])
        return [
            _message_from_dict(item)
            for item in payload[LEDGER_MESSAGES_KEY]
            if item.get("event_id") not in finalized
        ]

    def mark_finalized(self, conversation_id: str, day: str, event_ids: list[str]) -> None:
        payload = self._read(conversation_id, day)
        finalized = payload[LEDGER_FINALIZED_IDS_KEY]
        for event_id in event_ids:
            if event_id not in finalized:
                finalized.append(event_id)
        self._write(conversation_id, day, payload)

    def finalize(self, conversation_id: str, day: str):
        """返回当批日条目；调用方成功写入 Vault 后再调用 mark_finalized。"""
        return daily_envelope(self.pending(conversation_id, day), day)

    def _path(self, conversation_id: str, day: str) -> Path:
        return self.root / conversation_id / f"{day}.json"

    def _read(self, conversation_id: str, day: str) -> dict:
        path = self._path(conversation_id, day)
        if not path.exists():
            return {LEDGER_MESSAGES_KEY: [], LEDGER_FINALIZED_IDS_KEY: []}
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, conversation_id: str, day: str, payload: dict) -> None:
        atomic_write(
            self._path(conversation_id, day),
            json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
        )


def _message_to_dict(message: IncomingMessage) -> dict:
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


def _message_from_dict(data: dict) -> IncomingMessage:
    return IncomingMessage(
        platform=str(data.get("platform") or "qq"),
        conversation_id=str(data.get("conversation_id") or ""),
        event_id=str(data.get("event_id") or ""),
        sender_id=str(data.get("sender_id") or ""),
        source_time=data.get("source_time"),
        received_at=str(data.get("received_at") or ""),
        text=str(data.get("text") or ""),
        nodes=[node_from_dict(node) for node in data.get("nodes") or []],
        is_forward=bool(data.get("is_forward")),
        raw=dict(data.get("raw") or {}),
    )
