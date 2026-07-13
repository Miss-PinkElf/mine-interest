"""审核服务：片段确认等本地人工操作。"""

from sqlalchemy.orm import Session, sessionmaker

from app.core.database import session_scope
from app.domain.models import Segment
from app.repositories.segments import SegmentRepository


class SegmentNotFoundError(KeyError):
    """当片段标识不存在时抛出。"""


class ReviewService:
    """处理不依赖云端模型的本地审核写操作。"""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def confirm_segment(self, segment_id: str) -> Segment:
        """将片段标记为已确认并持久化。"""
        with session_scope(self._session_factory) as session:
            repository = SegmentRepository(session)
            segment = repository.get(segment_id)
            if segment is None:
                raise SegmentNotFoundError(segment_id)
            job_id = repository.get_job_id(segment_id)
            if job_id is None:
                raise SegmentNotFoundError(segment_id)
            segment.confirm()
            repository.save(job_id, segment)
            return segment

    def list_segments(self, job_id: str) -> list[Segment]:
        """列出任务下全部片段。"""
        with session_scope(self._session_factory) as session:
            return SegmentRepository(session).list_by_job(job_id)

    def add_segment(self, job_id: str, segment: Segment) -> Segment:
        """为任务追加片段，供测试与后续管线写入。"""
        with session_scope(self._session_factory) as session:
            return SegmentRepository(session).save(job_id, segment)
