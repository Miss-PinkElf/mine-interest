from app.core import constants
from app.services.orchestrator import FrameManifest, PipelineContext, run_pipeline
from app.services.tool_registry import build_default_registry


def test_orchestrator_only_calls_face_tool_when_face_frames_exist() -> None:
    registry = build_default_registry()
    result = run_pipeline(registry, frame_manifest=FrameManifest(has_face=False))
    assert "face_analysis" not in result.called_tools
    assert result.decision_log[0].reason == constants.TOOL_SKIP_REASON_NO_FACE_FRAME


def test_orchestrator_branches_for_low_quality_and_multi_speaker() -> None:
    result = run_pipeline(
        context=PipelineContext(
            low_quality=True,
            multi_speaker=True,
            frame_manifest=FrameManifest(has_face=True, has_person=True),
        )
    )
    assert "face_analysis" in result.called_tools
    reasons = {entry.reason for entry in result.decision_log}
    assert "LOW_QUALITY_BRANCH" in reasons
    assert "MULTI_SPEAKER_BRANCH" in reasons
