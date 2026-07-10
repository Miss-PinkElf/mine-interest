import { Layout, Typography } from 'antd'

import styles from './App.module.scss'

// 工作台标题，后续各功能页共享同一产品名称。
const APPLICATION_TITLE = '视频情感化转写'
// 骨架阶段向用户展示的当前初始化状态。
const APPLICATION_DESCRIPTION = '本地审核工作台正在初始化。'

// 仅提供当前阶段的工作台骨架，后续功能按 feature 目录逐步接入。
function App() {
  return (
    <Layout className={styles.applicationLayout}>
      <Layout.Header className={styles.header}>
        <Typography.Title className={styles.title} level={1}>
          {APPLICATION_TITLE}
        </Typography.Title>
      </Layout.Header>
      <Layout.Content className={styles.content}>
        <Typography.Paragraph className={styles.description}>
          {APPLICATION_DESCRIPTION}
        </Typography.Paragraph>
      </Layout.Content>
    </Layout>
  )
}

export default App
