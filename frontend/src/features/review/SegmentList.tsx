import { List, Tag } from 'antd'

import type { SegmentDto } from '../../api/jobs'
import styles from './index.module.scss'

export type SegmentListProps = {
  segments: SegmentDto[]
  activeId?: string
  onSelect: (segmentId: string) => void
}

export function SegmentList({ segments, activeId, onSelect }: SegmentListProps) {
  return (
    <List
      className={styles.segmentList}
      dataSource={segments}
      renderItem={(item) => (
        <List.Item
          className={item.id === activeId ? styles.activeItem : undefined}
          onClick={() => onSelect(item.id)}
        >
          <div>
            <div>
              {item.start_seconds.toFixed(1)}s - {item.end_seconds.toFixed(1)}s
            </div>
            <div>{item.final_text}</div>
            <Tag>{item.review_status}</Tag>
          </div>
        </List.Item>
      )}
    />
  )
}
