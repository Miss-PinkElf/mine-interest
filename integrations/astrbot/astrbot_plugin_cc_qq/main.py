"""AstrBot 插件入口（AstrBot Plugin Entry）。"""

from __future__ import annotations

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools, register

from .constants import (
    ENABLED_GROUP_IDS_KEY,
    AGENT_NOT_READY_REPLY,
    CONFIGURATION_INVALID_REPLY,
    LOG_PREFIX,
    NOT_ALLOWED_REPLY,
    PLUGIN_DESCRIPTION,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    PRIVATE_ENABLED_KEY,
    REASON_CONFIGURATION_INVALID,
    REASON_NOT_ALLOWED,
    REASON_OUT_OF_SCOPE,
    REASON_WORK_DIR_MISSING,
    UNSUPPORTED_SEGMENT_REPLY,
    WORK_DIR_MISSING_REPLY,
)
from .platform.qq_events import parse_qq_event
from .platform.replies import send_text
from .policy import authorize
from .storage import SessionStore


@register(PLUGIN_NAME, "Codex", PLUGIN_DESCRIPTION, PLUGIN_VERSION)
class CcQqPlugin(Star):
    """管理插件生命周期与 QQ 消息入口。"""

    def __init__(self, context: Context, config=None):
        super().__init__(context, config)
        self.config = config or {}
        self.store = SessionStore(StarTools.get_data_dir(PLUGIN_NAME))

    async def initialize(self):
        group_count = len(self.config.get(ENABLED_GROUP_IDS_KEY) or [])
        private_enabled = bool(self.config.get(PRIVATE_ENABLED_KEY, False))
        self.logger.info(
            "%s 已加载 v%s：启用群 %s 个，私聊 %s",
            LOG_PREFIX,
            PLUGIN_VERSION,
            group_count,
            "启用" if private_enabled else "关闭",
        )

    async def terminate(self):
        self.logger.info("%s 已停止", LOG_PREFIX)

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_qq_message(self, event: AstrMessageEvent):
        message = parse_qq_event(event)
        if message is None:
            return

        decision = authorize(message, self.config)
        if not decision.allowed:
            if decision.reason == REASON_OUT_OF_SCOPE:
                return
            reason_replies = {
                REASON_NOT_ALLOWED: NOT_ALLOWED_REPLY,
                REASON_CONFIGURATION_INVALID: CONFIGURATION_INVALID_REPLY,
                REASON_WORK_DIR_MISSING: WORK_DIR_MISSING_REPLY,
            }
            reply = reason_replies.get(decision.reason, CONFIGURATION_INVALID_REPLY)
        elif message.has_unsupported_segments:
            reply = UNSUPPORTED_SEGMENT_REPLY
        else:
            reply = AGENT_NOT_READY_REPLY

        await send_text(self.context, message.origin, reply, self.logger)
