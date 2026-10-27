"""AstrBot 插件入口（AstrBot Plugin Entry）。"""

from __future__ import annotations

import asyncio
import logging
import time

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools, register

from .approval import ApprovalBroker, approval_targets
from .commands.registry import command_allowed, parse_command
from .constants import (
    APPROVAL_USAGE_REPLY,
    ENABLED_GROUP_IDS_KEY,
    CONFIGURATION_INVALID_REPLY,
    EXECUTION_STARTED_REPLY,
    INTERRUPTED_ON_RESTART_REPLY,
    LOG_PREFIX,
    NO_COMMAND_PERMISSION_REPLY,
    PLUGIN_DESCRIPTION,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    PRIVATE_DUPLICATE_WINDOW_SECONDS,
    PRIVATE_ENABLED_KEY,
    RECEIPT_CANCELLED,
    RECEIPT_DELIVERY_FAILED,
    RECEIPT_ERROR,
    RECEIPT_INTERRUPTED,
    RECEIPT_PROCESSING,
    REASON_CONFIGURATION_INVALID,
    REASON_OUT_OF_SCOPE,
    REASON_WORK_DIR_MISSING,
    SERVICE_ERROR_REPLY,
    UNSUPPORTED_SEGMENT_REPLY,
    WORK_DIR_MISSING_REPLY,
)
from .contracts import ConversationKind, IncomingMessage
from .permissions import ROLE_ADMIN, ROLE_OWNER
from .platform.duplicates import is_recent_duplicate
from .platform.qq_events import empty_text_reply, parse_qq_event, should_ignore_as_stale, stale_max_age_from_config
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
        self.approvals = ApprovalBroker(
            self.store, logging.getLogger(f"{PLUGIN_NAME}.approval"), self.config
        )
        self.service = ConversationService(
            self.store, self.sessions, self.config, self.approvals
        )
        self._background_tasks: set[asyncio.Task] = set()
        self._recent_private_incoming: dict[tuple[str, ...], int] = {}
        self._recent_outgoing: dict[tuple[str, ...], int] = {}
        self._admin_origins: dict[str, str] = {}

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
        try:
            await self.approvals.start(self._notify_approval)
        except OSError as exc:
            # 启动失败时危险操作会被 hook 拒绝，但安全操作仍可用。
            self.logger.error("%s 审批服务启动失败：%s", LOG_PREFIX, type(exc).__name__)
        self.sessions.set_approval_env(self.approvals.hook_env())
        for pending in self.store.queued_messages():
            decision = authorize(
                pending,
                self.config,
                self.store.work_dir_override(pending.conversation),
            )
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
            if authorize(
                interrupted,
                self.config,
                self.store.work_dir_override(interrupted.conversation),
            ).allowed:
                self._schedule_background(self._notify_interrupted(interrupted))

    async def _notify_approval(self, origin: str, text: str) -> None:
        delivered = False
        for target in approval_targets(origin, self._admin_origins.values()):
            if await send_text(self.context, target, text, self.logger):
                delivered = True
        if not delivered:
            raise RuntimeError("审批卡片发送失败")

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
        await self.approvals.stop()
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

        decision = authorize(
            message,
            self.config,
            self.store.work_dir_override(message.conversation),
        )
        if decision.role in (ROLE_OWNER, ROLE_ADMIN) and message.origin:
            self._admin_origins[message.sender_id] = message.origin
        if not decision.allowed:
            if decision.reason == REASON_OUT_OF_SCOPE:
                if message.conversation.kind is ConversationKind.PRIVATE:
                    event.stop_event()
                return
        if (
            message.conversation.kind is ConversationKind.PRIVATE
            and not message.has_unsupported_segments
            and is_recent_duplicate(
                self._recent_private_incoming,
                (message.conversation.storage_key(), message.sender_id, message.text),
                int(time.time()),
                PRIVATE_DUPLICATE_WINDOW_SECONDS,
            )
        ):
            event.stop_event()
            self.logger.info(
                "%s 忽略重复私聊 message_id=%s",
                LOG_PREFIX,
                message.message_id,
            )
            return
        if should_ignore_as_stale(
            message.event_time,
            int(time.time()),
            stale_max_age_from_config(self.config),
        ):
            event.stop_event()
            self.logger.info(
                "%s 忽略过期消息 message_id=%s event_time=%s",
                LOG_PREFIX,
                message.message_id,
                message.event_time,
            )
            return
        # 审批回复不进入会话串行队列，否则会与正在等待审批的代理进程死锁。
        approval_command = parse_command(message.text)
        if approval_command and approval_command[0] in ("/approve", "/deny"):
            event.stop_event()
            await self._handle_approval_command(message, decision, approval_command)
            return
        event.stop_event()
        if not decision.allowed:
            reason_replies = {
                REASON_CONFIGURATION_INVALID: CONFIGURATION_INVALID_REPLY,
                REASON_WORK_DIR_MISSING: WORK_DIR_MISSING_REPLY,
            }
            reply = reason_replies.get(decision.reason, CONFIGURATION_INVALID_REPLY)
        elif message.has_unsupported_segments:
            reply = UNSUPPORTED_SEGMENT_REPLY
        elif not message.text:
            reply = empty_text_reply(message.conversation.kind)
        else:
            try:
                reply = await self.service.handle(
                    message, decision, on_started=lambda: self._notify_started(message)
                )
            except Exception as exc:
                self.logger.error("%s 消息处理失败：%s", LOG_PREFIX, type(exc).__name__)
                reply = SERVICE_ERROR_REPLY

        await self._send_reply(message, reply, decision.allowed)

    async def _notify_started(self, message) -> None:
        """执行回执：长任务期间不给任何反馈会让用户以为没反应。"""
        await send_text(self.context, message.origin, EXECUTION_STARTED_REPLY, self.logger)

    async def _handle_approval_command(self, message, decision, command) -> None:
        name, argument = command
        if not command_allowed(decision.role, name):
            reply = NO_COMMAND_PERMISSION_REPLY
        elif not argument:
            reply = APPROVAL_USAGE_REPLY
        else:
            reply = self.approvals.resolve(
                argument.strip(), name == "/approve", message.sender_id
            )
        await self._send_reply(message, reply, False)

    async def _send_reply(self, message, reply: str, mark_failed: bool) -> None:
        """统一回复与重复回复抑制；审批回复也走这里，但不写消息回执。"""
        if reply:
            outgoing_key = (message.origin, reply)
            now = int(time.time())
            last_sent = self._recent_outgoing.get(outgoing_key)
            if (
                last_sent is not None
                and 0 <= now - last_sent <= PRIVATE_DUPLICATE_WINDOW_SECONDS
            ):
                self.logger.info("%s 忽略重复回复 origin=%s", LOG_PREFIX, message.origin)
                return
            delivered = await send_text(self.context, message.origin, reply, self.logger)
            if delivered:
                is_recent_duplicate(
                    self._recent_outgoing,
                    outgoing_key,
                    now,
                    PRIVATE_DUPLICATE_WINDOW_SECONDS,
                )
            if not delivered and mark_failed:
                self.store.mark_message(
                    message.conversation, message.message_id, RECEIPT_DELIVERY_FAILED
                )
