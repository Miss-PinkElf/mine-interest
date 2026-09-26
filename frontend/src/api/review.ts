/** 审核相关 API。 */

import { requestJson } from './client'
import type { SegmentDto } from './jobs'
import { API_SEGMENTS_PATH, SEGMENT_TEXT_SUFFIX } from '../constants/task'

/** 保存片段人工修订，供确认和导出使用。 */
export async function editSegmentText(
  segmentId: string,
  editedText: string,
): Promise<SegmentDto> {
  return requestJson<SegmentDto>(`${API_SEGMENTS_PATH}/${segmentId}/${SEGMENT_TEXT_SUFFIX}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edited_text: editedText }),
  })
}

export async function splitSegment(
  segmentId: string,
  atSeconds: number,
): Promise<SegmentDto[]> {
  return requestJson<SegmentDto[]>(`/api/segments/${segmentId}/split`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ at_seconds: atSeconds }),
  })
}

export async function mergeSegments(
  leftSegmentId: string,
  rightSegmentId: string,
): Promise<SegmentDto> {
  return requestJson<SegmentDto>('/api/segments/merge', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      left_segment_id: leftSegmentId,
      right_segment_id: rightSegmentId,
    }),
  })
}
