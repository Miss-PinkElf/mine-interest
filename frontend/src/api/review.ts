/** 审核相关 API。 */

import { requestJson } from './client'
import type { SegmentDto } from './jobs'

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
