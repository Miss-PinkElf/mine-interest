import { Layout, Tabs, Typography } from 'antd'
import { useEffect, useState } from 'react'

import {
  APPLICATION_TITLE,
  NAV_JOBS_LABEL,
  NAV_SETTINGS_LABEL,
  REVIEW_WORKSPACE_TITLE,
} from './constants/copy'
import type { JobDto, SegmentDto } from './api/jobs'
import { confirmSegment, createJob, listSegments } from './api/jobs'
import { splitSegment } from './api/review'
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
    if (!activeJob) {
      setSegments([])
      return
    }
    listSegments(activeJob.id)
      .then(setSegments)
      .catch(() => setSegments([]))
  }, [activeJob])

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
                    onCreated={(job) => setActiveJob(job)}
                  />
                  <TaskProgress job={activeJob} />
                  <ExportPanel jobId={activeJob?.id ?? null} />
                </div>
              ),
            },
            {
              key: TAB_KEY_REVIEW,
              label: REVIEW_WORKSPACE_TITLE,
              children: activeJob ? (
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
                    setSegments(refreshed)
                    return next
                  }}
                  confirmSegment={async (segmentId) => {
                    await confirmSegment(segmentId)
                    setSegments(await listSegments(activeJob.id))
                  }}
                />
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
