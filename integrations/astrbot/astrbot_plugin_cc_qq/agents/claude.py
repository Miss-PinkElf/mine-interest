"""Claude Code CLI 流事件适配（Claude CLI Adapter）。"""

from __future__ import annotations

import json
from typing import AsyncIterator, Optional
from uuid import uuid4

from ..async_utils import aclosing
from ..constants import CLAUDE_COMMAND
from ..contracts import AgentEvent, AgentEventKind, AgentRequest
from .process import AgentProcessError, ProcessRunner
from .profiles import claude_args


def parse_claude_event(line: str) -> Optional[AgentEvent]:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None

    if payload.get("type") == "system" and payload.get("subtype") == "init":
        session_id = payload.get("session_id")
        if session_id:
            return AgentEvent(AgentEventKind.STARTED, agent_session_id=str(session_id))

    if payload.get("type") == "assistant":
        blocks = (payload.get("message") or {}).get("content") or []
        if isinstance(blocks, list):
            text_parts = [
                str(block.get("text"))
                for block in blocks
                if isinstance(block, dict) and block.get("type") == "text" and block.get("text")
            ]
            if text_parts:
                return AgentEvent(AgentEventKind.TEXT, "\n".join(text_parts))
        content = payload.get("content")
        if isinstance(content, str) and content:
            return AgentEvent(AgentEventKind.TEXT, content)

    if payload.get("type") == "result":
        if payload.get("is_error"):
            return AgentEvent(AgentEventKind.ERROR, "Claude Code 返回执行错误")
        return AgentEvent(AgentEventKind.DONE, str(payload.get("result") or ""))
    return None


class ClaudeAdapter:
    agent_type = "claude"

    def __init__(self, process_runner: ProcessRunner, command: str = CLAUDE_COMMAND):
        self._process_runner = process_runner
        self._command = command

    async def execute(self, request: AgentRequest) -> AsyncIterator[AgentEvent]:
        args = claude_args(
            profile=request.permission_profile,
            model=request.model,
            agent_session_id=request.agent_session_id or "",
            new_session_id=str(uuid4()),
            settings_path=request.claude_settings_path,
            setting_sources=request.claude_setting_sources,
        )
        try:
            async with aclosing(self._process_runner.run(
                request.conversation.storage_key(), self._command, args,
                request.work_dir, request.message, request.process_env,
            )) as lines:
                async for line in lines:
                    event = parse_claude_event(line)
                    if event is not None:
                        yield event
        except AgentProcessError as exc:
            yield AgentEvent(AgentEventKind.ERROR, str(exc))
