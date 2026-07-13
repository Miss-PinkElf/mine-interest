import { Alert, Progress, Typography } from 'antd'

import {
  JOB_STATUS_FAILED,
  JOB_STATUS_LABELS,
  JOB_STATUS_PROGRESS,
} from '../../constants/task'
import { TASK_STATUS_TITLE } from '../../constants/copy'
import type { JobDto } from '../../api/jobs'
import styles from './index.module.scss'

export type TaskProgressProps = {
  job: JobDto | null
}

export function TaskProgress({ job }: TaskProgressProps) {
  if (!job) {
    return null
  }

  const percent = JOB_STATUS_PROGRESS[job.status] ?? 0
  const label = JOB_STATUS_LABELS[job.status] ?? job.status
  const isFailed = job.status === JOB_STATUS_FAILED

  return (
    <div className={styles.panel}>
      <Typography.Title level={4}>{TASK_STATUS_TITLE}</Typography.Title>
      <Typography.Paragraph className={styles.meta}>
        任务 ID：{job.id}
      </Typography.Paragraph>
      <Progress percent={percent} status={isFailed ? 'exception' : 'active'} />
      <Typography.Text>{label}</Typography.Text>
      {isFailed && (
        <Alert
          className={styles.alert}
          type="error"
          showIcon
          message={job.error_code || '任务失败'}
          description={job.failed_stage ? `阶段：${job.failed_stage}` : undefined}
        />
      )}
    </div>
  )
}
