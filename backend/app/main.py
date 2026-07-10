from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings


APPLICATION_TITLE = "视频情感化转写本地服务"
HEALTH_ENDPOINT_PATH = "/api/health"
HEALTH_STATUS_RESPONSE = {"status": "ok"}
CORS_ALLOW_ALL_METHODS = ["*"]
CORS_ALLOW_ALL_HEADERS = ["*"]


def create_app() -> FastAPI:
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
    return application


def register_health_route(application: FastAPI) -> None:
    @application.get(HEALTH_ENDPOINT_PATH)
    def get_health() -> dict[str, str]:
        return HEALTH_STATUS_RESPONSE


app = create_app()
