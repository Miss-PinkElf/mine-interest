"""SourceHub 消息检查器（Message Inspector）。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

LOG_PREFIX = "[SourceHub Inspector]"
SNAPSHOT_DIR_NAME = "sourcehub-inspector/snapshots"


def _safe_value(value: Any, depth: int = 0) -> Any:
    if depth > 8:
        return "<max-depth>"
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple, set)):
        return [_safe_value(item, depth + 1) for item in value]
    if isinstance(value, dict):
        return {str(key): _safe_value(item, depth + 1) for key, item in value.items()}
    if hasattr(value, "__dict__"):
        return {
            "__type__": type(value).__name__,
            "fields": _safe_value(vars(value), depth + 1),
        }
    return {"__type__": type(value).__name__, "value": str(value)}


@register("astrbot_plugin_sourcehub_inspector", "Codex", "保存消息事件快照", "0.1.0")
class SourceHubInspector(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._snapshot_dir = Path("data") / SNAPSHOT_DIR_NAME
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info("%s 插件已加载，快照目录：%s", LOG_PREFIX, self._snapshot_dir)

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def inspect_message(self, event: AstrMessageEvent):
        received_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        event_id = str(getattr(event, "message_id", None) or received_at)
        snapshot = {
            "received_at": received_at,
            "event_type": type(event).__name__,
            "event_id": event_id,
            "event": _safe_value(event),
        }
        file_path = self._snapshot_dir / f"{received_at}_{event_id}.json"
        file_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        self.logger.info("%s 已保存消息快照：%s", LOG_PREFIX, file_path)

    async def terminate(self):
        self.logger.info("%s 插件已卸载", LOG_PREFIX)
