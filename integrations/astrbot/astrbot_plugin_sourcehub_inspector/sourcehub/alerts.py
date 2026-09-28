"""告警状态机（Alert State Machine）：状态变化去重与持久待送。"""

from __future__ import annotations

import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .vault import atomic_write

HEALTHY = "healthy"
LOGIN_REQUIRED = "login_required"
DISCONNECTED = "disconnected"
UNKNOWN = "unknown"
FAULT_STATUSES = {LOGIN_REQUIRED, DISCONNECTED}
EVENT_LABELS = {
    LOGIN_REQUIRED: "登录失效",
    DISCONNECTED: "连接中断",
    HEALTHY: "已恢复",
}


class AlertLedger:
    def __init__(self, path: Path):
        self.path = path
        self.lock_path = path.with_suffix(".lock")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> dict:
        if not self.path.exists():
            return {"states": {}, "pending": {}, "next_id": 1}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, value: dict) -> None:
        atomic_write(self.path, json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))

    def observe(self, platform: str, account: str, status: str, observed_at: str | None = None) -> dict | None:
        if status not in FAULT_STATUSES | {HEALTHY, UNKNOWN}:
            raise ValueError("invalid_alert_status")
        if platform not in {"bilibili", "qq"}:
            raise ValueError("invalid_alert_platform")
        if not account or not account.isdecimal():
            raise ValueError("invalid_alert_account")
        if status == UNKNOWN:
            return None
        key = f"{platform}:{account}"
        with self.lock_path.open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            state = self._read()
            previous = state["states"].get(key, HEALTHY)
            if previous == status:
                return None
            state["states"][key] = status
            if previous == HEALTHY and status == HEALTHY:
                self._write(state)
                return None
            event_id = str(state["next_id"]).zfill(8)
            state["next_id"] += 1
            event = {
                "id": event_id,
                "platform": platform,
                "account": f"尾号 {account[-4:]}",
                "status": status,
                "time": observed_at or datetime.now(timezone.utc).isoformat(),
            }
            state["pending"][event_id] = event
            self._write(state)
            return event

    def pending(self) -> list[dict]:
        return list(self._read()["pending"].values())

    def mark_delivered(self, event_id: str) -> None:
        with self.lock_path.open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            state = self._read()
            state["pending"].pop(event_id, None)
            self._write(state)
