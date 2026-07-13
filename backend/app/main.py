"""FastAPI 应用入口与基础 HTTP 配置。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import exports as exports_routes
from app.api.routes import settings as settings_routes
from app.api.routes import jobs as jobs_routes
from app.api.routes import segments as segments_routes
from app.core.config import get_settings


# 本地 FastAPI 服务展示的应用标题。
APPLICATION_TITLE = "视频情感化转写本地服务"
# 本地工作台与探针访问的健康检查路径。
HEALTH_ENDPOINT_PATH = "/api/health"
# 健康检查成功时返回的稳定响应体。
HEALTH_STATUS_RESPONSE = {"status": "ok"}
# CORS 允许所有 HTTP 方法，来源仍由本地白名单限制。
CORS_ALLOW_ALL_METHODS = ["*"]
# CORS 允许所有请求头，避免本地 API 开发期间遗漏自定义头。
CORS_ALLOW_ALL_HEADERS = ["*"]


def create_app() -> FastAPI:
    """创建带本地 CORS、健康检查与任务 API 的应用实例。"""
    settings = get_settings()
    application = FastAPI(title=APPLICATION_TITLE)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_cors_origins),
        allow_credentials=True,
        allow_methods=CORS_ALLOW_ALL_METHODS,
        allow_headers=CORS_ALLOW_ALL_HEADERS,
    )

    register_health_route(application)
    application.include_router(jobs_routes.router)
    application.include_router(segments_routes.router)
    application.include_router(exports_routes.router)
    application.include_router(settings_routes.router)
    return application


def register_health_route(application: FastAPI) -> None:
    """注册不依赖外部服务的存活检查端点。"""

    @application.get(HEALTH_ENDPOINT_PATH)
    def get_health() -> dict[str, str]:
        """返回稳定的服务可用状态。"""
        return HEALTH_STATUS_RESPONSE


# ASGI 服务器导入的应用实例。
app = create_app()
