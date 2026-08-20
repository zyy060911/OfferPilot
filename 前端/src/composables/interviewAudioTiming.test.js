import { describe, expect, it, vi } from 'vitest'
import { resolveInterviewAudioTiming } from './interviewAudioTiming'

describe('interview audio timing', () => {
  it('uses the three conservative silence defaults', () => {
    expect(resolveInterviewAudioTiming({})).toMatchObject({
      segmentSilenceMs: 3000,
      answerFinishMs: 7000,
      answerConfirmMs: 800,
      maxSegmentMs: 28000,
    })
  })

  it('falls back and warns for invalid ordering', () => {
    const logger = { warn: vi.fn() }
    const timing = resolveInterviewAudioTiming({ VITE_SEGMENT_SILENCE_MS: '4000', VITE_ANSWER_FINISH_MS: '2000' }, logger)
    expect(timing.answerFinishMs).toBeGreaterThan(timing.segmentSilenceMs)
    expect(logger.warn).toHaveBeenCalled()
  })
})
