/** 任务状态、轮询与 API 路径常量。 */

// 本地 API 任务集合路径。
export const API_JOBS_PATH = '/api/jobs'
// 本地 API 设置路径。
export const API_SETTINGS_PROVIDER_PATH = '/api/settings/provider'
// 任务状态轮询间隔（毫秒）。
export const TASK_STATUS_POLL_INTERVAL_MS = 2000
// 任务等待处理状态键。
export const JOB_STATUS_PENDING = 'pending'
// 任务处理中状态键。
export const JOB_STATUS_PROCESSING = 'processing'
// 任务待审核状态键。
export const JOB_STATUS_REVIEW = 'review'
// 任务已确认状态键。
export const JOB_STATUS_CONFIRMED = 'confirmed'
// 任务已导出状态键。
export const JOB_STATUS_EXPORTED = 'exported'
// 任务失败状态键。
export const JOB_STATUS_FAILED = 'failed'

// 状态键到展示文案映射。
export const JOB_STATUS_LABELS: Record<string, string> = {
  [JOB_STATUS_PENDING]: '等待处理',
  [JOB_STATUS_PROCESSING]: '处理中',
  [JOB_STATUS_REVIEW]: '待审核',
  [JOB_STATUS_CONFIRMED]: '已确认',
  [JOB_STATUS_EXPORTED]: '已导出',
  [JOB_STATUS_FAILED]: '失败',
}

// 状态进度百分比映射，仅用于本地进度条展示。
export const JOB_STATUS_PROGRESS: Record<string, number> = {
  [JOB_STATUS_PENDING]: 10,
  [JOB_STATUS_PROCESSING]: 45,
  [JOB_STATUS_REVIEW]: 70,
  [JOB_STATUS_CONFIRMED]: 90,
  [JOB_STATUS_EXPORTED]: 100,
  [JOB_STATUS_FAILED]: 100,
}
