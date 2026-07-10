from dataclasses import dataclass


LOCAL_DEVELOPMENT_FRONTEND_ORIGIN = "http://localhost:5173"
VITE_LOOPBACK_FRONTEND_ORIGIN = "http://127.0.0.1:5173"


@dataclass(frozen=True)
class AppSettings:
    allowed_cors_origins: tuple[str, ...] = (
        LOCAL_DEVELOPMENT_FRONTEND_ORIGIN,
        VITE_LOOPBACK_FRONTEND_ORIGIN,
    )


def get_settings() -> AppSettings:
    return AppSettings()
