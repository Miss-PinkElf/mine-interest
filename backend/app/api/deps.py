"""FastAPI 依赖注入入口。"""

from app.api.runtime import AppRuntime, get_runtime
from app.services.exports import ExportService
from app.services.jobs import JobService
from app.services.review import ReviewService


def provide_runtime() -> AppRuntime:
    """提供当前请求可用的运行时。"""
    return get_runtime()


def provide_job_service() -> JobService:
    """提供任务服务。"""
    return provide_runtime().job_service


def provide_review_service() -> ReviewService:
    """提供审核服务。"""
    return provide_runtime().review_service


def provide_export_service() -> ExportService:
    """提供导出服务。"""
    return provide_runtime().export_service
