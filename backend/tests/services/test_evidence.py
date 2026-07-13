from app.domain.enums import EvidenceAvailability, EvidenceSource
from app.services.evidence import EvidenceService
from app.services.orchestrator import FrameManifest, run_pipeline


def test_specialized_facts_separated_and_no_face_is_unavailable() -> None:
    pipeline = run_pipeline(frame_manifest=FrameManifest(has_face=False))
    evidence = EvidenceService().from_pipeline("seg-1", pipeline)
    kinds = {item.kind for item in evidence}
    assert "audio_emotion" in kinds or any(
        item.source == EvidenceSource.AUDIO_ANALYSIS for item in evidence
    )
    face = next(item for item in evidence if item.kind == "face_analysis")
    assert face.availability == EvidenceAvailability.UNAVAILABLE
    assert face.source != EvidenceSource.LLM
