import { Alert, Button, Form, Input, message } from 'antd'
import { useEffect, useState } from 'react'

import {
  API_KEY_STORAGE_HINT,
  PROVIDER_API_KEY_LABEL,
  PROVIDER_BASE_URL_LABEL,
  PROVIDER_MODEL_LABEL,
  PROVIDER_SETTINGS_TITLE,
  SAVE_SETTINGS_LABEL,
  SETTINGS_SAVED_MESSAGE,
} from '../../constants/copy'
import {
  getProviderSettings,
  saveProviderSettings,
  type ProviderSettingsDto,
} from '../../api/settings'
import styles from './index.module.scss'

// 故意不使用 localStorage 保存 API Key。
const FORBIDDEN_STORAGE_KEY = 'provider_api_key'

export function ProviderSettingsForm() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [current, setCurrent] = useState<ProviderSettingsDto | null>(null)

  useEffect(() => {
    let active = true
    getProviderSettings()
      .then((settings) => {
        if (!active) return
        setCurrent(settings)
        form.setFieldsValue({
          base_url: settings.base_url,
          model_name: settings.model_name,
          api_key: '',
        })
      })
      .catch(() => {
        // 后端未启动时保留空表单。
      })
    return () => {
      active = false
    }
  }, [form])

  const handleSubmit = async (values: {
    base_url: string
    model_name: string
    api_key?: string
  }) => {
    setLoading(true)
    try {
      // 确保不会把密钥写入浏览器本地存储。
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem(FORBIDDEN_STORAGE_KEY)
      }
      const saved = await saveProviderSettings({
        base_url: values.base_url,
        model_name: values.model_name,
        api_key: values.api_key || undefined,
      })
      setCurrent(saved)
      form.setFieldValue('api_key', '')
      message.success(SETTINGS_SAVED_MESSAGE)
    } catch (error) {
      message.error(error instanceof Error ? error.message : String(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.panel}>
      <h3>{PROVIDER_SETTINGS_TITLE}</h3>
      <Alert className={styles.hint} type="info" showIcon message={API_KEY_STORAGE_HINT} />
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Form.Item
          label={PROVIDER_BASE_URL_LABEL}
          name="base_url"
          rules={[{ required: true, message: PROVIDER_BASE_URL_LABEL }]}
        >
          <Input placeholder="https://api.openai.com/v1" />
        </Form.Item>
        <Form.Item
          label={PROVIDER_MODEL_LABEL}
          name="model_name"
          rules={[{ required: true, message: PROVIDER_MODEL_LABEL }]}
        >
          <Input placeholder="gpt-4.1-mini" />
        </Form.Item>
        <Form.Item label={PROVIDER_API_KEY_LABEL} name="api_key">
          <Input.Password
            placeholder={
              current?.api_key_configured ? '已配置（留空则不修改）' : '输入 API Key'
            }
          />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={loading}>
          {SAVE_SETTINGS_LABEL}
        </Button>
      </Form>
    </div>
  )
}
