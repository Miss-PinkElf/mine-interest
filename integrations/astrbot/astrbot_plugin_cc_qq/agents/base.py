"""代理运行统一接口（Agent Runner Interface）。"""

from __future__ import annotations

from typing import AsyncIterator, Protocol

from ..contracts import AgentEvent, AgentRequest


class AgentAdapter(Protocol):
    agent_type: str

    def execute(self, request: AgentRequest) -> AsyncIterator[AgentEvent]:
        """将代理原生输出映射为统一事件。"""
        ...
