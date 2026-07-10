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
    return str(uuid4())


def _current_time() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Job:
    id: str
    source_media_path: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=_current_time)

    @classmethod
    def create(cls, source_media_path: str) -> "Job":
        return cls(id=_create_entity_id(), source_media_path=source_media_path)


@dataclass(slots=True)
class Segment:
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
        return cls(
            id=_create_entity_id(),
            raw_text=raw_text,
            start_seconds=start_seconds,
            end_seconds=end_seconds,
            speaker_id=speaker_id,
        )

    @property
    def final_text(self) -> str:
        return self.edited_text if self.edited_text is not None else self.raw_text

    def apply_text_edit(self, edited_text: str) -> None:
        self.edited_text = edited_text


@dataclass(slots=True)
class Evidence:
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
        return cls(
            id=_create_entity_id(),
            segment_id=segment_id,
            source=source,
            kind=kind,
            payload=payload,
        )


@dataclass(slots=True)
class ReviewOperation:
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
        return cls(
            id=_create_entity_id(),
            segment_id=segment_id,
            operation_type=operation_type,
            actor_id=actor_id,
        )


@dataclass(slots=True)
class ExportArtifact:
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
        return cls(
            id=_create_entity_id(),
            job_id=job_id,
            format=format,
            artifact_path=artifact_path,
        )
