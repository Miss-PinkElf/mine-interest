"""同会话串行执行、代理恢复与中断（Session Manager）。"""

from __future__ import annotations

import asyncio
from contextlib import aclosing
from pathlib import Path

from .agents.claude import ClaudeAdapter
from .agents.codex import CodexAdapter
from .agents.process import ProcessRunner
from .constants import (
    AGENT_NO_TEXT_REPLY,
    CLAUDE_COMMAND,
    CLAUDE_COMMAND_KEY,
    CODEX_COMMAND,
    CODEX_COMMAND_KEY,
    NO_ACTIVE_SESSION_REPLY,
    RECEIPT_CANCELLED,
    RECEIPT_DONE,
    RECEIPT_ERROR,
    RECEIPT_PROCESSING,
)
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
    def __init__(self, store: SessionStore, config: dict):
        self.store = store
        self.config = config
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
                record, self._model_for_record(record, settings), prompt, message_id
            )

    async def new(
        self, conversation: ConversationKey, settings: SessionSettings, prompt: str, message_id: str
    ) -> tuple[SessionRecord, str | None]:
        async with self._lock(conversation):
            self._ensure_open()
            self.store.mark_message(conversation, message_id, RECEIPT_PROCESSING)
            record = self.store.create(conversation, settings)
            reply = await self._execute(record, settings.model, prompt, message_id) if prompt else None
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
        await self.interrupt(conversation)
        async with self._lock(conversation):
            self._ensure_open()
            self.store.mark_message(conversation, message_id, RECEIPT_PROCESSING)
            record = self.store.active(conversation)
            if record is None or not record.agent_session_id:
                return NO_ACTIVE_SESSION_REPLY
            return await self._execute(
                record, self._model_for_record(record, settings), prompt, message_id
            ) or ""

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
        self, record: SessionRecord, model: str, prompt: str, message_id: str
    ) -> str | None:
        key = record.conversation.storage_key()
        task = asyncio.current_task()
        if task is not None:
            self._running[key] = task
        request = AgentRequest(
            conversation=record.conversation,
            work_dir=record.work_dir,
            message=prompt,
            model=model,
            agent_session_id=record.agent_session_id,
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
