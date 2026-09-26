"""演示任务执行器：串联现有本地适配层与审核片段持久化。"""

import json

from app.core import constants
from app.domain.enums import JobStatus
from app.services.artifacts import ArtifactStore
from app.services.jobs import JobService
from app.services.media import MediaService
from app.services.preprocess import PreprocessService
from app.services.review import ReviewService
from app.services.transcription import TranscriptionService


class JobRunner:
    """执行单个演示任务；失败时保留已有产物并写入稳定错误码。"""

    def __init__(
        self,
        job_service: JobService,
        review_service: ReviewService,
        artifact_store: ArtifactStore,
        transcription_service: TranscriptionService,
        media_service: MediaService | None = None,
    ) -> None:
        self._jobs = job_service
        self._review = review_service
        self._artifacts = artifact_store
        self._transcription = transcription_service
        self._media = media_service or MediaService()
        self._preprocess = PreprocessService(artifact_store)

    def run(self, job_id: str) -> None:
        """把等待中的演示任务推进到待审核或失败，避免重复写片段。"""
        job = self._jobs.get(job_id)
        if job.status != JobStatus.PENDING:
            return
        if not job.is_demo:
            raise ValueError(constants.JOB_ERROR_RUNNER_NOT_DEMO)

        stage = constants.JOB_STAGE_MEDIA
        self._jobs.mark_processing(job_id)
        try:
            report = self._media.build_quality_report(job.source_media_path)
            self._artifacts.write_text(
                job_id,
                constants.QUALITY_REPORT_RELATIVE_PATH,
                json.dumps(report.to_dict(), ensure_ascii=False),
            )

            stage = constants.JOB_STAGE_PREPROCESS
            self._preprocess.run(job_id, job.source_media_path, report)

            stage = constants.JOB_STAGE_TRANSCRIPTION
            segments = self._transcription.run(job.source_media_path)
            if not segments:
                self._jobs.mark_failed(
                    job_id,
                    stage=stage,
                    error_code=constants.JOB_ERROR_CODE_NO_SEGMENTS,
                )
                return

            stage = constants.JOB_STAGE_SEGMENTS
            for segment in segments:
                self._review.add_segment(job_id, segment)
            self._jobs.mark_review(job_id)
        except Exception:
            # 后台任务不会把异常返回给上传请求，失败原因以稳定状态查询。
            self._jobs.mark_failed(
                job_id,
                stage=stage,
                error_code=constants.JOB_ERROR_CODE_PIPELINE_FAILED,
            )
