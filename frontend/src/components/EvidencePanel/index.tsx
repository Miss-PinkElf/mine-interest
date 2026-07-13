import { Alert, List, Typography } from 'antd'

import { CONFLICT_REVIEW_COPY, EVIDENCE_PANEL_TITLE } from '../../constants/copy'
import styles from './index.module.scss'

export type EvidenceItem = {
  id: string
  kind: string
  source: string
  summary: string
  availability?: string
  conflict?: boolean
}

export type EvidencePanelProps = {
  items: EvidenceItem[]
}

export function EvidencePanel({ items }: EvidencePanelProps) {
  const hasConflict = items.some((item) => item.conflict)

  return (
    <div className={styles.panel}>
      <Typography.Title level={5}>{EVIDENCE_PANEL_TITLE}</Typography.Title>
      {hasConflict && (
        <Alert type="warning" showIcon message={CONFLICT_REVIEW_COPY} />
      )}
      <List
        size="small"
        dataSource={items}
        renderItem={(item) => (
          <List.Item>
            <div>
              <Typography.Text strong>
                {item.kind} ({item.source})
              </Typography.Text>
              <div>{item.summary}</div>
              {item.availability === 'unavailable' && (
                <Typography.Text type="secondary">不可用</Typography.Text>
              )}
            </div>
          </List.Item>
        )}
      />
    </div>
  )
}
