"""Codex CLI JSON Lines 事件适配（Codex CLI Adapter）。"""

from __future__ import annotations

import json
from contextlib import aclosing
from typing import AsyncIterator, Optional

from ..constants import CODEX_COMMAND, CODEX_DEFAULT_ACCESS_FLAG
from ..contracts import AgentEvent, AgentEventKind, AgentRequest
from .process import AgentProcessError, ProcessRunner


CODEX_BASE_ARGS = ("--skip-git-repo-check", CODEX_DEFAULT_ACCESS_FLAG, "--json")


def parse_codex_event(line: str) -> Optional[AgentEvent]:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None

    event_type = payload.get("type")
    if event_type == "thread.started" and payload.get("thread_id"):
        return AgentEvent(
            AgentEventKind.STARTED, agent_session_id=str(payload["thread_id"])
        )

    if event_type == "item.completed":
        item = payload.get("item") or {}
        if not isinstance(item, dict):
            return None
        if item.get("type") == "agent_message" and item.get("text"):
            return AgentEvent(AgentEventKind.TEXT, str(item["text"]))
        if item.get("type") == "message" and item.get("role") == "assistant":
            content = item.get("content") or []
            text_parts = [
                str(block.get("text"))
                for block in content
                if isinstance(block, dict) and block.get("type") == "output_text" and block.get("text")
            ] if isinstance(content, list) else []
            if text_parts:
                return AgentEvent(AgentEventKind.TEXT, "\n".join(text_parts))

    if event_type == "turn.completed":
        return AgentEvent(AgentEventKind.DONE)
    if event_type in ("turn.failed", "error"):
        return AgentEvent(AgentEventKind.ERROR, "Codex 返回执行错误")
    return None


class CodexAdapter:
    agent_type = "codex"

    def __init__(self, process_runner: ProcessRunner, command: str = CODEX_COMMAND):
        self._process_runner = process_runner
        self._command = command

    async def execute(self, request: AgentRequest) -> AsyncIterator[AgentEvent]:
        args = ["exec"]
        if request.agent_session_id:
            args.append("resume")
        args.extend(CODEX_BASE_ARGS)
        if request.model:
            args.extend(("--model", request.model))
        if request.agent_session_id:
            args.extend((request.agent_session_id, "-"))
        else:
            args.extend(("--cd", request.work_dir, "-"))

        try:
            async with aclosing(self._process_runner.run(
                request.conversation.storage_key(), self._command, args,
                request.work_dir, request.message,
            )) as lines:
                async for line in lines:
                    event = parse_codex_event(line)
                    if event is not None:
                        yield event
        except AgentProcessError as exc:
            yield AgentEvent(AgentEventKind.ERROR, str(exc))
