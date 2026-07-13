from pathlib import Path

from app.core import constants
from app.domain.enums import JobStatus
from app.services.artifacts import ArtifactStore
from app.services.jobs import JobService


# 失败场景中写入的质量报告相对路径，用于验证产物不被清理。
QUALITY_REPORT_RELATIVE_PATH = f"{constants.QUALITY_REPORT_RELATIVE_DIR}/report.json"
# 质量报告占位内容，仅用于存在性断言。
QUALITY_REPORT_CONTENT = "{}"


def test_failed_job_keeps_completed_artifacts(tmp_path: Path) -> None:
    artifact_store = ArtifactStore(tmp_path)
    job_service = JobService(artifact_store)
    job = job_service.create(source_media_path="sample.mp4")

    artifact_store.write_text(job.id, QUALITY_REPORT_RELATIVE_PATH, QUALITY_REPORT_CONTENT)
    job_service.mark_failed(
        job.id,
        stage="transcription",
        error_code="MODEL_UNAVAILABLE",
    )

    assert artifact_store.exists(job.id, QUALITY_REPORT_RELATIVE_PATH)
    failed_job = job_service.get(job.id)
    assert failed_job.status == JobStatus.FAILED
    assert failed_job.failed_stage == "transcription"
    assert failed_job.error_code == "MODEL_UNAVAILABLE"


def test_restart_recovers_interrupted_job_without_deleting_artifacts(
    tmp_path: Path,
) -> None:
    artifact_store = ArtifactStore(tmp_path)
    job_service = JobService(artifact_store)
    job = job_service.create(source_media_path="sample.mp4")
    artifact_store.write_text(job.id, QUALITY_REPORT_RELATIVE_PATH, QUALITY_REPORT_CONTENT)
    job_service.mark_processing(job.id)

    # 模拟应用重启：使用同一产物根与 SQLite 重新构建服务。
    restarted_service = JobService(ArtifactStore(tmp_path))
    recovered = restarted_service.recover_interrupted_jobs()

    assert len(recovered) == 1
    assert recovered[0].id == job.id
    restored = restarted_service.get(job.id)
    assert restored.status == JobStatus.FAILED
    assert restored.error_code == constants.JOB_ERROR_CODE_INTERRUPTED
    assert restored.retryable is True
    assert artifact_store.exists(job.id, QUALITY_REPORT_RELATIVE_PATH)
