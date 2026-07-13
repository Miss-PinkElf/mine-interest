from app.domain.enums import EvidenceSource
from app.domain.models import Evidence
from app.services.fusion import FusionService


def test_fusion_request_keeps_local_evidence_and_flags_conflict() -> None:
    specialized = [
        Evidence.create(
            segment_id="seg-1",
            source=EvidenceSource.SPECIALIZED_MODEL,
            kind="audio_emotion",
            payload={"emotion": "neutral"},
        )
    ]
    # 固化专用证据 id，便于断言引用。
    original_ids = [item.id for item in specialized]
    result = FusionService().fuse_segment(
        segment_id="seg-1",
        text="这明显是反讽吧",
        specialized_evidence=specialized,
    )
    assert result.llm_evidence.source == EvidenceSource.LLM
    assert specialized[0].id == original_ids[0]
    assert result.response.requires_human_review is True
    assert result.response.evidence_ids
