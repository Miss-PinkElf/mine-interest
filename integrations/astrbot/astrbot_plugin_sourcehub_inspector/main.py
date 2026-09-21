"""SourceHub 消息检查器（Message Inspector）。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Forward
from astrbot.api.star import Context, Star, register

from .collect import build_pack, collect_event, load_engine
from .constants import (
    ALL_GROUPS_SCOPE_LABEL,
    COLLECT_ENABLED_KEY,
    DEFAULT_VAULT_DIR,
    ENABLED_GROUP_IDS_KEY,
    FORWARD_DIR_NAME,
    LOG_PREFIX,
    MEDIA_MAX_BYTES_KEY,
    SNAPSHOT_DIR_NAME,
    VAULT_DIR_KEY,
)
from .sourcehub.constants import DEFAULT_MEDIA_MAX_BYTES, SPOOL_DIR
from .sourcehub.vault import Vault
from .forward_expander import (
    expand_forward_tree,
    fetch_forward_messages,
    resolve_call_action,
    summarize_forward_tree,
)
from .forward_renderer import render_forward


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


def _parse_enabled_group_ids(config: dict | None) -> set[str]:
    """解析群白名单。留空表示全部群启用；群号统一转字符串便于比对。"""
    raw = (config or {}).get(ENABLED_GROUP_IDS_KEY) or []
    if isinstance(raw, (str, int)):
        raw = [raw]
    return {str(item).strip() for item in raw if str(item).strip()}


def _describe_group(event: AstrMessageEvent) -> str:
    """拼出「群名(群号)」用于日志；取不到群名时退化为群号。"""
    group_id = event.get_group_id() or ""
    group = getattr(event.message_obj, "group", None)
    group_name = getattr(group, "group_name", "") or ""
    if group_name and group_id:
        return f"{group_name}({group_id})"
    return group_name or group_id or "非群聊"


@register("astrbot_plugin_sourcehub_inspector", "Codex", "保存消息事件快照并成条入库", "0.5.0")
class SourceHubInspector(Star):
    def __init__(self, context: Context, config: dict | None = None):
        super().__init__(context, config)
        self.config = config or {}
        self._enabled_group_ids = _parse_enabled_group_ids(self.config)

        self._snapshot_dir = Path("data") / SNAPSHOT_DIR_NAME
        self._forward_dir = Path("data") / FORWARD_DIR_NAME
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._forward_dir.mkdir(parents=True, exist_ok=True)

        self._collect_enabled = bool(self.config.get(COLLECT_ENABLED_KEY, True))
        vault_dir = Path(str(self.config.get(VAULT_DIR_KEY) or DEFAULT_VAULT_DIR))
        self._vault = Vault(vault_dir, git_enabled=True) if self._collect_enabled else None
        self._pack = build_pack(self.config)
        self._spool_path = vault_dir / SPOOL_DIR / "qq_sessions.json"
        self._engine = load_engine(self._pack, self._spool_path) if self._collect_enabled else None
        self._media_max_bytes = int(self.config.get(MEDIA_MAX_BYTES_KEY) or DEFAULT_MEDIA_MAX_BYTES)

        self.logger.info(
            "%s 插件已加载，快照目录：%s，启用范围：%s，成条：%s，Vault：%s",
            LOG_PREFIX,
            self._snapshot_dir,
            self._describe_scope(),
            self._collect_enabled,
            vault_dir,
        )

    def _describe_scope(self) -> str:
        """启用范围的日志文案。留空时明确说明是全部群。"""
        if not self._enabled_group_ids:
            return f"{ALL_GROUPS_SCOPE_LABEL}（白名单留空）"
        return "、".join(sorted(self._enabled_group_ids))

    def _is_group_enabled(self, group_id: str) -> bool:
        """白名单留空时全部启用；填了白名单则只放行列出的群。"""
        if not self._enabled_group_ids:
            return True
        return group_id in self._enabled_group_ids

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def inspect_message(self, event: AstrMessageEvent):
        group_id = event.get_group_id() or ""
        if not self._is_group_enabled(group_id):
            self.logger.debug(
                "%s 群不在启用范围内，跳过：%s", LOG_PREFIX, _describe_group(event)
            )
            return

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
        self.logger.info(
            "%s 已保存消息快照：%s -> %s", LOG_PREFIX, _describe_group(event), file_path
        )

        expanded = await self._expand_forwards(event, received_at, event_id)
        if self._collect_enabled and self._vault is not None and self._engine is not None:
            try:
                item_ids = collect_event(
                    event,
                    expanded,
                    self._vault,
                    self._engine,
                    self._spool_path,
                    self._media_max_bytes,
                )
                if item_ids:
                    self.logger.info("%s 已成条入库：%s", LOG_PREFIX, "、".join(item_ids))
            except Exception:
                self.logger.exception("%s 成条入库失败", LOG_PREFIX)

    async def _expand_forwards(
        self, event: AstrMessageEvent, received_at: str, event_id: str
    ) -> dict:
        """对消息里的每个合并转发段调用 get_forward_msg，展开完整内层树并落盘。"""
        forward_ids = [
            component.id
            for component in event.get_messages()
            if isinstance(component, Forward) and component.id
        ]
        if not forward_ids:
            return {}

        call_action = resolve_call_action(event)
        if call_action is None:
            self.logger.info("%s 当前平台不支持 get_forward_msg，跳过转发展开", LOG_PREFIX)
            return {}

        expanded = {}
        for forward_id in forward_ids:
            messages = await self._expand_one_forward(event, call_action, received_at, event_id, forward_id)
            if messages is not None:
                expanded[str(forward_id)] = messages
        return expanded

    async def _expand_one_forward(
        self,
        event: AstrMessageEvent,
        call_action,
        received_at: str,
        event_id: str,
        forward_id: str,
    ):
        messages = await fetch_forward_messages(call_action, forward_id)
        if messages is None:
            self.logger.warning(
                "%s 转发消息获取失败：%s forward_id=%s",
                LOG_PREFIX,
                _describe_group(event),
                forward_id,
            )
            return None

        # 补全嵌套转发的 content，再统计成摘要写日志
        await expand_forward_tree(messages, call_action)
        summary = summarize_forward_tree(messages)

        file_path = self._forward_dir / f"{received_at}_{event_id}_{forward_id}.json"
        payload = {
            "received_at": received_at,
            "event_id": event_id,
            "forward_id": forward_id,
            "summary": summary,
            "messages": messages,
        }
        file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        # 同时输出一份可读文本，原始数据仍以 JSON 为准
        text_path = file_path.with_suffix(".txt")
        text_path.write_text(render_forward(payload), encoding="utf-8")

        if summary["message_count"] == 0:
            self.logger.warning(
                "%s 转发展开为空（接口可用但无内容）：%s forward_id=%s -> %s",
                LOG_PREFIX,
                _describe_group(event),
                forward_id,
                file_path,
            )
            return messages

        self.logger.info(
            "%s 已展开转发消息：%s 层数=%s 内层条数=%s 段类型=%s -> %s",
            LOG_PREFIX,
            _describe_group(event),
            summary["max_depth"],
            summary["message_count"],
            summary["segment_type_counts"],
            text_path,
        )
        return messages

    async def terminate(self):
        self.logger.info("%s 插件已卸载", LOG_PREFIX)
