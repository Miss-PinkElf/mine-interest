"""自动演示任务的状态、失败和来源持久化测试。"""

import json
from pathlib import Path

from app.api.runtime import build_runtime
from app.core import constants
from app.domain.enums import ExportFormat, JobStatus
from app.services.job_runner import JobRunner
from app.services.transcription import TranscriptionResult, TranscriptionService


class EmptyEngine:
    """模拟 STT 未识别到任何片段。"""

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        return TranscriptionResult(words=[], raw_engine_payload={})


class FailingEngine:
    """模拟转写引擎执行失败。"""

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        raise RuntimeError("engine unavailable")


def test_demo_job_runs_to_review_and_keeps_source_after_restart(tmp_path: Path) -> None:
    runtime = build_runtime(tmp_path)
    job = runtime.job_service.create_from_upload(
        "sample.mp4", b"fake-media", demo_mode=True
    )

    runtime.job_runner.run(job.id)

    finished = runtime.job_service.get(job.id)
    assert finished.status == JobStatus.REVIEW
    assert finished.is_demo is True
    assert len(runtime.review_service.list_segments(job.id)) == 1
    assert runtime.artifact_store.exists(job.id, constants.QUALITY_REPORT_RELATIVE_PATH)

    restarted = build_runtime(tmp_path)
    assert restarted.job_service.get(job.id).is_demo is True
    segment = restarted.review_service.list_segments(job.id)[0]
    restarted.review_service.confirm_segment(segment.id)
    for export_format in (ExportFormat.MARKDOWN, ExportFormat.JSON):
        artifact = restarted.export_service.export_job(job.id, export_format)
        content = Path(artifact.artifact_path).read_text(encoding="utf-8")
        assert constants.DEMO_TRANSCRIPT_NOTICE in content
        if export_format is ExportFormat.JSON:
            assert json.loads(content)[0]["demo_notice"] == constants.DEMO_TRANSCRIPT_NOTICE


def test_empty_transcription_marks_failed_without_losing_artifacts(tmp_path: Path) -> None:
    runtime = build_runtime(tmp_path)
    job = runtime.job_service.create_from_upload("sample.mp4", b"media", demo_mode=True)
    runner = JobRunner(
        runtime.job_service,
        runtime.review_service,
        runtime.artifact_store,
        TranscriptionService(EmptyEngine()),
    )

    runner.run(job.id)

    failed = runtime.job_service.get(job.id)
    assert failed.status == JobStatus.FAILED
    assert failed.failed_stage == constants.JOB_STAGE_TRANSCRIPTION
    assert failed.error_code == constants.JOB_ERROR_CODE_NO_SEGMENTS
    assert runtime.artifact_store.exists(job.id, constants.QUALITY_REPORT_RELATIVE_PATH)
    assert runtime.review_service.list_segments(job.id) == []


def test_engine_error_marks_failed_and_runner_does_not_duplicate(tmp_path: Path) -> None:
    runtime = build_runtime(tmp_path)
    job = runtime.job_service.create_from_upload("sample.mp4", b"media", demo_mode=True)
    runner = JobRunner(
        runtime.job_service,
        runtime.review_service,
        runtime.artifact_store,
        TranscriptionService(FailingEngine()),
    )

    runner.run(job.id)
    runner.run(job.id)

    failed = runtime.job_service.get(job.id)
    assert failed.status == JobStatus.FAILED
    assert failed.failed_stage == constants.JOB_STAGE_TRANSCRIPTION
    assert failed.error_code == constants.JOB_ERROR_CODE_PIPELINE_FAILED
    assert runtime.artifact_store.exists(job.id, constants.QUALITY_REPORT_RELATIVE_PATH)


def test_legacy_job_is_not_marked_as_demo(tmp_path: Path) -> None:
    runtime = build_runtime(tmp_path)
    job = runtime.job_service.create_from_upload("sample.mp4", b"media")

    assert runtime.job_service.get(job.id).is_demo is False


def test_restart_marks_unscheduled_demo_job_failed_but_keeps_legacy_pending(
    tmp_path: Path,
) -> None:
    runtime = build_runtime(tmp_path)
    demo_job = runtime.job_service.create_from_upload(
        "demo.mp4", b"media", demo_mode=True
    )
    legacy_job = runtime.job_service.create_from_upload("legacy.mp4", b"media")

    restarted = build_runtime(tmp_path)

    interrupted = restarted.job_service.get(demo_job.id)
    assert interrupted.status == JobStatus.FAILED
    assert interrupted.error_code == constants.JOB_ERROR_CODE_INTERRUPTED
    assert interrupted.retryable is True
    assert restarted.job_service.get(legacy_job.id).status == JobStatus.PENDING
    assert restarted.artifact_store.exists(
        demo_job.id, f"{constants.SOURCE_MEDIA_RELATIVE_DIR}/demo.mp4"
    )
