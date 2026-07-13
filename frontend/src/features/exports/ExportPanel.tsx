import { Button, Space, Typography, message } from 'antd'
import { useState } from 'react'

import {
  EXPORT_JSON_LABEL,
  EXPORT_MARKDOWN_LABEL,
  EXPORT_PANEL_TITLE,
} from '../../constants/copy'
import { exportJob } from '../../api/jobs'
import styles from './index.module.scss'

export type ExportPanelProps = {
  jobId: string | null
  disabled?: boolean
}

export function ExportPanel({ jobId, disabled }: ExportPanelProps) {
  const [loadingFormat, setLoadingFormat] = useState<string | null>(null)

  const handleExport = async (format: 'markdown' | 'json') => {
    if (!jobId) return
    setLoadingFormat(format)
    try {
      const artifact = await exportJob(jobId, format)
      message.success(`已导出：${artifact.artifact_path}`)
    } catch (error) {
      message.error(error instanceof Error ? error.message : String(error))
    } finally {
      setLoadingFormat(null)
    }
  }

  return (
    <div className={styles.panel}>
      <Typography.Title level={4}>{EXPORT_PANEL_TITLE}</Typography.Title>
      <Space>
        <Button
          disabled={!jobId || disabled}
          loading={loadingFormat === 'markdown'}
          onClick={() => handleExport('markdown')}
        >
          {EXPORT_MARKDOWN_LABEL}
        </Button>
        <Button
          disabled={!jobId || disabled}
          loading={loadingFormat === 'json'}
          onClick={() => handleExport('json')}
        >
          {EXPORT_JSON_LABEL}
        </Button>
      </Space>
    </div>
  )
}
