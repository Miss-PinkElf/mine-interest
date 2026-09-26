import { Typography } from 'antd'
import { useEffect, useMemo, useState } from 'react'

import { REVIEW_WORKSPACE_TITLE } from '../../constants/copy'
import type { SegmentDto } from '../../api/jobs'
import { EvidencePanel, type EvidenceItem } from '../../components/EvidencePanel'
import { SegmentList } from './SegmentList'
import { SegmentEditor } from './SegmentEditor'
import styles from './index.module.scss'

export type ReviewJobView = {
  id: string
  segments: SegmentDto[]
  evidenceBySegment: Record<string, EvidenceItem[]>
}

export type ReviewWorkspaceProps = {
  job: ReviewJobView
  splitSegment?: (segmentId: string, atSeconds: number) => Promise<unknown> | unknown
  confirmSegment?: (segmentId: string, editedText: string | null) => Promise<unknown> | unknown
  onTextEdit?: (segmentId: string, text: string) => void
}

export function ReviewWorkspace({
  job,
  splitSegment,
  confirmSegment,
  onTextEdit,
}: ReviewWorkspaceProps) {
  const [activeId, setActiveId] = useState(job.segments[0]?.id)
  const [currentTime, setCurrentTime] = useState(0)
  const [segments, setSegments] = useState(job.segments)

  useEffect(() => {
    // 后台转写完成后，父组件传入的片段会替换创建任务时的空列表。
    setSegments(job.segments)
  }, [job.segments])

  const active = useMemo(
    () => segments.find((item) => item.id === activeId) ?? segments[0] ?? null,
    [segments, activeId],
  )
  const evidence = active ? job.evidenceBySegment[active.id] || [] : []

  return (
    <div className={styles.workspace}>
      <Typography.Title level={3}>{REVIEW_WORKSPACE_TITLE}</Typography.Title>
      <div className={styles.columns}>
        <div className={styles.column}>
          <SegmentList
            segments={segments}
            activeId={active?.id}
            onSelect={setActiveId}
          />
        </div>
        <div className={styles.column}>
          <SegmentEditor
            segment={active}
            currentTime={currentTime}
            onCurrentTimeChange={setCurrentTime}
            onConfirm={() => active && confirmSegment?.(active.id, active.edited_text)}
            onSplit={(atSeconds) => active && splitSegment?.(active.id, atSeconds)}
            onTextChange={(text) => {
              if (!active) return
              setSegments((prev) =>
                prev.map((item) =>
                  item.id === active.id
                    ? { ...item, edited_text: text, final_text: text }
                    : item,
                ),
              )
              onTextEdit?.(active.id, text)
            }}
          />
        </div>
        <div className={styles.column}>
          <EvidencePanel items={evidence} />
        </div>
      </div>
    </div>
  )
}
