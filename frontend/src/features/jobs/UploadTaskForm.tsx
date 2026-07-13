import { Button, Form, Upload, message } from 'antd'
import { useState } from 'react'
import type { UploadFile } from 'antd/es/upload/interface'

import { START_TASK_LABEL, UPLOAD_MEDIA_LABEL, UPLOAD_SUCCESS_MESSAGE } from '../../constants/copy'
import type { JobDto } from '../../api/jobs'
import styles from './index.module.scss'

export type UploadTaskFormProps = {
  createJob: (file: File) => Promise<JobDto>
  onCreated?: (job: JobDto) => void
}

export function UploadTaskForm({ createJob, onCreated }: UploadTaskFormProps) {
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [submitting, setSubmitting] = useState(false)

  const selectedFile = fileList[0]?.originFileObj as File | undefined

  const handleSubmit = async () => {
    if (!selectedFile) {
      message.warning(UPLOAD_MEDIA_LABEL)
      return
    }
    setSubmitting(true)
    try {
      const job = await createJob(selectedFile)
      message.success(UPLOAD_SUCCESS_MESSAGE)
      onCreated?.(job)
    } catch (error) {
      message.error(error instanceof Error ? error.message : String(error))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className={styles.panel}>
      <Form layout="vertical" onFinish={handleSubmit}>
        <Form.Item label={UPLOAD_MEDIA_LABEL} required>
          <Upload
            accept="video/*,audio/*"
            beforeUpload={() => false}
            fileList={fileList}
            maxCount={1}
            onChange={({ fileList: next }) => setFileList(next)}
          >
            <Button aria-label={UPLOAD_MEDIA_LABEL}>{UPLOAD_MEDIA_LABEL}</Button>
          </Upload>
        </Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          loading={submitting}
          disabled={!selectedFile}
        >
          {START_TASK_LABEL}
        </Button>
      </Form>
    </div>
  )
}
