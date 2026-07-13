from app.services.tool_registry import build_default_registry


def test_registry_declares_face_tool_preconditions() -> None:
    registry = build_default_registry()
    face = registry.get("face_analysis")
    assert face is not None
    assert "has_face_frame" in face.preconditions
    assert face.requires_local_gpu is True
    assert face.failure_policy == "mark_unavailable"
