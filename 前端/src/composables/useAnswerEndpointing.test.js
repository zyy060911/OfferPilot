import { afterEach, describe, expect, it, vi } from 'vitest'
import { useAnswerEndpointing } from './useAnswerEndpointing'

const timing = { answerFinishMs: 3000, answerConfirmMs: 800 }

afterEach(() => vi.useRealTimers())

function harness(eligible = () => true, evaluateConfirmation = () => null) {
  vi.useFakeTimers()
  let now = 1500
  const possible = vi.fn()
  const cancelled = vi.fn()
  const confirmed = vi.fn()
  const endpointing = useAnswerEndpointing({
    timing, now: () => now, isEligible: eligible, evaluateConfirmation,
    onPossibleEnd: possible, onPossibleEndCancelled: cancelled, onConfirmed: confirmed,
    logger: { info: vi.fn() },
  })
  const context = { answerId: 'a1', answerEpoch: 1, endedAt: 0 }
  return { endpointing, context, possible, cancelled, confirmed, setNow: (value) => { now = value } }
}

describe('useAnswerEndpointing', () => {
  it('enters POSSIBLE_END after total long silence and confirms later', () => {
    const h = harness()
    h.endpointing.speechEnded(h.context)
    vi.advanceTimersByTime(1499)
    expect(h.possible).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1)
    expect(h.possible).toHaveBeenCalledOnce()
    vi.advanceTimersByTime(800)
    expect(h.confirmed).toHaveBeenCalledOnce()
  })

  it('reliable new speech cancels POSSIBLE_END but a noise event never reaches this API', () => {
    const h = harness()
    h.endpointing.speechEnded(h.context)
    vi.advanceTimersByTime(1500)
    h.endpointing.speechStarted({ ...h.context, startedAt: 3200 })
    expect(h.cancelled).toHaveBeenCalledOnce()
    vi.advanceTimersByTime(800)
    expect(h.confirmed).not.toHaveBeenCalled()
  })

  it('does not run while speaking/guard makes the context ineligible', () => {
    const h = harness(() => false)
    expect(h.endpointing.speechEnded(h.context)).toBe(false)
    vi.runAllTimers()
    expect(h.possible).not.toHaveBeenCalled()
  })

  it('dispose cancels timers and stale question callbacks', () => {
    const h = harness()
    h.endpointing.speechEnded(h.context)
    h.endpointing.dispose()
    vi.runAllTimers()
    expect(h.possible).not.toHaveBeenCalled()
  })

  it('extends only the confirmation period when completeness is low', () => {
    const evaluate = vi.fn(() => ({
      score: 0.2,
      classification: 'INCOMPLETE',
      signals: [{ code: 'dangling-expression' }],
      recommendedConfirmMs: 2000,
      reason: 'incomplete:dangling-expression',
    }))
    const h = harness(() => true, evaluate)
    h.endpointing.speechEnded(h.context)
    vi.advanceTimersByTime(1499)
    expect(evaluate).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1)
    expect(evaluate).toHaveBeenCalledOnce()
    expect(h.possible).toHaveBeenCalledOnce()
    vi.advanceTimersByTime(1999)
    expect(h.confirmed).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1)
    expect(h.confirmed).toHaveBeenCalledOnce()
  })

  it('new speech cancels an extended semantic confirmation timer', () => {
    const h = harness(() => true, () => ({ recommendedConfirmMs: 2000, classification: 'INCOMPLETE' }))
    h.endpointing.speechEnded(h.context)
    vi.advanceTimersByTime(1500)
    h.endpointing.speechStarted({ ...h.context, startedAt: 3200 })
    vi.advanceTimersByTime(2000)
    expect(h.cancelled).toHaveBeenCalledOnce()
    expect(h.confirmed).not.toHaveBeenCalled()
  })

  it('falls back to 800ms when semantic evaluation fails or asks for a shorter pause', () => {
    const thrown = harness(() => true, () => { throw new Error('broken rule') })
    thrown.endpointing.speechEnded(thrown.context)
    vi.advanceTimersByTime(1500 + 799)
    expect(thrown.confirmed).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1)
    expect(thrown.confirmed).toHaveBeenCalledOnce()

    const shortened = harness(() => true, () => ({ recommendedConfirmMs: 100, classification: 'COMPLETE' }))
    shortened.endpointing.speechEnded(shortened.context)
    vi.advanceTimersByTime(1500 + 799)
    expect(shortened.confirmed).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1)
    expect(shortened.confirmed).toHaveBeenCalledOnce()
  })
})
