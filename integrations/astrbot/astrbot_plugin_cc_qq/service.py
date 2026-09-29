"""QQ 消息到命令、会话和代理的编排（Conversation Service）。"""

from __future__ import annotations

import asyncio

from .commands.registry import parse_command
from .commands.session import (
    cc_prompt,
    help_text,
    info_text,
    new_session_text,
    resumed_session_text,
)
from .constants import (
    AGENT_INTERRUPTED_REPLY,
    CC_USAGE_REPLY,
    CONTINUE_PROMPT,
    NO_RUNNING_AGENT_REPLY,
    NO_SESSION_TO_END_REPLY,
    NO_SESSION_TO_RESUME_REPLY,
    RECEIPT_CANCELLED,
    RECEIPT_DONE,
    RECEIPT_ERROR,
    RECEIPT_QUEUED,
    SESSION_ENDED_REPLY,
)
from .contracts import AuthorizationDecision, IncomingMessage, SessionSettings
from .sessions import SessionManager
from .storage import SessionStore


class ConversationService:
    def __init__(self, store: SessionStore, sessions: SessionManager):
        self.store = store
        self.sessions = sessions

    async def handle(
        self, message: IncomingMessage, decision: AuthorizationDecision, claimed: bool = False
    ) -> str | None:
        if self.sessions.is_closing:
            return None
        if not claimed and not self.store.claim_message(message):
            return None
        settings = decision.settings
        assert settings is not None
        command = parse_command(message.text)
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

    async def _command(
        self, message: IncomingMessage, settings: SessionSettings, name: str, argument: str
    ) -> str | None:
        conversation = message.conversation
        if name == "/help":
            return help_text()
        if name == "/info":
            return info_text(self.store.active(conversation))
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
