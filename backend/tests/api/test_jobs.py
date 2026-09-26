"""任务上传与查询 API 测试。"""

from pathlib import Path

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


def test_demo_upload_automatically_creates_reviewable_export(client) -> None:
    """上传后不手工插片段，也能确认并导出演示结果。"""
    response = client.post(
        constants.API_JOBS_PATH,
        files={constants.UPLOAD_FILE_FORM_FIELD: ("sample.mp4", b"fake-video", "video/mp4")},
        data={constants.UPLOAD_DEMO_MODE_FORM_FIELD: "true"},
    )
    assert response.status_code == constants.HTTP_STATUS_CREATED
    job_id = response.json()["id"]
    assert response.json()["is_demo"] is True

    detail = client.get(f"{constants.API_JOBS_PATH}/{job_id}")
    assert detail.json()["status"] == JobStatus.REVIEW.value
    assert detail.json()["is_demo"] is True

    segments_response = client.get(
        f"{constants.API_JOBS_PATH}/{job_id}/{constants.API_JOB_SEGMENTS_SUFFIX}"
    )
    segments = segments_response.json()
    assert len(segments) == 1
    assert "演示" in segments[0]["raw_text"]

    edited = client.post(
        f"{constants.API_SEGMENTS_PATH}/{segments[0]['id']}/text",
        json={"edited_text": "人工修订后的文本"},
    )
    assert edited.status_code == constants.HTTP_STATUS_OK
    assert edited.json()["raw_text"] == segments[0]["raw_text"]
    assert edited.json()["edited_text"] == "人工修订后的文本"

    confirmed = client.post(
        f"{constants.API_SEGMENTS_PATH}/{segments[0]['id']}/{constants.API_SEGMENT_CONFIRM_SUFFIX}"
    )
    assert confirmed.status_code == constants.HTTP_STATUS_OK

    for export_format in ("markdown", "json"):
        exported = client.post(
            f"{constants.API_JOBS_PATH}/{job_id}/{constants.API_JOB_EXPORTS_SUFFIX}",
            json={"format": export_format},
        )
        assert exported.status_code == constants.HTTP_STATUS_CREATED
        content = Path(exported.json()["artifact_path"]).read_text(encoding="utf-8")
        assert constants.DEMO_TRANSCRIPT_NOTICE in content
        assert "人工修订后的文本" in content
