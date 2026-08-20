import { describe, expect, it, vi } from 'vitest'
import { useAnswerAggregation } from './useAnswerAggregation'

function create() {
  const aggregation = useAnswerAggregation({ now: () => 100, logger: { info: vi.fn() } })
  aggregation.createAnswer({ sessionId: 7, questionId: 9 })
  aggregation.markSpeechStarted(10)
  return aggregation
}

describe('useAnswerAggregation', () => {
  it('keeps one answerId across silence and max-duration segments and merges by sequence', () => {
    const aggregation = create()
    const answerId = aggregation.currentAnswer.value.answerId
    const first = aggregation.addSegment({ reason: 'max-duration' })
    const second = aggregation.addSegment({ reason: 'silence' })
    expect(first.answerId).toBe(answerId)
    expect(second.answerId).toBe(answerId)
    aggregation.resolveSegment(answerId, second.segmentId, '第二段')
    aggregation.resolveSegment(answerId, first.segmentId, '第一段')
    expect(aggregation.transcript.value).toBe('第一段 第二段')
  })

  it('ignores stale ASR results after a new answer epoch', () => {
    const aggregation = create()
    const old = aggregation.addSegment({ reason: 'silence' })
    aggregation.createAnswer({ sessionId: 7, questionId: 10 })
    expect(aggregation.resolveSegment(old.answerId, old.segmentId, '迟到')).toBe(false)
    expect(aggregation.transcript.value).toBe('')
  })

  it('grants manual/auto finalization ownership only once and permits very short valid text', () => {
    const aggregation = create()
    const segment = aggregation.addSegment({ reason: 'silence' })
    aggregation.resolveSegment(segment.answerId, segment.segmentId, '是')
    expect(aggregation.beginFinalization('auto').acquired).toBe(true)
    expect(aggregation.beginFinalization('manual').acquired).toBe(false)
    expect(aggregation.markSubmitting().answer).toBe('是')
  })

  it('blocks empty text and exposes failed/timeout segments as recoverable', () => {
    const aggregation = create()
    const segment = aggregation.addSegment({ reason: 'silence' })
    aggregation.beginFinalization('auto')
    aggregation.failPendingSegments('timeout')
    expect(aggregation.currentAnswer.value.failedSegments).toEqual([segment.segmentId])
    aggregation.markRecoverableError('timeout')
    expect(aggregation.beginFinalization('retry').acquired).toBe(true)
    expect(aggregation.markSubmitting()).toBeNull()
  })

  it('accepts a successful ASR response that arrives after finalization timeout', () => {
    const aggregation = create()
    const segment = aggregation.addSegment({ reason: 'silence' })
    aggregation.beginFinalization('auto')
    aggregation.failPendingSegments('timeout')
    aggregation.markRecoverableError('timeout')

    expect(aggregation.resolveSegment(segment.answerId, segment.segmentId, '迟到但成功')).toBe(true)
    expect(aggregation.transcript.value).toBe('迟到但成功')
    expect(aggregation.currentAnswer.value.failedSegments).toEqual([])
    expect(aggregation.currentAnswer.value.pendingSegmentCount).toBe(0)
  })

  it('creates a new answerId and epoch for the next question', () => {
    const aggregation = create()
    const first = aggregation.currentAnswer.value
    aggregation.createAnswer({ sessionId: 7, questionId: 10 })
    expect(aggregation.currentAnswer.value.answerId).not.toBe(first.answerId)
    expect(aggregation.currentAnswer.value.answerEpoch).toBeGreaterThan(first.answerEpoch)
  })
})
