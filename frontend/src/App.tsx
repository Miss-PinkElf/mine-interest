import { Layout, Tabs, Typography } from 'antd'
import { useState } from 'react'

import {
  APPLICATION_TITLE,
  NAV_JOBS_LABEL,
  NAV_SETTINGS_LABEL,
} from './constants/copy'
import type { JobDto } from './api/jobs'
import { createJob } from './api/jobs'
import { UploadTaskForm } from './features/jobs/UploadTaskForm'
import { TaskProgress } from './features/jobs/TaskProgress'
import { ExportPanel } from './features/exports/ExportPanel'
import { ProviderSettingsForm } from './features/settings/ProviderSettingsForm'
import styles from './App.module.scss'

// 任务页 Tab 键。
const TAB_KEY_JOBS = 'jobs'
// 设置页 Tab 键。
const TAB_KEY_SETTINGS = 'settings'

function App() {
  const [activeJob, setActiveJob] = useState<JobDto | null>(null)

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
