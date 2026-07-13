"""Provider 设置服务。"""

from sqlalchemy.orm import Session, sessionmaker

from app.core import constants
from app.core.database import session_scope
from app.domain.schemas import ProviderSettingsSchema
from app.repositories.settings import ProviderSettingsRepository


class SettingsService:
    """管理本机云端 Provider 配置。"""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_provider_settings(self) -> ProviderSettingsSchema:
        """读取设置；缺失时返回空默认值。"""
        with session_scope(self._session_factory) as session:
            row = ProviderSettingsRepository(session).get()
            if row is None:
                return ProviderSettingsSchema(
                    base_url=constants.DEFAULT_PROVIDER_BASE_URL,
                    model_name=constants.DEFAULT_PROVIDER_MODEL_NAME,
                    api_key_configured=False,
                )
            return ProviderSettingsSchema(
                base_url=row.base_url,
                model_name=row.model_name,
                api_key_configured=bool(row.api_key),
            )

    def update_provider_settings(
        self,
        *,
        base_url: str,
        model_name: str,
        api_key: str | None,
    ) -> ProviderSettingsSchema:
        """更新设置并返回脱敏结果。"""
        with session_scope(self._session_factory) as session:
            row = ProviderSettingsRepository(session).upsert(
                base_url=base_url,
                model_name=model_name,
                api_key=api_key,
            )
            return ProviderSettingsSchema(
                base_url=row.base_url,
                model_name=row.model_name,
                api_key_configured=bool(row.api_key),
            )
