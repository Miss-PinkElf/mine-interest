"""QQ OneBot 状态探针（QQ Status Probe）。"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from .sourcehub.alerts import DISCONNECTED, HEALTHY, UNKNOWN

STATUS_TIMEOUT_SECONDS = 10
DEFAULT_DISCONNECT_GRACE_SECONDS = 300
DEFAULT_STATUS_INTERVAL_SECONDS = 30


async def probe_qq_status(context, platform_id: str) -> str:
    """仅采信 OneBot get_status 的明确结果；无消息不是掉线证据。"""
    if not platform_id:
        return UNKNOWN
    try:
        platform = context.get_platform_inst(platform_id)
        client = platform.get_client() if platform else None
        action = getattr(getattr(client, "api", None), "call_action", None)
        if not callable(action):
            return UNKNOWN
        result = await asyncio.wait_for(action("get_status"), timeout=STATUS_TIMEOUT_SECONDS)
    except Exception:
        return UNKNOWN
    if not isinstance(result, dict):
        return UNKNOWN
    data = result.get("data") if isinstance(result.get("data"), dict) else result
    if data.get("online") is True and data.get("good", True) is True:
        return HEALTHY
    if data.get("online") is False:
        return DISCONNECTED
    return UNKNOWN


class QQDisconnectGrace:
    def __init__(self, grace_seconds: int = DEFAULT_DISCONNECT_GRACE_SECONDS):
        self.grace_seconds = max(0, grace_seconds)
        self.first_disconnected_at: datetime | None = None

    def observe(self, status: str, now: datetime | None = None) -> str:
        now = now or datetime.now(timezone.utc)
        if status == HEALTHY:
            self.first_disconnected_at = None
            return HEALTHY
        if status == UNKNOWN:
            self.first_disconnected_at = None
            return UNKNOWN
        if status == DISCONNECTED:
            if self.first_disconnected_at is None:
                self.first_disconnected_at = now
            if (now - self.first_disconnected_at).total_seconds() >= self.grace_seconds:
                return DISCONNECTED
        return UNKNOWN
