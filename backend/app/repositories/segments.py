"""片段仓储：为后续审核链路预留 SQLite 读写能力。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import AnalysisStatus, SegmentReviewStatus
from app.domain.models import Segment
from app.repositories.tables import SegmentRow


class SegmentRepository:
    """封装片段实体与 SQLite 行之间的映射。"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, job_id: str, segment: Segment) -> Segment:
        """插入或更新指定任务下的片段。"""
        row = self._session.get(SegmentRow, segment.id)
        if row is None:
            row = SegmentRow(id=segment.id)
            self._session.add(row)
        row.job_id = job_id
        row.raw_text = segment.raw_text
        row.edited_text = segment.edited_text
        row.start_seconds = segment.start_seconds
        row.end_seconds = segment.end_seconds
        row.speaker_id = segment.speaker_id
        row.review_status = segment.review_status.value
        row.analysis_status = segment.analysis_status.value
        self._session.flush()
        return segment

    def list_by_job(self, job_id: str) -> list[Segment]:
        """列出某任务下全部片段。"""
        statement = select(SegmentRow).where(SegmentRow.job_id == job_id)
        rows = self._session.scalars(statement).all()
        return [self._to_domain(row) for row in rows]

    def get(self, segment_id: str) -> Segment | None:
        """按标识读取片段；不存在时返回 None。"""
        row = self._session.get(SegmentRow, segment_id)
        if row is None:
            return None
        return self._to_domain(row)

    def get_job_id(self, segment_id: str) -> str | None:
        """返回片段所属任务标识；不存在时返回 None。"""
        row = self._session.get(SegmentRow, segment_id)
        if row is None:
            return None
        return row.job_id

    @staticmethod
    def _to_domain(row: SegmentRow) -> Segment:
        """将持久化行还原为领域片段对象。"""
        return Segment(
            id=row.id,
            raw_text=row.raw_text,
            start_seconds=row.start_seconds,
            end_seconds=row.end_seconds,
            speaker_id=row.speaker_id,
            edited_text=row.edited_text,
            review_status=SegmentReviewStatus(row.review_status),
            analysis_status=AnalysisStatus(row.analysis_status),
        )
