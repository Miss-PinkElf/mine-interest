import { Layout, Typography } from 'antd'

import styles from './App.module.scss'

const APPLICATION_TITLE = '视频情感化转写'
const APPLICATION_DESCRIPTION = '本地审核工作台正在初始化。'

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
