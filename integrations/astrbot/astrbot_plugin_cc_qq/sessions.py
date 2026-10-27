"""同会话串行执行、代理恢复与中断（Session Manager）。"""

from __future__ import annotations

import asyncio
from pathlib import Path

from .agents.claude import ClaudeAdapter
from .agents.codex import CodexAdapter
from .agents.process import ProcessRunner
from .agents.profiles import claude_setting_sources, ensure_claude_settings
from .async_utils import aclosing
from .constants import (
    AGENT_ENV_CONVERSATION_KEY,
    AGENT_ENV_ORIGIN,
    AGENT_ENV_PROFILE,
    AGENT_ENV_ROLE,
    AGENT_ENV_SENDER_ID,
    AGENT_ENV_WORK_DIR,
    AGENT_INTERRUPTED_REPLY,
    AGENT_NO_TEXT_REPLY,
    APPROVAL_HOOK_DIR_NAME,
    APPROVAL_HOOK_SCRIPT_NAME,
    CLAUDE_COMMAND,
    CLAUDE_COMMAND_KEY,
    CODEX_COMMAND,
    CODEX_COMMAND_KEY,
    DANGER_APPROVAL_TIMEOUT_SECONDS_KEY,
    DEFAULT_DANGER_APPROVAL_TIMEOUT_SECONDS,
    DEFAULT_READONLY_MCP_ENABLED,
    GOON_INTERRUPTED_PREFIX,
    MAX_DANGER_APPROVAL_TIMEOUT_SECONDS,
    MIN_DANGER_APPROVAL_TIMEOUT_SECONDS,
    NO_ACTIVE_SESSION_REPLY,
    READONLY_MCP_ENABLED_KEY,
    RECEIPT_CANCELLED,
    RECEIPT_DONE,
    RECEIPT_ERROR,
    RECEIPT_PROCESSING,
)
from .permissions import PROFILE_WORKSPACE, clamp_approval_timeout
from .contracts import (
    AgentEventKind,
    AgentRequest,
    ConversationKey,
    ConversationKind,
    SessionRecord,
    SessionSettings,
)
from .policy import default_model_for_agent
from .storage import SessionStore


class SessionManager:
    def __init__(self, store: SessionStore, config: dict, data_dir: Path | None = None):
        self.store = store
        self.config = config
        self.data_dir = Path(data_dir) if data_dir else Path(store.data_dir)
        self.processes = ProcessRunner()
        claude_command = str(config.get(CLAUDE_COMMAND_KEY) or CLAUDE_COMMAND).strip()
        codex_command = str(config.get(CODEX_COMMAND_KEY) or CODEX_COMMAND).strip()
        self.adapters = {
            "claude": ClaudeAdapter(self.processes, claude_command),
            "codex": CodexAdapter(self.processes, codex_command),
        }
        self._locks: dict[str, asyncio.Lock] = {}
        self._running: dict[str, asyncio.Task] = {}
        self._closing = False
        self._approval_env: dict[str, str] = {}
        self._approval_timeout_seconds = clamp_approval_timeout(
            config.get(DANGER_APPROVAL_TIMEOUT_SECONDS_KEY),
            DEFAULT_DANGER_APPROVAL_TIMEOUT_SECONDS,
            MIN_DANGER_APPROVAL_TIMEOUT_SECONDS,
            MAX_DANGER_APPROVAL_TIMEOUT_SECONDS,
        )
        self._approval_hook_script = (
            Path(__file__).resolve().parent / APPROVAL_HOOK_DIR_NAME / APPROVAL_HOOK_SCRIPT_NAME
        )

    def set_approval_env(self, env: dict[str, str]) -> None:
        """审批服务启动后注入 hook 需要的本机地址与 token。"""
        self._approval_env = dict(env)

    def is_running(self, conversation: ConversationKey) -> bool:
        task = self._running.get(conversation.storage_key())
        return task is not None and not task.done()

    @property
    def is_closing(self) -> bool:
        return self._closing

    def begin_shutdown(self) -> None:
        self._closing = True

    def _ensure_open(self) -> None:
        if self._closing:
            raise asyncio.CancelledError

    def _lock(self, conversation: ConversationKey) -> asyncio.Lock:
        return self._locks.setdefault(conversation.storage_key(), asyncio.Lock())

    def _model_for_record(self, record: SessionRecord, settings: SessionSettings) -> str:
        if record.agent_type == settings.agent_type:
            return settings.model
        return default_model_for_agent(self.config, record.agent_type)

    async def run(
        self, conversation: ConversationKey, settings: SessionSettings, prompt: str, message_id: str
    ) -> str | None:
        async with self._lock(conversation):
            self._ensure_open()
            self.store.mark_message(conversation, message_id, RECEIPT_PROCESSING)
            record = self.store.active(conversation) or self.store.create(conversation, settings)
            return await self._execute(
                record, self._model_for_record(record, settings), prompt, message_id, settings
            )

    async def new(
        self, conversation: ConversationKey, settings: SessionSettings, prompt: str, message_id: str
    ) -> tuple[SessionRecord, str | None]:
        async with self._lock(conversation):
            self._ensure_open()
            self.store.mark_message(conversation, message_id, RECEIPT_PROCESSING)
            record = self.store.create(conversation, settings)
            reply = (
                await self._execute(record, settings.model, prompt, message_id, settings)
                if prompt
                else None
            )
            return record, reply

    async def resume(self, conversation: ConversationKey, identifier: str) -> SessionRecord | None:
        async with self._lock(conversation):
            self._ensure_open()
            return self.store.resume(conversation, identifier)

    async def end(self, conversation: ConversationKey) -> bool:
        await self.interrupt(conversation)
        async with self._lock(conversation):
            self._ensure_open()
            return self.store.end(conversation)

    async def goon(
        self, conversation: ConversationKey, settings: SessionSettings, prompt: str, message_id: str
    ) -> str:
        interrupted = await self.interrupt(conversation)
        async with self._lock(conversation):
            self._ensure_open()
            self.store.mark_message(conversation, message_id, RECEIPT_PROCESSING)
            record = self.store.active(conversation)
            if record is None or not record.agent_session_id:
                return NO_ACTIVE_SESSION_REPLY
            reply = await self._execute(
                record, self._model_for_record(record, settings), prompt, message_id, settings
            )
        # 本轮被后续命令取消时不能静默：空字符串会被判成 done 且不发送，
        # 用户既收不到回复、也看不出被中断。
        if reply is None:
            return AGENT_INTERRUPTED_REPLY
        return f"{GOON_INTERRUPTED_PREFIX}{reply}" if interrupted else reply

    async def interrupt(self, conversation: ConversationKey) -> bool:
        key = conversation.storage_key()
        task = self._running.get(key)
        if task is None or task.done():
            return False
        task.cancel()
        await self.processes.interrupt(key)
        return True

    async def shutdown(self) -> None:
        self.begin_shutdown()
        tasks = tuple(self._running.values())
        for task in tasks:
            task.cancel()
        await self.processes.shutdown()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute(
        self,
        record: SessionRecord,
        model: str,
        prompt: str,
        message_id: str,
        settings: SessionSettings,
    ) -> str | None:
        key = record.conversation.storage_key()
        task = asyncio.current_task()
        if task is not None:
            self._running[key] = task
        profile = settings.permission_profile
        claude_settings_path = ""
        if record.agent_type == "claude":
            claude_settings_path = ensure_claude_settings(
                self.data_dir,
                profile,
                self._approval_hook_script,
                self._approval_timeout_seconds,
                bool(
                    self.config.get(
                        READONLY_MCP_ENABLED_KEY, DEFAULT_READONLY_MCP_ENABLED
                    )
                ),
            )
        process_env = {
            AGENT_ENV_PROFILE: profile,
            AGENT_ENV_ROLE: settings.role,
            AGENT_ENV_WORK_DIR: record.work_dir,
            AGENT_ENV_CONVERSATION_KEY: key,
            AGENT_ENV_SENDER_ID: settings.sender_id,
            AGENT_ENV_ORIGIN: settings.origin,
        }
        if profile == PROFILE_WORKSPACE:
            process_env.update(self._approval_env)
        request = AgentRequest(
            conversation=record.conversation,
            work_dir=record.work_dir,
            message=prompt,
            model=model,
            agent_session_id=record.agent_session_id,
            permission_profile=profile,
            sender_id=settings.sender_id,
            origin=settings.origin,
            claude_settings_path=claude_settings_path,
            claude_setting_sources=claude_setting_sources(self.config),
            process_env=process_env,
        )
        parts: list[str] = []
        final_text = ""
        error = ""
        try:
            if record.conversation.kind is ConversationKind.PRIVATE:
                Path(record.work_dir).mkdir(parents=True, exist_ok=True)
            async with aclosing(self.adapters[record.agent_type].execute(request)) as stream:
                async for event in stream:
                    if event.agent_session_id:
                        self.store.set_agent_session_id(record.id, event.agent_session_id)
                    if event.kind is AgentEventKind.TEXT and event.content:
                        parts.append(event.content)
                    elif event.kind is AgentEventKind.DONE:
                        final_text = event.content
                    elif event.kind is AgentEventKind.ERROR:
                        error = event.content
                        break
            text = "\n".join(parts) or final_text
            if not text and not error:
                error = AGENT_NO_TEXT_REPLY
            reply = f"{text}\n\n{error}" if text and error else error or text
            status = RECEIPT_ERROR if error else RECEIPT_DONE
            self.store.record_turn(record.id, message_id, prompt, reply, status)
            return reply
        except asyncio.CancelledError:
            self.store.record_turn(record.id, message_id, prompt, "", RECEIPT_CANCELLED)
            return None
        finally:
            if self._running.get(key) is task:
                self._running.pop(key, None)
