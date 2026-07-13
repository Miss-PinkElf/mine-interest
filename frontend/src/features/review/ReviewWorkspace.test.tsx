import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import {
  CONFLICT_REVIEW_COPY,
  SPLIT_SEGMENT_LABEL,
} from '../../constants/copy'
import { ReviewWorkspace } from './ReviewWorkspace'

const conflictingJob = {
  id: 'job-1',
  segments: [
    {
      id: 'seg-1',
      raw_text: '第一段',
      edited_text: null,
      final_text: '第一段',
      start_seconds: 0,
      end_seconds: 1,
      speaker_id: 's0',
      review_status: 'pending',
      analysis_status: 'current',
    },
    {
      id: 'seg-2',
      raw_text: '第二段',
      edited_text: null,
      final_text: '第二段',
      start_seconds: 1,
      end_seconds: 3,
      speaker_id: 's1',
      review_status: 'pending',
      analysis_status: 'current',
    },
  ],
  evidenceBySegment: {
    'seg-1': [],
    'seg-2': [
      {
        id: 'ev-1',
        kind: 'audio_emotion',
        source: 'specialized_model',
        summary: 'neutral',
        conflict: true,
      },
    ],
  },
}

describe('ReviewWorkspace', () => {
  it('shows conflicting evidence and sends a split request', async () => {
    const user = userEvent.setup()
    const splitSegment = vi.fn()
    render(
      <ReviewWorkspace
        job={conflictingJob}
        splitSegment={splitSegment}
      />,
    )

    await user.click(screen.getByText('第二段'))
    expect(screen.getByText(CONFLICT_REVIEW_COPY)).toBeVisible()
    await user.click(screen.getByRole('button', { name: SPLIT_SEGMENT_LABEL }))
    expect(splitSegment).toHaveBeenCalledWith('seg-2', expect.any(Number))
  })
})
