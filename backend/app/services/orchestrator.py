"""确定性编排器：按条件选择工具并记录决策日志。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core import constants
from app.services.tool_registry import ToolRegistry, build_default_registry


@dataclass(slots=True)
class FrameManifest:
    """关键帧清单，供人脸/姿态工具前置判断。"""

    has_face: bool = False
    has_person: bool = False
    frame_paths: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PipelineContext:
    """编排上下文。"""

    has_audio: bool = True
    multi_speaker: bool = False
    low_quality: bool = False
    needs_semantic_interpretation: bool = True
    frame_manifest: FrameManifest = field(default_factory=FrameManifest)


@dataclass(slots=True)
class DecisionLogEntry:
    """单次工具选择/跳过决策。"""

    tool_name: str
    selected: bool
    reason: str


@dataclass(slots=True)
class PipelineResult:
    """编排结果。"""

    called_tools: list[str]
    decision_log: list[DecisionLogEntry]
    outputs: dict[str, Any] = field(default_factory=dict)


def run_pipeline(
    registry: ToolRegistry | None = None,
    *,
    frame_manifest: FrameManifest | None = None,
    context: PipelineContext | None = None,
) -> PipelineResult:
    """按前置条件确定性选择工具，不让 LLM 决定文件处理。"""
    registry = registry or build_default_registry()
    context = context or PipelineContext(frame_manifest=frame_manifest or FrameManifest())
    if frame_manifest is not None:
        context.frame_manifest = frame_manifest

    called: list[str] = []
    logs: list[DecisionLogEntry] = []
    outputs: dict[str, Any] = {}

    face_tool = registry.get("face_analysis")
    if face_tool is not None:
        if context.frame_manifest.has_face:
            called.append(face_tool.name)
            logs.append(DecisionLogEntry(face_tool.name, True, "HAS_FACE_FRAME"))
            outputs[face_tool.name] = {"faces": [{"bbox": [0, 0, 1, 1]}]}
        else:
            logs.append(
                DecisionLogEntry(
                    face_tool.name,
                    False,
                    constants.TOOL_SKIP_REASON_NO_FACE_FRAME,
                )
            )

    audio_tool = registry.get("audio_emotion")
    if audio_tool is not None:
        if context.has_audio:
            called.append(audio_tool.name)
            logs.append(DecisionLogEntry(audio_tool.name, True, "HAS_AUDIO"))
            outputs[audio_tool.name] = {"emotion": "neutral", "source": "specialized_model"}
        else:
            logs.append(DecisionLogEntry(audio_tool.name, False, "NO_AUDIO"))

    pose_tool = registry.get("pose_analysis")
    if pose_tool is not None:
        if context.frame_manifest.has_person:
            called.append(pose_tool.name)
            logs.append(DecisionLogEntry(pose_tool.name, True, "HAS_PERSON_FRAME"))
            outputs[pose_tool.name] = {"pose": {"keypoints": []}}
        else:
            logs.append(DecisionLogEntry(pose_tool.name, False, "NO_PERSON_FRAME"))

    fusion_tool = registry.get("cloud_fusion")
    if fusion_tool is not None:
        if context.needs_semantic_interpretation:
            called.append(fusion_tool.name)
            logs.append(DecisionLogEntry(fusion_tool.name, True, "NEEDS_SEMANTIC"))
        else:
            logs.append(DecisionLogEntry(fusion_tool.name, False, "NO_SEMANTIC_NEED"))

    if context.low_quality:
        logs.append(DecisionLogEntry("quality_gate", True, "LOW_QUALITY_BRANCH"))
    if context.multi_speaker:
        logs.append(DecisionLogEntry("diarization_priority", True, "MULTI_SPEAKER_BRANCH"))

    return PipelineResult(called_tools=called, decision_log=logs, outputs=outputs)
