"""任务上传与查询 API 测试。"""

from app.core import constants
from app.domain.enums import JobStatus


def test_upload_media_creates_pending_job(client) -> None:
    response = client.post(
        constants.API_JOBS_PATH,
        files={
            constants.UPLOAD_FILE_FORM_FIELD: (
                "sample.mp4",
                b"fake-video-bytes",
                "video/mp4",
            )
        },
    )

    assert response.status_code == constants.HTTP_STATUS_CREATED
    body = response.json()
    assert body["status"] == JobStatus.PENDING.value
    assert body["id"]
    assert body["source_media_path"]

    detail = client.get(f"{constants.API_JOBS_PATH}/{body['id']}")
    assert detail.status_code == constants.HTTP_STATUS_OK
    assert detail.json()["id"] == body["id"]


def test_list_job_segments_returns_seeded_segments(client, prepared_job) -> None:
    response = client.get(
        f"{constants.API_JOBS_PATH}/{prepared_job.id}/{constants.API_JOB_SEGMENTS_SUFFIX}"
    )

    assert response.status_code == constants.HTTP_STATUS_OK
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == prepared_job.segment_id
    assert body[0]["raw_text"] == "原始识别文本"
    assert body[0]["final_text"] == "原始识别文本"
