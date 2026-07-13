from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.domain.enums import (
    AnalysisStatus,
    EvidenceAvailability,
    EvidenceSource,
    ExportFormat,
    JobStatus,
    ReviewOperationType,
    SegmentReviewStatus,
)


class JobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_media_path: str
    status: JobStatus
    created_at: datetime
    failed_stage: str | None = None
    error_code: str | None = None
    retryable: bool = False
    failed_at: datetime | None = None
    updated_at: datetime | None = None


class SegmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    raw_text: str
    edited_text: str | None
    final_text: str
    start_seconds: float
    end_seconds: float
    speaker_id: str | None
    review_status: SegmentReviewStatus
    analysis_status: AnalysisStatus


class EvidenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    segment_id: str
    source: EvidenceSource
    kind: str
    payload: dict[str, Any]
    confidence: float
    availability: EvidenceAvailability


class ReviewOperationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    segment_id: str
    operation_type: ReviewOperationType
    actor_id: str
    created_at: datetime


class ExportArtifactSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    format: ExportFormat
    artifact_path: str
    created_at: datetime


class ExportRequestSchema(BaseModel):
    """创建导出任务时的请求体。"""

    format: ExportFormat

