from app.domain.enums import JobStatus
from app.services.artifacts import ArtifactStore
from app.services.jobs import JobService


def test_failed_job_keeps_completed_artifacts(tmp_path) -> None:
    artifact_store = ArtifactStore(tmp_path)
    job_service = JobService(artifact_store)
    job = job_service.create(source_media_path="sample.mp4")

    artifact_store.write_text(job.id, "quality/report.json", "{}")
    job_service.mark_failed(
        job.id,
        stage="transcription",
        error_code="MODEL_UNAVAILABLE",
    )

    assert artifact_store.exists(job.id, "quality/report.json")
    assert job_service.get(job.id).status == JobStatus.FAILED
