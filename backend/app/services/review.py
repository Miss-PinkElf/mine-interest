"""审核服务：确认、切分、合并、删除与文本/角色修改。"""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from app.core.database import session_scope
from app.domain.enums import AnalysisStatus
from app.domain.models import Segment
from app.repositories.segments import SegmentRepository
from app.repositories.tables import SegmentRow


class SegmentNotFoundError(KeyError):
    """当片段标识不存在时抛出。"""


class ReviewOperationError(ValueError):
    """当审核操作不满足业务约束时抛出。"""


class ReviewService:
    """处理不依赖云端模型的本地审核写操作。"""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def confirm_segment(self, segment_id: str) -> Segment:
        """将片段标记为已确认并持久化。"""
        with session_scope(self._session_factory) as session:
            repository = SegmentRepository(session)
            segment = self._require_segment(repository, segment_id)
            job_id = self._require_job_id(repository, segment_id)
            segment.confirm()
            repository.save(job_id, segment)
            return segment

    def list_segments(self, job_id: str) -> list[Segment]:
        """列出任务下全部片段，按开始时间排序。"""
        with session_scope(self._session_factory) as session:
            segments = SegmentRepository(session).list_by_job(job_id)
        return sorted(segments, key=lambda item: item.start_seconds)

    def add_segment(self, job_id: str, segment: Segment) -> Segment:
        """为任务追加片段，供测试与后续管线写入。"""
        with session_scope(self._session_factory) as session:
            return SegmentRepository(session).save(job_id, segment)

    def apply_text_edit(self, segment_id: str, edited_text: str) -> Segment:
        """修改片段文本并标记分析失效。"""
        with session_scope(self._session_factory) as session:
            repository = SegmentRepository(session)
            segment = self._require_segment(repository, segment_id)
            job_id = self._require_job_id(repository, segment_id)
            segment.apply_text_edit(edited_text)
            segment.mark_analysis_stale()
            repository.save(job_id, segment)
            return segment

    def apply_speaker_edit(self, segment_id: str, speaker_id: str) -> Segment:
        """修改说话人。"""
        with session_scope(self._session_factory) as session:
            repository = SegmentRepository(session)
            segment = self._require_segment(repository, segment_id)
            job_id = self._require_job_id(repository, segment_id)
            segment.apply_speaker_edit(speaker_id)
            repository.save(job_id, segment)
            return segment

    def split_segment(self, segment_id: str, at_seconds: float) -> list[Segment]:
        """在时间点切分片段，仅失效受影响片段。"""
        with session_scope(self._session_factory) as session:
            repository = SegmentRepository(session)
            segment = self._require_segment(repository, segment_id)
            job_id = self._require_job_id(repository, segment_id)
            if not (segment.start_seconds < at_seconds < segment.end_seconds):
                raise ReviewOperationError("SPLIT_POINT_OUT_OF_RANGE")

            left = Segment.create(
                raw_text=segment.raw_text,
                start_seconds=segment.start_seconds,
                end_seconds=at_seconds,
                speaker_id=segment.speaker_id,
            )
            left.edited_text = segment.edited_text
            left.analysis_status = AnalysisStatus.STALE

            right = Segment.create(
                raw_text=segment.raw_text,
                start_seconds=at_seconds,
                end_seconds=segment.end_seconds,
                speaker_id=segment.speaker_id,
            )
            right.edited_text = segment.edited_text
            right.analysis_status = AnalysisStatus.STALE

            row = session.get(SegmentRow, segment_id)
            if row is not None:
                session.delete(row)
                session.flush()
            repository.save(job_id, left)
            repository.save(job_id, right)
            return [left, right]

    def merge_adjacent(self, left_segment_id: str, right_segment_id: str) -> Segment:
        """合并相邻片段。"""
        with session_scope(self._session_factory) as session:
            repository = SegmentRepository(session)
            left = self._require_segment(repository, left_segment_id)
            right = self._require_segment(repository, right_segment_id)
            job_id = self._require_job_id(repository, left_segment_id)
            right_job = self._require_job_id(repository, right_segment_id)
            if job_id != right_job:
                raise ReviewOperationError("SEGMENTS_NOT_SAME_JOB")
            if abs(left.end_seconds - right.start_seconds) > 1e-6:
                raise ReviewOperationError("SEGMENTS_NOT_ADJACENT")

            merged = Segment.create(
                raw_text=f"{left.raw_text}{right.raw_text}",
                start_seconds=left.start_seconds,
                end_seconds=right.end_seconds,
                speaker_id=left.speaker_id,
            )
            if left.edited_text is not None or right.edited_text is not None:
                merged.edited_text = f"{left.final_text}{right.final_text}"
            merged.analysis_status = AnalysisStatus.STALE

            for segment_id in (left_segment_id, right_segment_id):
                row = session.get(SegmentRow, segment_id)
                if row is not None:
                    session.delete(row)
            session.flush()
            repository.save(job_id, merged)
            return merged

    def delete_segment(self, segment_id: str) -> None:
        """删除无效片段。"""
        with session_scope(self._session_factory) as session:
            repository = SegmentRepository(session)
            self._require_segment(repository, segment_id)
            row = session.get(SegmentRow, segment_id)
            if row is not None:
                session.delete(row)

    @staticmethod
    def _require_segment(repository: SegmentRepository, segment_id: str) -> Segment:
        segment = repository.get(segment_id)
        if segment is None:
            raise SegmentNotFoundError(segment_id)
        return segment

    @staticmethod
    def _require_job_id(repository: SegmentRepository, segment_id: str) -> str:
        job_id = repository.get_job_id(segment_id)
        if job_id is None:
            raise SegmentNotFoundError(segment_id)
        return job_id
