import { Alert, Layout, Tabs, Typography, message } from 'antd'
import { useEffect, useState } from 'react'

import {
  APPLICATION_TITLE,
  DEMO_MODE_NOTICE,
  NAV_JOBS_LABEL,
  NAV_SETTINGS_LABEL,
  REVIEW_WORKSPACE_TITLE,
  SEGMENT_CONFIRM_FAILED_MESSAGE,
  SEGMENT_CONFIRMED_MESSAGE,
} from './constants/copy'
import type { JobDto, SegmentDto } from './api/jobs'
import { confirmSegment, createJob, getJob, listSegments } from './api/jobs'
import {
  ACTIVE_JOB_SESSION_KEY,
  JOB_STATUS_PENDING,
  JOB_STATUS_PROCESSING,
  SEGMENT_REVIEW_STATUS_CONFIRMED,
  TASK_STATUS_POLL_INTERVAL_MS,
} from './constants/task'
import { editSegmentText, splitSegment } from './api/review'
import { UploadTaskForm } from './features/jobs/UploadTaskForm'
import { TaskProgress } from './features/jobs/TaskProgress'
import { ExportPanel } from './features/exports/ExportPanel'
import { ProviderSettingsForm } from './features/settings/ProviderSettingsForm'
import { ReviewWorkspace } from './features/review/ReviewWorkspace'
import styles from './App.module.scss'

const TAB_KEY_JOBS = 'jobs'
const TAB_KEY_REVIEW = 'review'
const TAB_KEY_SETTINGS = 'settings'

function App() {
  const [activeJob, setActiveJob] = useState<JobDto | null>(null)
  const [segments, setSegments] = useState<SegmentDto[]>([])

  useEffect(() => {
    const savedJobId = window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY)
    if (!savedJobId) return

    let isMounted = true
    getJob(savedJobId)
      .then((job) => {
        // 新上传任务已替换会话 ID 时，旧查询结果不得覆盖当前任务。
        if (isMounted && window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY) === savedJobId) {
          setActiveJob(job)
        }
      })
      .catch(() => {
        if (window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY) === savedJobId) {
          window.sessionStorage.removeItem(ACTIVE_JOB_SESSION_KEY)
        }
      })
    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    const jobId = activeJob?.id
    if (!jobId) {
      setSegments([])
      return
    }

    let isCurrentJob = true
    let pollTimer: ReturnType<typeof setTimeout> | undefined
    const stillActive = () =>
      isCurrentJob && window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY) === jobId

    const refreshJob = async () => {
      try {
        const latestJob = await getJob(jobId)
        if (!stillActive()) return
        setActiveJob(latestJob)
        const isProcessing =
          latestJob.status === JOB_STATUS_PENDING || latestJob.status === JOB_STATUS_PROCESSING
        if (isProcessing) {
          pollTimer = setTimeout(refreshJob, TASK_STATUS_POLL_INTERVAL_MS)
          return
        }
        const latestSegments = await listSegments(jobId)
        if (stillActive()) setSegments(latestSegments)
      } catch {
        if (stillActive()) {
          pollTimer = setTimeout(refreshJob, TASK_STATUS_POLL_INTERVAL_MS)
        }
      }
    }

    void refreshJob()
    return () => {
      isCurrentJob = false
      if (pollTimer) clearTimeout(pollTimer)
    }
  }, [activeJob?.id])

  const hasConfirmedSegment = segments.some(
    (segment) => segment.review_status === SEGMENT_REVIEW_STATUS_CONFIRMED,
  )

  const handleJobCreated = (job: JobDto) => {
    window.sessionStorage.setItem(ACTIVE_JOB_SESSION_KEY, job.id)
    setSegments([])
    setActiveJob(job)
  }

  /** 操作成功后从后端读取持久状态，避免任务进度停留在待审核。 */
  const refreshActiveJob = async (jobId: string) => {
    const latestJob = await getJob(jobId)
    if (window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY) === jobId) {
      setActiveJob(latestJob)
    }
  }

  /** 先持久化人工修订，再确认片段并刷新任务与片段状态。 */
  const handleConfirmSegment = async (segmentId: string, editedText: string | null) => {
    if (!activeJob) return
    try {
      if (editedText !== null) {
        await editSegmentText(segmentId, editedText)
      }
      await confirmSegment(segmentId)
      const [latestJob, refreshedSegments] = await Promise.all([
        getJob(activeJob.id),
        listSegments(activeJob.id),
      ])
      if (window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY) === activeJob.id) {
        setActiveJob(latestJob)
        setSegments(refreshedSegments)
        message.success(SEGMENT_CONFIRMED_MESSAGE)
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : SEGMENT_CONFIRM_FAILED_MESSAGE)
    }
  }

  return (
    <Layout className={styles.applicationLayout}>
      <Layout.Header className={styles.header}>
        <Typography.Title className={styles.title} level={1}>
          {APPLICATION_TITLE}
        </Typography.Title>
      </Layout.Header>
      <Layout.Content className={styles.content}>
        <Tabs
          items={[
            {
              key: TAB_KEY_JOBS,
              label: NAV_JOBS_LABEL,
              children: (
                <div className={styles.tabBody}>
                  <UploadTaskForm
                    createJob={createJob}
                    onCreated={handleJobCreated}
                  />
                  <TaskProgress job={activeJob} />
                  <ExportPanel
                    jobId={activeJob?.id ?? null}
                    disabled={!hasConfirmedSegment}
                    onExported={refreshActiveJob}
                  />
                </div>
              ),
            },
            {
              key: TAB_KEY_REVIEW,
              label: REVIEW_WORKSPACE_TITLE,
              children: activeJob ? (
                <div>
                  {activeJob.is_demo && <Alert type="warning" showIcon title={DEMO_MODE_NOTICE} />}
                  <ReviewWorkspace
                    job={{
                      id: activeJob.id,
                      segments,
                      evidenceBySegment: Object.fromEntries(
                        segments.map((segment) => [segment.id, []]),
                      ),
                    }}
                    splitSegment={async (segmentId, atSeconds) => {
                      const next = await splitSegment(segmentId, atSeconds)
                      const refreshed = await listSegments(activeJob.id)
                      if (window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY) === activeJob.id) {
                        setSegments(refreshed)
                      }
                      return next
                    }}
                    confirmSegment={handleConfirmSegment}
                  />
                </div>
              ) : (
                <Typography.Paragraph>请先创建任务</Typography.Paragraph>
              ),
            },
            {
              key: TAB_KEY_SETTINGS,
              label: NAV_SETTINGS_LABEL,
              children: <ProviderSettingsForm />,
            },
          ]}
        />
      </Layout.Content>
    </Layout>
  )
}

export default App
