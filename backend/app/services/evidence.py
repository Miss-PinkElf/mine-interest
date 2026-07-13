"""专用模型事实证据标准化。"""

from __future__ import annotations

from typing import Any

from app.domain.enums import EvidenceAvailability, EvidenceSource
from app.domain.models import Evidence
from app.services.orchestrator import PipelineResult


class EvidenceService:
    """把编排输出写成 Evidence，并区分专用事实与 LLM 叙事。"""

    def from_pipeline(self, segment_id: str, pipeline: PipelineResult) -> list[Evidence]:
        """从编排结果生成证据列表。"""
        items: list[Evidence] = []
        for tool_name, payload in pipeline.outputs.items():
            if tool_name == "cloud_fusion":
                continue
            source = (
                EvidenceSource.AUDIO_ANALYSIS
                if tool_name.startswith("audio_")
                else EvidenceSource.SPECIALIZED_MODEL
            )
            items.append(
                Evidence.create(
                    segment_id=segment_id,
                    source=source,
                    kind=tool_name,
                    payload=payload if isinstance(payload, dict) else {"value": payload},
                )
            )
        # 无人脸应表现为不可用，而不是失败。
        face_decisions = [
            entry for entry in pipeline.decision_log if entry.tool_name == "face_analysis"
        ]
        if face_decisions and not face_decisions[0].selected:
            unavailable = Evidence.create(
                segment_id=segment_id,
                source=EvidenceSource.SPECIALIZED_MODEL,
                kind="face_analysis",
                payload={"reason": face_decisions[0].reason},
            )
            unavailable.availability = EvidenceAvailability.UNAVAILABLE
            items.append(unavailable)
        return items
