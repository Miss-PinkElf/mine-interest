"""Provider 设置 API。"""

from fastapi import APIRouter, Depends

from app.api.deps import provide_settings_service
from app.core import constants
from app.domain.schemas import ProviderSettingsSchema, ProviderSettingsUpdateSchema
from app.services.settings import SettingsService

router = APIRouter(tags=["settings"])


@router.get(
    constants.API_SETTINGS_PROVIDER_PATH,
    response_model=ProviderSettingsSchema,
)
def get_provider_settings(
    settings_service: SettingsService = Depends(provide_settings_service),
) -> ProviderSettingsSchema:
    """读取本机 Provider 设置（不回显完整密钥）。"""
    return settings_service.get_provider_settings()


@router.put(
    constants.API_SETTINGS_PROVIDER_PATH,
    response_model=ProviderSettingsSchema,
)
def update_provider_settings(
    body: ProviderSettingsUpdateSchema,
    settings_service: SettingsService = Depends(provide_settings_service),
) -> ProviderSettingsSchema:
    """保存本机 Provider 设置。"""
    return settings_service.update_provider_settings(
        base_url=body.base_url,
        model_name=body.model_name,
        api_key=body.api_key,
    )
