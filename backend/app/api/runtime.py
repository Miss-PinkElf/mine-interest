"""应用运行时：共享数据根、仓储会话与服务实例。"""

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session, sessionmaker

from app.core import constants
from app.core.config import get_settings
from app.core.database import create_session_factory
from app.services.artifacts import ArtifactStore
from app.services.exports import ExportService
from app.services.jobs import JobService
from app.services.review import ReviewService
from app.services.settings import SettingsService


@dataclass
class AppRuntime:
    """一次进程内复用的本地运行时依赖集合。"""

    data_root: Path
    artifact_store: ArtifactStore
    session_factory: sessionmaker[Session]
    job_service: JobService
    review_service: ReviewService
    export_service: ExportService
    settings_service: SettingsService


def build_runtime(data_root: Path | str | None = None) -> AppRuntime:
    """基于数据根目录构建本地服务运行时。"""
    root = Path(data_root) if data_root is not None else get_settings().data_root
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    artifact_store = ArtifactStore(root / "artifacts")
    session_factory = create_session_factory(root / constants.JOB_SQLITE_FILENAME)
    job_service = JobService(
        artifact_store=artifact_store,
        session_factory=session_factory,
    )
    review_service = ReviewService(session_factory=session_factory)
    export_service = ExportService(
        artifact_store=artifact_store,
        job_service=job_service,
        review_service=review_service,
    )
    settings_service = SettingsService(session_factory=session_factory)
    return AppRuntime(
        data_root=root,
        artifact_store=artifact_store,
        session_factory=session_factory,
        job_service=job_service,
        review_service=review_service,
        export_service=export_service,
        settings_service=settings_service,
    )


# 进程级默认运行时，可在测试中通过依赖覆盖替换。
_default_runtime: AppRuntime | None = None


def get_runtime() -> AppRuntime:
    """返回默认运行时，首次访问时惰性创建。"""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = build_runtime()
    return _default_runtime


def reset_runtime() -> None:
    """清空默认运行时，便于测试隔离。"""
    global _default_runtime
    _default_runtime = None
