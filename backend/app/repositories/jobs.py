"""任务仓储：在 SQLite 中读写 Job 生命周期状态。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import JobStatus
from app.domain.models import Job
from app.repositories.tables import JobRow


class JobRepository:
    """封装任务实体与 SQLite 行之间的映射。"""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, job: Job) -> Job:
        """插入或更新任务记录。"""
        row = self._session.get(JobRow, job.id)
        if row is None:
            row = JobRow(id=job.id)
            self._session.add(row)
        self._apply_domain_to_row(job, row)
        self._session.flush()
        return job

    def get(self, job_id: str) -> Job | None:
        """按标识读取任务；不存在时返回 None。"""
        row = self._session.get(JobRow, job_id)
        if row is None:
            return None
        return self._to_domain(row)

    def list_by_status(self, status: JobStatus) -> list[Job]:
        """按状态列出任务，供启动恢复扫描使用。"""
        statement = select(JobRow).where(JobRow.status == status.value)
        rows = self._session.scalars(statement).all()
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _apply_domain_to_row(job: Job, row: JobRow) -> None:
        """将领域对象字段同步到持久化行。"""
        row.source_media_path = job.source_media_path
        row.status = job.status.value
        row.created_at = job.created_at
        row.failed_stage = job.failed_stage
        row.error_code = job.error_code
        row.retryable = job.retryable
        row.failed_at = job.failed_at
        row.updated_at = job.updated_at

    @staticmethod
    def _to_domain(row: JobRow) -> Job:
        """将持久化行还原为领域任务对象。"""
        return Job(
            id=row.id,
            source_media_path=row.source_media_path,
            status=JobStatus(row.status),
            created_at=row.created_at,
            failed_stage=row.failed_stage,
            error_code=row.error_code,
            retryable=row.retryable,
            failed_at=row.failed_at,
            updated_at=row.updated_at,
        )
