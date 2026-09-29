"""AstrBot 插件入口（AstrBot Plugin Entry）。"""

from __future__ import annotations

import asyncio

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools, register

from .constants import (
    ENABLED_GROUP_IDS_KEY,
    CONFIGURATION_INVALID_REPLY,
    EMPTY_MESSAGE_REPLY,
    INTERRUPTED_ON_RESTART_REPLY,
    LOG_PREFIX,
    NOT_ALLOWED_REPLY,
    PLUGIN_DESCRIPTION,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    PRIVATE_ENABLED_KEY,
    RECEIPT_CANCELLED,
    RECEIPT_DELIVERY_FAILED,
    RECEIPT_ERROR,
    RECEIPT_INTERRUPTED,
    RECEIPT_PROCESSING,
    REASON_CONFIGURATION_INVALID,
    REASON_NOT_ALLOWED,
    REASON_OUT_OF_SCOPE,
    REASON_WORK_DIR_MISSING,
    SERVICE_ERROR_REPLY,
    UNSUPPORTED_SEGMENT_REPLY,
    WORK_DIR_MISSING_REPLY,
)
from .contracts import ConversationKind, IncomingMessage
from .platform.qq_events import parse_qq_event
from .platform.replies import send_text
from .policy import authorize
from .service import ConversationService
from .sessions import SessionManager
from .storage import SessionStore


@register(PLUGIN_NAME, "Codex", PLUGIN_DESCRIPTION, PLUGIN_VERSION)
class CcQqPlugin(Star):
    """管理插件生命周期与 QQ 消息入口。"""

    def __init__(self, context: Context, config=None):
        super().__init__(context, config)
        self.config = config or {}
        self.store = SessionStore(StarTools.get_data_dir(PLUGIN_NAME))
        self.sessions = SessionManager(self.store, self.config)
        self.service = ConversationService(self.store, self.sessions)
        self._background_tasks: set[asyncio.Task] = set()

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
        for pending in self.store.queued_messages():
            decision = authorize(pending, self.config)
            if not decision.allowed:
                self.store.mark_message(
                    pending.conversation, pending.message_id, RECEIPT_CANCELLED
                )
                continue
            self._schedule_background(self._replay_queued(pending, decision))
        for interrupted in self.store.processing_messages():
            self.store.mark_message(
                interrupted.conversation, interrupted.message_id, RECEIPT_INTERRUPTED
            )
            if authorize(interrupted, self.config).allowed:
                self._schedule_background(self._notify_interrupted(interrupted))

    def _schedule_background(self, coroutine):
        task = asyncio.create_task(coroutine)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def terminate(self):
        self.sessions.begin_shutdown()
        in_flight = self.store.processing_messages()
        for task in tuple(self._background_tasks):
            task.cancel()
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        await self.sessions.shutdown()
        for message in in_flight:
            status = self.store.message_status(message.conversation, message.message_id)
            if status in (RECEIPT_CANCELLED, RECEIPT_PROCESSING):
                self.store.mark_message(
                    message.conversation, message.message_id, RECEIPT_PROCESSING
                )
        self.logger.info("%s 已停止", LOG_PREFIX)

    async def _notify_interrupted(self, message: IncomingMessage):
        try:
            delivered = await send_text(
                self.context, message.origin, INTERRUPTED_ON_RESTART_REPLY, self.logger
            )
        except asyncio.CancelledError:
            self.store.mark_message(
                message.conversation, message.message_id, RECEIPT_PROCESSING
            )
            raise
        if not delivered:
            self.store.mark_message(
                message.conversation, message.message_id, RECEIPT_DELIVERY_FAILED
            )

    async def _replay_queued(self, message, decision):
        try:
            reply = await self.service.handle(message, decision, claimed=True)
            if reply:
                delivered = await send_text(self.context, message.origin, reply, self.logger)
                if not delivered:
                    self.store.mark_message(
                        message.conversation, message.message_id, RECEIPT_DELIVERY_FAILED
                    )
        except Exception as exc:
            self.logger.error("%s 待处理消息恢复失败：%s", LOG_PREFIX, type(exc).__name__)
            self.store.mark_message(message.conversation, message.message_id, RECEIPT_ERROR)

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_qq_message(self, event: AstrMessageEvent):
        message = parse_qq_event(event)
        if message is None:
            return
        if message.conversation.kind is ConversationKind.GROUP and not message.mentions_bot:
            return

        decision = authorize(message, self.config)
        if not decision.allowed:
            if decision.reason == REASON_OUT_OF_SCOPE:
                return
        event.stop_event()
        if not decision.allowed:
            reason_replies = {
                REASON_NOT_ALLOWED: NOT_ALLOWED_REPLY,
                REASON_CONFIGURATION_INVALID: CONFIGURATION_INVALID_REPLY,
                REASON_WORK_DIR_MISSING: WORK_DIR_MISSING_REPLY,
            }
            reply = reason_replies.get(decision.reason, CONFIGURATION_INVALID_REPLY)
        elif message.has_unsupported_segments:
            reply = UNSUPPORTED_SEGMENT_REPLY
        elif not message.text:
            reply = EMPTY_MESSAGE_REPLY
        else:
            try:
                reply = await self.service.handle(message, decision)
            except Exception as exc:
                self.logger.error("%s 消息处理失败：%s", LOG_PREFIX, type(exc).__name__)
                reply = SERVICE_ERROR_REPLY

        if reply:
            delivered = await send_text(self.context, message.origin, reply, self.logger)
            if not delivered and decision.allowed:
                self.store.mark_message(
                    message.conversation, message.message_id, RECEIPT_DELIVERY_FAILED
                )
