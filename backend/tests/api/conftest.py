"""API 测试共享夹具：隔离数据根并覆盖运行时依赖。"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import provide_runtime
from app.api.runtime import AppRuntime, build_runtime, reset_runtime
from app.domain.models import Segment
from app.main import app


@pytest.fixture
def runtime(tmp_path: Path) -> Iterator[AppRuntime]:
    """为每个测试构建独立运行时，并覆盖 FastAPI 依赖。"""
    reset_runtime()
    current = build_runtime(tmp_path)
    app.dependency_overrides[provide_runtime] = lambda: current
    # 依赖链通过 provide_runtime 间接取服务时，也覆盖具体 provider。
    from app.api import deps

    app.dependency_overrides[deps.provide_job_service] = lambda: current.job_service
    app.dependency_overrides[deps.provide_review_service] = lambda: current.review_service
    app.dependency_overrides[deps.provide_export_service] = lambda: current.export_service
    try:
        yield current
    finally:
        app.dependency_overrides.clear()
        reset_runtime()


@pytest.fixture
def client(runtime: AppRuntime) -> Iterator[TestClient]:
    """返回绑定隔离运行时的 TestClient。"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def prepared_job(runtime: AppRuntime):
    """创建已有媒体与一个可确认片段的任务。"""
    job = runtime.job_service.create_from_upload(
        filename="sample.mp4",
        content=b"fake-media-bytes",
    )
    segment = Segment.create(
        raw_text="原始识别文本",
        start_seconds=0.0,
        end_seconds=1.5,
        speaker_id="speaker_0",
    )
    runtime.review_service.add_segment(job.id, segment)

    class PreparedJob:
        id = job.id
        segment_id = segment.id

    return PreparedJob()
