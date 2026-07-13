"""云端 Provider 协议。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class FusionRequest:
    """受限的证据融合请求，不含原媒体路径。"""

    segment_id: str
    text: str
    evidence_summaries: list[dict[str, Any]]
    frame_refs: list[str]


@dataclass(slots=True)
class FusionResponse:
    """结构化融合输出。"""

    conclusion: str
    confidence: float
    uncertainty: str
    evidence_ids: list[str]
    conflicts: list[str]
    requires_human_review: bool


class LlmProvider(Protocol):
    """OpenAI-compatible 等云端提供方适配协议。"""

    def fuse(self, request: FusionRequest) -> FusionResponse:
        """执行证据融合。"""
