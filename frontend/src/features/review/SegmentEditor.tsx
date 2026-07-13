import { Button, Input, Space, Typography } from 'antd'

import {
  CONFIRM_SEGMENT_LABEL,
  EDITED_TEXT_LABEL,
  RAW_TEXT_LABEL,
  SPLIT_SEGMENT_LABEL,
} from '../../constants/copy'
import type { SegmentDto } from '../../api/jobs'
import { SegmentAudioPlayer } from '../../components/SegmentAudioPlayer'
import styles from './index.module.scss'

export type SegmentEditorProps = {
  segment: SegmentDto | null
  currentTime: number
  onCurrentTimeChange: (value: number) => void
  onConfirm: () => void
  onSplit: (atSeconds: number) => void
  onTextChange: (text: string) => void
}

export function SegmentEditor({
  segment,
  currentTime,
  onCurrentTimeChange,
  onConfirm,
  onSplit,
  onTextChange,
}: SegmentEditorProps) {
  if (!segment) {
    return <div className={styles.editorEmpty}>请选择片段</div>
  }

  return (
    <div className={styles.editor}>
      <Typography.Text type="secondary">
        说话人：{segment.speaker_id || '-'}
      </Typography.Text>
      <SegmentAudioPlayer onTimeUpdate={onCurrentTimeChange} />
      <div>
        <Typography.Text strong>{RAW_TEXT_LABEL}</Typography.Text>
        <div>{segment.raw_text}</div>
      </div>
      <div>
        <Typography.Text strong>{EDITED_TEXT_LABEL}</Typography.Text>
        <Input.TextArea
          value={segment.edited_text ?? segment.raw_text}
          onChange={(event) => onTextChange(event.target.value)}
          rows={4}
        />
      </div>
      <Space>
        <Button onClick={() => onSplit(currentTime)}>{SPLIT_SEGMENT_LABEL}</Button>
        <Button type="primary" onClick={onConfirm}>
          {CONFIRM_SEGMENT_LABEL}
        </Button>
      </Space>
    </div>
  )
}
