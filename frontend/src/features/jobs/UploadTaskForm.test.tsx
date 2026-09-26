import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { DEMO_MODE_LABEL, START_TASK_LABEL, UPLOAD_MEDIA_LABEL } from '../../constants/copy'
import { UploadTaskForm } from './UploadTaskForm'

describe('UploadTaskForm', () => {
  it('submits a selected local media file', async () => {
    const user = userEvent.setup()
    const createJob = vi.fn().mockResolvedValue({
      id: 'job-1',
      source_media_path: 'sample.mp4',
      status: 'pending',
      created_at: new Date().toISOString(),
    })

    render(<UploadTaskForm createJob={createJob} />)

    const file = new File(['x'], 'sample.mp4', { type: 'video/mp4' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    expect(input).toBeTruthy()
    await user.upload(input, file)
    expect(screen.getByRole('button', { name: START_TASK_LABEL })).toBeDisabled()
    await user.click(screen.getByRole('checkbox', { name: DEMO_MODE_LABEL }))
    await user.click(screen.getByRole('button', { name: START_TASK_LABEL }))

    expect(createJob).toHaveBeenCalled()
    const [uploaded] = createJob.mock.calls[0]
    expect(uploaded).toBeInstanceOf(File)
    expect(uploaded.name).toBe('sample.mp4')
    expect(createJob.mock.calls[0][1]).toBe(true)
  })
})
