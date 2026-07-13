"""片段确认与导出 API 测试。"""

from app.core import constants
from app.domain.enums import ExportFormat, JobStatus, SegmentReviewStatus


def test_confirmed_segment_can_be_exported(client, prepared_job) -> None:
    confirm_response = client.post(
        f"{constants.API_SEGMENTS_PATH}/{prepared_job.segment_id}/"
        f"{constants.API_SEGMENT_CONFIRM_SUFFIX}"
    )
    assert confirm_response.status_code == constants.HTTP_STATUS_OK
    assert (
        confirm_response.json()["review_status"]
        == SegmentReviewStatus.CONFIRMED.value
    )

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
