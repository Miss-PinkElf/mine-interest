/** Provider 设置 API 客户端；不把密钥写入 localStorage。 */

import { requestJson } from './client'
import { API_SETTINGS_PROVIDER_PATH } from '../constants/task'

export type ProviderSettingsDto = {
  base_url: string
  model_name: string
  // 仅回显是否已配置，不回显完整密钥。
  api_key_configured: boolean
}

export type ProviderSettingsUpdate = {
  base_url: string
  model_name: string
  api_key?: string
}

export async function getProviderSettings(): Promise<ProviderSettingsDto> {
  return requestJson<ProviderSettingsDto>(API_SETTINGS_PROVIDER_PATH)
}

export async function saveProviderSettings(
  payload: ProviderSettingsUpdate,
): Promise<ProviderSettingsDto> {
  return requestJson<ProviderSettingsDto>(API_SETTINGS_PROVIDER_PATH, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
