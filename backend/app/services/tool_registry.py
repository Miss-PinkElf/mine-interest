"""工具注册表：声明工具 schema、前置条件与失败策略。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True)
class ToolMetadata:
    """单个工具的可观测元数据。"""

    name: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    preconditions: list[str]
    run_location: str
    requires_local_gpu: bool
    artifact_path_template: str
    failure_policy: str
    handler: Callable[..., Any] | None = None


class ToolRegistry:
    """集中登记本地/云端工具，供编排器查询。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolMetadata] = {}

    def register(self, metadata: ToolMetadata) -> None:
        """注册工具元数据。"""
        self._tools[metadata.name] = metadata

    def get(self, name: str) -> ToolMetadata | None:
        """按名称获取工具。"""
        return self._tools.get(name)

    def list_tools(self) -> list[ToolMetadata]:
        """列出全部工具。"""
        return list(self._tools.values())


def build_default_registry() -> ToolRegistry:
    """构建第一版默认工具集合（处理器可后续替换为真实模型）。"""
    registry = ToolRegistry()
    registry.register(
        ToolMetadata(
            name="face_analysis",
            input_schema={"frames": "list[str]"},
            output_schema={"faces": "list"},
            preconditions=["has_face_frame"],
            run_location="local",
            requires_local_gpu=True,
            artifact_path_template="evidence/{segment_id}/face.json",
            failure_policy="mark_unavailable",
        )
    )
    registry.register(
        ToolMetadata(
            name="audio_emotion",
            input_schema={"audio_path": "str"},
            output_schema={"emotion": "str"},
            preconditions=["has_audio"],
            run_location="local",
            requires_local_gpu=False,
            artifact_path_template="evidence/{segment_id}/audio_emotion.json",
            failure_policy="mark_failed",
        )
    )
    registry.register(
        ToolMetadata(
            name="pose_analysis",
            input_schema={"frames": "list[str]"},
            output_schema={"pose": "object"},
            preconditions=["has_person_frame"],
            run_location="local",
            requires_local_gpu=True,
            artifact_path_template="evidence/{segment_id}/pose.json",
            failure_policy="mark_unavailable",
        )
    )
    registry.register(
        ToolMetadata(
            name="cloud_fusion",
            input_schema={"evidence_ids": "list[str]", "text": "str"},
            output_schema={"conclusion": "str"},
            preconditions=["needs_semantic_interpretation"],
            run_location="cloud",
            requires_local_gpu=False,
            artifact_path_template="evidence/{segment_id}/fusion.json",
            failure_policy="retry_segment",
        )
    )
    return registry
