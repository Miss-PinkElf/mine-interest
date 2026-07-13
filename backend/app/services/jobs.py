"""JobService（任务服务）：创建、失败标记、查询与中断恢复。"""

from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from app.core import constants
from app.core.database import create_session_factory, session_scope
from app.domain.enums import JobStatus
from app.domain.models import Job
from app.repositories.jobs import JobRepository
from app.services.artifacts import ArtifactStore


class JobNotFoundError(KeyError):
    """当请求的任务标识不存在时抛出。"""


class JobService:
    """协调任务持久化与产物目录，保证失败不清理已完成产物。"""

    def __init__(
        self,
        artifact_store: ArtifactStore,
        database_path: Path | str | None = None,
        session_factory: sessionmaker[Session] | None = None,
    ) -> None:
        self._artifact_store = artifact_store
        if session_factory is not None:
            self._session_factory = session_factory
        else:
            db_path = (
                Path(database_path)
                if database_path is not None
                else artifact_store.root_dir / constants.JOB_SQLITE_FILENAME
            )
            self._session_factory = create_session_factory(db_path)

    def create(self, source_media_path: str) -> Job:
        """创建等待处理的任务，并预创建对应产物目录。"""
        job = Job.create(source_media_path=source_media_path)
        self._artifact_store.job_dir(job.id)
        with session_scope(self._session_factory) as session:
            JobRepository(session).save(job)
        return job

    def get(self, job_id: str) -> Job:
        """读取任务；不存在时抛出 JobNotFoundError。"""
        with session_scope(self._session_factory) as session:
            job = JobRepository(session).get(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job

    def mark_failed(
        self,
        job_id: str,
        stage: str,
        error_code: str,
        *,
        retryable: bool = constants.DEFAULT_FAILURE_RETRYABLE,
    ) -> Job:
        """标记任务失败并保留已有产物；不删除任何上游文件。"""
        with session_scope(self._session_factory) as session:
            repository = JobRepository(session)
            job = repository.get(job_id)
            if job is None:
                raise JobNotFoundError(job_id)
            job.mark_failed(stage=stage, error_code=error_code, retryable=retryable)
            repository.save(job)
            return job

    def mark_processing(self, job_id: str) -> Job:
        """将任务标记为处理中，供管线推进与恢复测试使用。"""
        with session_scope(self._session_factory) as session:
            repository = JobRepository(session)
            job = repository.get(job_id)
            if job is None:
                raise JobNotFoundError(job_id)
            job.mark_processing()
            repository.save(job)
            return job


    def create_from_upload(self, filename: str, content: bytes) -> Job:
        """根据上传字节创建任务，并把原始媒体写入任务产物目录。"""
        if not content:
            raise ValueError(constants.UPLOAD_ERROR_EMPTY_FILE)

        safe_name = Path(filename or constants.DEFAULT_UPLOAD_FILENAME).name
        if not safe_name:
            safe_name = constants.DEFAULT_UPLOAD_FILENAME

        job = Job.create(source_media_path=safe_name)
        relative_path = f"{constants.SOURCE_MEDIA_RELATIVE_DIR}/{safe_name}"
        stored_path = self._artifact_store.write_bytes(job.id, relative_path, content)
        job.source_media_path = str(stored_path)

        with session_scope(self._session_factory) as session:
            JobRepository(session).save(job)
        return job

    def mark_exported(self, job_id: str) -> Job:
        """将任务标记为已导出。"""
        with session_scope(self._session_factory) as session:
            repository = JobRepository(session)
            job = repository.get(job_id)
            if job is None:
                raise JobNotFoundError(job_id)
            job.mark_exported()
            repository.save(job)
            return job

    def recover_interrupted_jobs(self) -> list[Job]:
        """应用启动时将处理中任务转为可恢复失败，且不删除产物。"""
        recovered: list[Job] = []
        with session_scope(self._session_factory) as session:
            repository = JobRepository(session)
            interrupted_jobs = repository.list_by_status(JobStatus.PROCESSING)
            for job in interrupted_jobs:
                job.mark_failed(
                    stage=constants.JOB_FAILED_STAGE_INTERRUPTED,
                    error_code=constants.JOB_ERROR_CODE_INTERRUPTED,
                    retryable=constants.INTERRUPTED_FAILURE_RETRYABLE,
                )
                repository.save(job)
                recovered.append(job)
        return recovered
