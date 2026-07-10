"""审核链路的领域实体与不变量。"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.core import constants
from app.domain.enums import (
    AnalysisStatus,
    EvidenceAvailability,
    EvidenceSource,
    ExportFormat,
    JobStatus,
    ReviewOperationType,
    SegmentReviewStatus,
)


def _create_entity_id() -> str:
    """为尚未持久化的领域实体生成本地唯一标识。"""
    return str(uuid4())


def _current_time() -> datetime:
    """以 UTC 记录审计时间，避免本地时区影响持久化结果。"""
    return datetime.now(UTC)


@dataclass(slots=True)
class Job:
    """表示一次本地媒体处理任务。"""
    id: str
    source_media_path: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=_current_time)

    @classmethod
    def create(cls, source_media_path: str) -> "Job":
        """创建处于等待状态的新任务。"""
        return cls(id=_create_entity_id(), source_media_path=source_media_path)


@dataclass(slots=True)
class Segment:
    """表示可独立审核的时间轴片段。"""
    id: str
    raw_text: str
    start_seconds: float = constants.DEFAULT_SEGMENT_START_SECONDS
    end_seconds: float = constants.DEFAULT_SEGMENT_END_SECONDS
    speaker_id: str | None = None
    edited_text: str | None = None
    review_status: SegmentReviewStatus = SegmentReviewStatus.PENDING
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING

    @classmethod
    def create(
        cls,
        raw_text: str,
        start_seconds: float = constants.DEFAULT_SEGMENT_START_SECONDS,
        end_seconds: float = constants.DEFAULT_SEGMENT_END_SECONDS,
        speaker_id: str | None = None,
    ) -> "Segment":
        """由原始识别结果创建片段，人工字段保持为空。"""
        return cls(
            id=_create_entity_id(),
            raw_text=raw_text,
            start_seconds=start_seconds,
            end_seconds=end_seconds,
            speaker_id=speaker_id,
        )

    @property
    def final_text(self) -> str:
        """优先返回人工修订，未修订时回退到原始转写。"""
        return self.edited_text if self.edited_text is not None else self.raw_text

    def apply_text_edit(self, edited_text: str) -> None:
        """保存人工文本修订，且绝不覆盖模型原始转写。"""
        self.edited_text = edited_text


@dataclass(slots=True)
class Evidence:
    """保存某个片段的可追溯分析证据。"""
    id: str
    segment_id: str
    source: EvidenceSource
    kind: str
    payload: dict[str, Any]
    confidence: float = constants.DEFAULT_ENTITY_CONFIDENCE
    availability: EvidenceAvailability = EvidenceAvailability.AVAILABLE

    @classmethod
    def create(
        cls,
        segment_id: str,
        source: EvidenceSource,
        kind: str,
        payload: dict[str, Any],
    ) -> "Evidence":
        """创建默认可用的证据记录。"""
        return cls(
            id=_create_entity_id(),
            segment_id=segment_id,
            source=source,
            kind=kind,
            payload=payload,
        )


@dataclass(slots=True)
class ReviewOperation:
    """记录单个片段的人工审核操作。"""
    id: str
    segment_id: str
    operation_type: ReviewOperationType
    actor_id: str
    created_at: datetime = field(default_factory=_current_time)

    @classmethod
    def create(
        cls,
        segment_id: str,
        operation_type: ReviewOperationType,
        actor_id: str = constants.DEFAULT_LOCAL_USER_ID,
    ) -> "ReviewOperation":
        """以本地用户作为默认操作者创建审计记录。"""
        return cls(
            id=_create_entity_id(),
            segment_id=segment_id,
            operation_type=operation_type,
            actor_id=actor_id,
        )


@dataclass(slots=True)
class ExportArtifact:
    """描述任务已生成的导出文件。"""
    id: str
    job_id: str
    format: ExportFormat
    artifact_path: str
    created_at: datetime = field(default_factory=_current_time)

    @classmethod
    def create(
        cls,
        job_id: str,
        format: ExportFormat,
        artifact_path: str,
    ) -> "ExportArtifact":
        """创建指向本地产物路径的导出记录。"""
        return cls(
            id=_create_entity_id(),
            job_id=job_id,
            format=format,
            artifact_path=artifact_path,
        )
