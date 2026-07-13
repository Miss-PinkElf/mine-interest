/** 任务相关 API 客户端。 */

import { requestJson } from './client'
import { API_JOBS_PATH } from '../constants/task'

export type JobDto = {
  id: string
  source_media_path: string
  status: string
  created_at: string
  failed_stage?: string | null
  error_code?: string | null
  retryable?: boolean
}

export type SegmentDto = {
  id: string
  raw_text: string
  edited_text: string | null
  final_text: string
  start_seconds: number
  end_seconds: number
  speaker_id: string | null
  review_status: string
  analysis_status: string
}

export type ExportArtifactDto = {
  id: string
  job_id: string
  format: string
  artifact_path: string
  created_at: string
}

export async function createJob(file: File): Promise<JobDto> {
  const formData = new FormData()
  formData.append('file', file)
  return requestJson<JobDto>(API_JOBS_PATH, {
    method: 'POST',
    body: formData,
  })
}

export async function getJob(jobId: string): Promise<JobDto> {
  return requestJson<JobDto>(`${API_JOBS_PATH}/${jobId}`)
}

export async function listSegments(jobId: string): Promise<SegmentDto[]> {
  return requestJson<SegmentDto[]>(`${API_JOBS_PATH}/${jobId}/segments`)
}

export async function confirmSegment(segmentId: string): Promise<SegmentDto> {
  return requestJson<SegmentDto>(`/api/segments/${segmentId}/confirm`, {
    method: 'POST',
  })
}

export async function exportJob(
  jobId: string,
  format: 'markdown' | 'json',
): Promise<ExportArtifactDto> {
  return requestJson<ExportArtifactDto>(`${API_JOBS_PATH}/${jobId}/exports`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ format }),
  })
}
