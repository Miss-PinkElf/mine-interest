"""QQ 消息到命令、会话和代理的编排（Conversation Service）。"""

from __future__ import annotations

import asyncio
from pathlib import Path

from .commands.registry import command_allowed, parse_command, will_run_agent
from .commands.session import (
    cc_prompt,
    cd_list_text,
    cd_success_text,
    help_text,
    info_text,
    initbase_text,
    new_session_text,
    pwd_text,
    resumed_session_text,
)
from .constants import (
    AGENT_INTERRUPTED_REPLY,
    APPROVAL_BROKER_ERROR_REPLY,
    APPROVAL_USAGE_REPLY,
    CC_USAGE_REPLY,
    CD_INDEX_OUT_OF_RANGE_TEMPLATE,
    CD_LIST_KEYWORD,
    CD_NOT_CONFIGURED_REPLY,
    CD_NOT_DIRECTORY_REPLY,
    CD_OUTSIDE_ROOTS_REPLY,
    CD_RUNNING_REPLY,
    CD_USAGE_REPLY,
    CONTINUE_PROMPT,
    INITBASE_FAILED_REPLY,
    NO_COMMAND_PERMISSION_REPLY,
    NO_RUNNING_AGENT_REPLY,
    NO_SESSION_TO_END_REPLY,
    NO_SESSION_TO_RESUME_REPLY,
    RECEIPT_CANCELLED,
    RECEIPT_DONE,
    RECEIPT_ERROR,
    RECEIPT_QUEUED,
    SESSION_ENDED_REPLY,
    WORK_DIR_MISSING_REPLY,
)
from .contracts import (
    AuthorizationDecision,
    ConversationKey,
    IncomingMessage,
    SessionSettings,
)
from .permissions import allowed_work_dir, resolve_path, workspace_roots
from .sessions import SessionManager
from .storage import SessionStore
from .templates import init_base_templates


class ConversationService:
    def __init__(
        self,
        store: SessionStore,
        sessions: SessionManager,
        config: dict | None = None,
        approvals=None,
    ):
        self.store = store
        self.sessions = sessions
        self.config = config or {}
        self.approvals = approvals

    async def handle(
        self,
        message: IncomingMessage,
        decision: AuthorizationDecision,
        claimed: bool = False,
        on_started=None,
    ) -> str | None:
        if self.sessions.is_closing:
            return None
        if not claimed and not self.store.claim_message(message):
            return None
        settings = decision.settings
        assert settings is not None
        command = parse_command(message.text)
        # 回执必须在 claim、权限、参数与会话校验之后发，避免「先处理后被拒」。
        if on_started is not None and self._should_notify_started(
            command, settings, message.conversation
        ):
            await on_started()
        try:
            if command is None:
                reply = await self.sessions.run(
                    message.conversation, settings, message.text, message.message_id
                )
            else:
                name, argument = command
                reply = await self._command(message, settings, name, argument)
            status = RECEIPT_DONE if reply is not None else RECEIPT_CANCELLED
            self.store.mark_message(message.conversation, message.message_id, status)
            return reply
        except asyncio.CancelledError:
            if self.store.message_status(message.conversation, message.message_id) != RECEIPT_QUEUED:
                self.store.mark_message(message.conversation, message.message_id, RECEIPT_CANCELLED)
            return None
        except Exception:
            self.store.mark_message(message.conversation, message.message_id, RECEIPT_ERROR)
            raise

    def _should_notify_started(
        self, command, settings: SessionSettings, conversation: ConversationKey
    ) -> bool:
        """只有真正会启动代理且用户有权执行时才发执行回执。"""
        if not will_run_agent(command, settings.role):
            return False
        if command is not None and command[0] == "/goon":
            record = self.store.active(conversation)
            return bool(record and record.agent_session_id)
        return True

    async def _command(
        self, message: IncomingMessage, settings: SessionSettings, name: str, argument: str
    ) -> str | None:
        conversation = message.conversation
        if not command_allowed(settings.role, name):
            return NO_COMMAND_PERMISSION_REPLY

        if name == "/help":
            return help_text(settings.role)
        if name == "/info":
            return info_text(self.store.active(conversation))
        if name == "/pwd":
            return pwd_text(settings)
        if name == "/cd":
            return self._change_work_dir(conversation, settings, argument)
        if name == "/initbase":
            return self._init_base(settings)
        if name in ("/approve", "/deny"):
            if self.approvals is None:
                return APPROVAL_BROKER_ERROR_REPLY
            if not argument:
                return APPROVAL_USAGE_REPLY
            return self.approvals.resolve(
                argument.strip(), name == "/approve", settings.sender_id
            )
        if name == "/!":
            interrupted = await self.sessions.interrupt(conversation)
            if argument:
                return await self.sessions.run(
                    conversation, settings, argument, message.message_id
                )
            return AGENT_INTERRUPTED_REPLY if interrupted else NO_RUNNING_AGENT_REPLY
        if name == "/end":
            ended = await self.sessions.end(conversation)
            return SESSION_ENDED_REPLY if ended else NO_SESSION_TO_END_REPLY
        if name == "/new":
            await self.sessions.interrupt(conversation)
            record, result = await self.sessions.new(
                conversation, settings, argument, message.message_id
            )
            if argument and result is None:
                return None
            return result or new_session_text(record)
        if name == "/resume":
            record = await self.sessions.resume(conversation, argument)
            return resumed_session_text(record) if record else NO_SESSION_TO_RESUME_REPLY
        if name == "/goon":
            return await self.sessions.goon(
                conversation, settings, CONTINUE_PROMPT, message.message_id
            )
        if name == "/cc":
            if not argument:
                return CC_USAGE_REPLY
            return await self.sessions.run(
                conversation, settings, cc_prompt(argument), message.message_id
            )
        return None

    def _change_work_dir(
        self, conversation: ConversationKey, settings: SessionSettings, argument: str
    ) -> str:
        if not argument:
            return CD_USAGE_REPLY
        roots = workspace_roots(self.config)
        if not roots:
            return CD_NOT_CONFIGURED_REPLY
        text = argument.strip()
        # list 与序号都基于配置顺序，路径形式继续走原有校验。
        if text.lower() == CD_LIST_KEYWORD:
            return cd_list_text(roots, settings.work_dir)
        if text.isdigit():
            index = int(text)
            if not 1 <= index <= len(roots):
                return CD_INDEX_OUT_OF_RANGE_TEMPLATE.format(max_index=len(roots))
            return self._apply_work_dir(conversation, roots[index - 1])
        return self._apply_work_dir(conversation, self._resolve_work_dir_arg(settings, text))

    def _resolve_work_dir_arg(self, settings: SessionSettings, text: str) -> Path:
        raw = Path(text).expanduser()
        if not raw.is_absolute():
            raw = Path(settings.work_dir) / raw
        return resolve_path(raw)

    def _apply_work_dir(self, conversation: ConversationKey, target: Path) -> str:
        if not allowed_work_dir(str(target), self.config):
            return CD_OUTSIDE_ROOTS_REPLY
        if not target.is_dir():
            return CD_NOT_DIRECTORY_REPLY
        # 当前有代理执行时拒绝切换，避免执行中工作目录漂移。
        if self.sessions.is_running(conversation):
            return CD_RUNNING_REPLY
        self.store.set_work_dir_override(conversation, str(target))
        self.store.end(conversation)
        return cd_success_text(str(target))

    def _init_base(self, settings: SessionSettings) -> str:
        if not Path(settings.work_dir).is_dir():
            return WORK_DIR_MISSING_REPLY
        try:
            created, skipped = init_base_templates(settings.work_dir)
        except OSError:
            return INITBASE_FAILED_REPLY
        return initbase_text(created, skipped)
