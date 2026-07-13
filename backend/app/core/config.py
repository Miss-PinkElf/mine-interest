"""本地服务的运行配置。"""

from dataclasses import dataclass
from pathlib import Path

from app.core import constants


# Vite 默认开发地址，用于浏览器直接请求本地 API 时的 CORS 放行。
LOCAL_DEVELOPMENT_FRONTEND_ORIGIN = "http://localhost:5173"
# Vite 绑定回环地址时对应的浏览器 Origin，同样需要被本地 API 放行。
VITE_LOOPBACK_FRONTEND_ORIGIN = "http://127.0.0.1:5173"


@dataclass(frozen=True)
class AppSettings:
    # 仅允许本机开发工作台跨域访问，避免开放给任意来源。
    allowed_cors_origins: tuple[str, ...] = (
        LOCAL_DEVELOPMENT_FRONTEND_ORIGIN,
        VITE_LOOPBACK_FRONTEND_ORIGIN,
    )
    # 本地 SQLite 与产物文件的数据根目录。
    data_root: Path = Path(constants.DEFAULT_DATA_ROOT_DIRNAME)


def get_settings() -> AppSettings:
    """返回应用当前使用的本地运行配置。"""
    return AppSettings()
