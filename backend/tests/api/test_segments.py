"""片段确认与导出 API 测试。"""

from app.core import constants
from app.core.database import session_scope
from app.domain.enums import ExportFormat, JobStatus, SegmentReviewStatus
from app.domain.models import Segment
from app.repositories.jobs import JobRepository


def test_confirmed_segment_can_be_exported(client, runtime, prepared_job) -> None:
    runtime.job_service.mark_review(prepared_job.id)
    confirm_response = client.post(
        f"{constants.API_SEGMENTS_PATH}/{prepared_job.segment_id}/"
        f"{constants.API_SEGMENT_CONFIRM_SUFFIX}"
    )
    assert confirm_response.status_code == constants.HTTP_STATUS_OK
    assert (
        confirm_response.json()["review_status"]
        == SegmentReviewStatus.CONFIRMED.value
    )
    confirmed_job = client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}")
    assert confirmed_job.json()["status"] == JobStatus.CONFIRMED.value

    export_response = client.post(
        f"{constants.API_JOBS_PATH}/{prepared_job.id}/{constants.API_JOB_EXPORTS_SUFFIX}",
        json={"format": ExportFormat.MARKDOWN.value},
    )
    assert export_response.status_code == constants.HTTP_STATUS_CREATED
    body = export_response.json()
    assert body["job_id"] == prepared_job.id
    assert body["format"] == ExportFormat.MARKDOWN.value
    assert body["artifact_path"]

    job_response = client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}")
    assert job_response.status_code == constants.HTTP_STATUS_OK
    assert job_response.json()["status"] == JobStatus.EXPORTED.value


def test_job_confirms_only_after_all_segments_are_confirmed(client, runtime, prepared_job) -> None:
    runtime.job_service.mark_review(prepared_job.id)
    second = Segment.create(raw_text="第二段", start_seconds=1.5, end_seconds=3.0)
    runtime.review_service.add_segment(prepared_job.id, second)

    first_response = client.post(
        f"{constants.API_SEGMENTS_PATH}/{prepared_job.segment_id}/"
        f"{constants.API_SEGMENT_CONFIRM_SUFFIX}"
    )
    assert first_response.status_code == constants.HTTP_STATUS_OK
    assert client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}").json()["status"] == JobStatus.REVIEW.value

    second_response = client.post(
        f"{constants.API_SEGMENTS_PATH}/{second.id}/{constants.API_SEGMENT_CONFIRM_SUFFIX}"
    )
    assert second_response.status_code == constants.HTTP_STATUS_OK
    assert client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}").json()["status"] == JobStatus.CONFIRMED.value


def test_editing_confirmed_text_returns_job_to_review(client, runtime, prepared_job) -> None:
    runtime.job_service.mark_review(prepared_job.id)
    client.post(
        f"{constants.API_SEGMENTS_PATH}/{prepared_job.segment_id}/"
        f"{constants.API_SEGMENT_CONFIRM_SUFFIX}"
    )

    edit_response = client.post(
        f"{constants.API_SEGMENTS_PATH}/{prepared_job.segment_id}/text",
        json={"edited_text": "重新修订"},
    )
    assert edit_response.status_code == constants.HTTP_STATUS_OK
    assert edit_response.json()["review_status"] == SegmentReviewStatus.PENDING.value
    assert client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}").json()["status"] == JobStatus.REVIEW.value

    confirm_response = client.post(
        f"{constants.API_SEGMENTS_PATH}/{prepared_job.segment_id}/"
        f"{constants.API_SEGMENT_CONFIRM_SUFFIX}"
    )
    assert confirm_response.status_code == constants.HTTP_STATUS_OK
    assert client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}").json()["status"] == JobStatus.CONFIRMED.value


def test_loading_legacy_review_job_repairs_confirmed_status(client, runtime, prepared_job) -> None:
    runtime.job_service.mark_review(prepared_job.id)
    runtime.review_service.confirm_segment(prepared_job.segment_id)
    # 模拟修复前已确认片段却仍持久化为待审核的旧任务。
    runtime.job_service.mark_review(prepared_job.id)

    response = client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}")
    assert response.status_code == constants.HTTP_STATUS_OK
    assert response.json()["status"] == JobStatus.CONFIRMED.value
    with session_scope(runtime.session_factory) as session:
        persisted = JobRepository(session).get(prepared_job.id)
    assert persisted is not None
    assert persisted.status == JobStatus.CONFIRMED


def test_loading_partially_confirmed_job_keeps_review_status(client, runtime, prepared_job) -> None:
    runtime.job_service.mark_review(prepared_job.id)
    second = Segment.create(raw_text="仍待审核", start_seconds=1.5, end_seconds=3.0)
    runtime.review_service.add_segment(prepared_job.id, second)
    runtime.review_service.confirm_segment(prepared_job.segment_id)

    response = client.get(f"{constants.API_JOBS_PATH}/{prepared_job.id}")
    assert response.status_code == constants.HTTP_STATUS_OK
    assert response.json()["status"] == JobStatus.REVIEW.value
