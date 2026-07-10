"""领域状态的类型安全枚举。"""

from enum import Enum

from app.core import constants


class JobStatus(str, Enum):
    PENDING = constants.JOB_STATUS_PENDING
    PROCESSING = constants.JOB_STATUS_PROCESSING
    REVIEW = constants.JOB_STATUS_REVIEW
    CONFIRMED = constants.JOB_STATUS_CONFIRMED
    EXPORTED = constants.JOB_STATUS_EXPORTED
    FAILED = constants.JOB_STATUS_FAILED


class SegmentReviewStatus(str, Enum):
    PENDING = constants.SEGMENT_REVIEW_STATUS_PENDING
    CONFIRMED = constants.SEGMENT_REVIEW_STATUS_CONFIRMED


class AnalysisStatus(str, Enum):
    PENDING = constants.ANALYSIS_STATUS_PENDING
    CURRENT = constants.ANALYSIS_STATUS_CURRENT
    STALE = constants.ANALYSIS_STATUS_STALE
    FAILED = constants.ANALYSIS_STATUS_FAILED


class EvidenceSource(str, Enum):
    SPECIALIZED_MODEL = constants.EVIDENCE_SOURCE_SPECIALIZED_MODEL
    AUDIO_ANALYSIS = constants.EVIDENCE_SOURCE_AUDIO_ANALYSIS
    OCR = constants.EVIDENCE_SOURCE_OCR
    LLM = constants.EVIDENCE_SOURCE_LLM
    HUMAN_REVIEW = constants.EVIDENCE_SOURCE_HUMAN_REVIEW


class EvidenceAvailability(str, Enum):
    AVAILABLE = constants.EVIDENCE_AVAILABILITY_AVAILABLE
    UNAVAILABLE = constants.EVIDENCE_AVAILABILITY_UNAVAILABLE
    FAILED = constants.EVIDENCE_AVAILABILITY_FAILED


class ReviewOperationType(str, Enum):
    TEXT_EDIT = constants.REVIEW_OPERATION_TEXT_EDIT
    SPEAKER_EDIT = constants.REVIEW_OPERATION_SPEAKER_EDIT
    SPLIT = constants.REVIEW_OPERATION_SPLIT
    MERGE = constants.REVIEW_OPERATION_MERGE
    DELETE = constants.REVIEW_OPERATION_DELETE
    CONFIRM = constants.REVIEW_OPERATION_CONFIRM


class ExportFormat(str, Enum):
    JSON = constants.EXPORT_FORMAT_JSON
    MARKDOWN = constants.EXPORT_FORMAT_MARKDOWN
