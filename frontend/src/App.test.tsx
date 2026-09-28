import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import { CONFIRM_SEGMENT_LABEL, DEMO_MODE_LABEL, DEMO_MODE_NOTICE, EXPORT_MARKDOWN_LABEL, REVIEW_WORKSPACE_TITLE, SEGMENT_CONFIRMED_MESSAGE, START_TASK_LABEL } from './constants/copy'
import { ACTIVE_JOB_SESSION_KEY } from './constants/task'

const jobApi = vi.hoisted(() => ({
  createJob: vi.fn(),
  getJob: vi.fn(),
  listSegments: vi.fn(),
  confirmSegment: vi.fn(),
  exportJob: vi.fn(),
}))

vi.mock('./api/jobs', () => jobApi)

const reviewApi = vi.hoisted(() => ({
  splitSegment: vi.fn(),
  editSegmentText: vi.fn(),
}))

vi.mock('./api/review', () => reviewApi)

const reviewJob = {
  id: 'demo-job',
  source_media_path: 'sample.mp4',
  status: 'review',
  is_demo: true,
  created_at: new Date().toISOString(),
}

const demoSegment = {
  id: 'demo-segment',
  raw_text: '演示片段文本',
  edited_text: null,
  final_text: '演示片段文本',
  start_seconds: 0,
  end_seconds: 2,
  speaker_id: null,
  review_status: 'pending',
  analysis_status: 'pending',
}

describe('App 自动演示任务', () => {
  beforeEach(() => {
    window.sessionStorage.clear()
    vi.clearAllMocks()
    reviewApi.editSegmentText.mockResolvedValue(demoSegment)
    jobApi.confirmSegment.mockResolvedValue(demoSegment)
    jobApi.createJob.mockResolvedValue({ ...reviewJob, status: 'pending' })
    jobApi.getJob.mockResolvedValue(reviewJob)
    jobApi.listSegments.mockResolvedValue([demoSegment])
  })

  it('uploads in demo mode and shows segments after the job reaches review', async () => {
    const user = userEvent.setup()
    render(<App />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    await user.upload(input, new File(['media'], 'sample.mp4', { type: 'video/mp4' }))
    await user.click(screen.getByRole('checkbox', { name: DEMO_MODE_LABEL }))
    await user.click(screen.getByRole('button', { name: START_TASK_LABEL }))

    await waitFor(() => expect(jobApi.getJob).toHaveBeenCalledWith(reviewJob.id))
    await user.click(screen.getByRole('tab', { name: REVIEW_WORKSPACE_TITLE }))
    expect((await screen.findAllByText(demoSegment.raw_text))[0]).toBeVisible()
    expect(within(screen.getByRole('tabpanel')).getByText(DEMO_MODE_NOTICE)).toBeVisible()
    expect(window.sessionStorage.getItem(ACTIVE_JOB_SESSION_KEY)).toBe(reviewJob.id)
  })

  it('restores the demo notice and segments after browser refresh', async () => {
    window.sessionStorage.setItem(ACTIVE_JOB_SESSION_KEY, reviewJob.id)
    const user = userEvent.setup()
    render(<App />)

    await waitFor(() => expect(jobApi.listSegments).toHaveBeenCalledWith(reviewJob.id))
    await user.click(screen.getByRole('tab', { name: REVIEW_WORKSPACE_TITLE }))
    expect((await screen.findAllByText(demoSegment.raw_text))[0]).toBeVisible()
    expect(within(screen.getByRole('tabpanel')).getByText(DEMO_MODE_NOTICE)).toBeVisible()
  })

  it('ignores the previous job segments when a new upload starts', async () => {
    const user = userEvent.setup()
    const nextJob = { ...reviewJob, id: 'next-job' }
    const nextSegment = { ...demoSegment, id: 'next-segment', raw_text: '新任务片段', final_text: '新任务片段' }
    let resolvePreviousSegments!: (segments: typeof demoSegment[]) => void
    const delayedPreviousSegments = new Promise<typeof demoSegment[]>((resolve) => {
      resolvePreviousSegments = resolve
    })

    jobApi.createJob
      .mockResolvedValueOnce({ ...reviewJob, status: 'pending' })
      .mockResolvedValueOnce({ ...nextJob, status: 'pending' })
    jobApi.getJob.mockImplementation((jobId: string) =>
      Promise.resolve(jobId === nextJob.id ? nextJob : reviewJob),
    )
    jobApi.listSegments.mockImplementation((jobId: string) =>
      jobId === reviewJob.id ? delayedPreviousSegments : Promise.resolve([nextSegment]),
    )

    render(<App />)
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    await user.upload(input, new File(['a'], 'first.mp4', { type: 'video/mp4' }))
    await user.click(screen.getByRole('checkbox', { name: DEMO_MODE_LABEL }))
    await user.click(screen.getByRole('button', { name: START_TASK_LABEL }))
    await waitFor(() => expect(jobApi.listSegments).toHaveBeenCalledWith(reviewJob.id))

    await user.upload(input, new File(['b'], 'second.mp4', { type: 'video/mp4' }))
    await user.click(screen.getByRole('button', { name: START_TASK_LABEL }))
    await waitFor(() => expect(jobApi.listSegments).toHaveBeenCalledWith(nextJob.id))

    resolvePreviousSegments([{ ...demoSegment, review_status: 'confirmed' }])
    await user.click(screen.getByRole('tab', { name: REVIEW_WORKSPACE_TITLE }))
    expect((await screen.findAllByText(nextSegment.raw_text))[0]).toBeVisible()
    expect(screen.queryByText(demoSegment.raw_text)).not.toBeInTheDocument()

    await user.click(screen.getByRole('tab', { name: '任务' }))
    expect(screen.getByRole('button', { name: EXPORT_MARKDOWN_LABEL })).toBeDisabled()
  })

  it('saves edited text before confirming a segment', async () => {
    const user = userEvent.setup()
    const revisedSegment = {
      ...demoSegment,
      edited_text: '人工修订后的文本',
      final_text: '人工修订后的文本',
      review_status: 'confirmed',
    }
    jobApi.listSegments
      .mockResolvedValueOnce([demoSegment])
      .mockResolvedValueOnce([revisedSegment])
    render(<App />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    await user.upload(input, new File(['media'], 'sample.mp4', { type: 'video/mp4' }))
    await user.click(screen.getByRole('checkbox', { name: DEMO_MODE_LABEL }))
    await user.click(screen.getByRole('button', { name: START_TASK_LABEL }))
    await user.click(screen.getByRole('tab', { name: REVIEW_WORKSPACE_TITLE }))

    const editor = await screen.findByRole('textbox')
    await user.clear(editor)
    await user.type(editor, revisedSegment.edited_text)
    await user.click(screen.getByRole('button', { name: CONFIRM_SEGMENT_LABEL }))

    await waitFor(() => {
      expect(reviewApi.editSegmentText).toHaveBeenCalledWith(demoSegment.id, revisedSegment.edited_text)
      expect(jobApi.confirmSegment).toHaveBeenCalledWith(demoSegment.id)
    })
    expect(reviewApi.editSegmentText.mock.invocationCallOrder[0]).toBeLessThan(
      jobApi.confirmSegment.mock.invocationCallOrder[0],
    )
  })

  it('does not confirm when saving edited text fails', async () => {
    const user = userEvent.setup()
    reviewApi.editSegmentText.mockRejectedValueOnce(new Error('保存失败'))
    render(<App />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    await user.upload(input, new File(['media'], 'sample.mp4', { type: 'video/mp4' }))
    await user.click(screen.getByRole('checkbox', { name: DEMO_MODE_LABEL }))
    await user.click(screen.getByRole('button', { name: START_TASK_LABEL }))
    await user.click(screen.getByRole('tab', { name: REVIEW_WORKSPACE_TITLE }))

    const editor = await screen.findByRole('textbox')
    await user.clear(editor)
    await user.type(editor, '修订失败场景')
    await user.click(screen.getByRole('button', { name: CONFIRM_SEGMENT_LABEL }))

    await waitFor(() => expect(reviewApi.editSegmentText).toHaveBeenCalled())
    expect(jobApi.confirmSegment).not.toHaveBeenCalled()
  })

  it('shows the confirmed job status after the final segment is confirmed', async () => {
    window.sessionStorage.setItem(ACTIVE_JOB_SESSION_KEY, reviewJob.id)
    const confirmedSegment = { ...demoSegment, review_status: 'confirmed' }
    jobApi.getJob.mockImplementation(() =>
      Promise.resolve(jobApi.confirmSegment.mock.calls.length ? { ...reviewJob, status: 'confirmed' } : reviewJob),
    )
    jobApi.listSegments.mockImplementation(() =>
      Promise.resolve(jobApi.confirmSegment.mock.calls.length ? [confirmedSegment] : [demoSegment]),
    )

    const user = userEvent.setup()
    render(<App />)
    await user.click(screen.getByRole('tab', { name: REVIEW_WORKSPACE_TITLE }))
    await screen.findByRole('button', { name: CONFIRM_SEGMENT_LABEL })
    await user.click(screen.getByRole('button', { name: CONFIRM_SEGMENT_LABEL }))

    await user.click(screen.getByRole('tab', { name: '任务' }))
    expect(await within(screen.getByRole('tabpanel', { name: '任务' })).findByText('已确认')).toBeVisible()
    expect((await screen.findAllByText(SEGMENT_CONFIRMED_MESSAGE))[0]).toBeVisible()
  })

  it('shows the exported job status immediately after export', async () => {
    window.sessionStorage.setItem(ACTIVE_JOB_SESSION_KEY, reviewJob.id)
    jobApi.getJob.mockImplementation(() =>
      Promise.resolve({ ...reviewJob, status: jobApi.exportJob.mock.calls.length ? 'exported' : 'confirmed' }),
    )
    jobApi.listSegments.mockResolvedValue([{ ...demoSegment, review_status: 'confirmed' }])
    jobApi.exportJob.mockResolvedValue({ artifact_path: 'artifacts/demo.md' })

    const user = userEvent.setup()
    render(<App />)
    const exportButton = await screen.findByRole('button', { name: EXPORT_MARKDOWN_LABEL })
    await waitFor(() => expect(exportButton).toBeEnabled())
    await user.click(exportButton)

    expect(await within(screen.getByRole('tabpanel', { name: '任务' })).findByText('已导出')).toBeVisible()
  })
})
