"""专用模型优先的证据融合与云端失败重试。"""

from __future__ import annotations

from dataclasses import dataclass

from app.core import constants
from app.domain.enums import EvidenceSource
from app.domain.models import Evidence
from app.integrations.llm.base import FusionRequest, FusionResponse, LlmProvider
from app.integrations.llm.openai_compatible import OpenAICompatibleProvider


@dataclass(slots=True)
class FusionResult:
    """融合结果及是否触发人工审核。"""

    response: FusionResponse
    llm_evidence: Evidence
    attempts: int


class FusionService:
    """融合服务：失败可重试，不覆盖本地专用证据。"""

    def __init__(
        self,
        provider: LlmProvider | None = None,
        max_retries: int = constants.DEFAULT_FUSION_MAX_RETRIES,
    ) -> None:
        self._provider = provider or OpenAICompatibleProvider(
            base_url="",
            model_name="local-fallback",
            api_key="",
        )
        self._max_retries = max_retries

    def fuse_segment(
        self,
        *,
        segment_id: str,
        text: str,
        specialized_evidence: list[Evidence],
        frame_refs: list[str] | None = None,
    ) -> FusionResult:
        """执行融合；网络失败时重试，不修改专用证据列表。"""
        request = FusionRequest(
            segment_id=segment_id,
            text=text,
            evidence_summaries=[
                {
                    "id": item.id,
                    "kind": item.kind,
                    "source": item.source.value,
                    "payload": item.payload,
                }
                for item in specialized_evidence
            ],
            frame_refs=frame_refs or [],
        )
        # 确保请求不含原媒体绝对路径字段。
        assert not hasattr(request, "source_media_path")

        attempts = 0
        last_error: Exception | None = None
        while attempts <= self._max_retries:
            attempts += 1
            try:
                response = self._provider.fuse(request)
                llm_evidence = Evidence.create(
                    segment_id=segment_id,
                    source=EvidenceSource.LLM,
                    kind="semantic_interpretation",
                    payload={
                        "conclusion": response.conclusion,
                        "confidence": response.confidence,
                        "uncertainty": response.uncertainty,
                        "evidence_ids": response.evidence_ids,
                        "conflicts": response.conflicts,
                        "requires_human_review": response.requires_human_review,
                    },
                )
                return FusionResult(
                    response=response,
                    llm_evidence=llm_evidence,
                    attempts=attempts,
                )
            except Exception as error:  # noqa: BLE001 - 云端失败需捕获后重试
                last_error = error
                continue
        raise RuntimeError(f"FUSION_FAILED_AFTER_RETRIES:{last_error}")
