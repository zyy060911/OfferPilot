import { computed, readonly, ref } from 'vue'

function newId(prefix) {
  const uuid = globalThis.crypto?.randomUUID?.()
  return uuid ? `${prefix}-${uuid}` : `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`
}

function normalizeText(value) {
  return String(value || '').trim().replace(/\s+/g, ' ')
}

export function useAnswerAggregation({ now = () => performance.now(), logger = console } = {}) {
  const currentAnswer = ref(null)
  let epoch = 0

  const transcript = computed(() => mergeTranscript(currentAnswer.value))

  function log(event, metadata = {}) {
    const answer = currentAnswer.value
    logger.info?.('[AnswerAggregation]', {
      event,
      sessionId: answer?.sessionId ?? null,
      questionId: answer?.questionId ?? null,
      answerId: answer?.answerId ?? null,
      answerEpoch: answer?.answerEpoch ?? null,
      pendingSegmentCount: answer?.pendingSegmentCount ?? 0,
      timestamp: new Date().toISOString(),
      ...metadata,
    })
  }

  function createAnswer({ sessionId, questionId }) {
    epoch++
    currentAnswer.value = {
      answerId: newId('answer'),
      sessionId,
      questionId,
      answerEpoch: epoch,
      startedAt: null,
      lastSpeechStartedAt: null,
      lastSpeechEndedAt: null,
      segmentSequence: 0,
      segments: [],
      pendingSegmentCount: 0,
      failedSegments: [],
      finalizationState: 'collecting',
      submitState: 'idle',
    }
    log('answer-created')
    return currentAnswer.value
  }

  function markSpeechStarted(at = now()) {
    const answer = currentAnswer.value
    if (!answer || answer.finalizationState === 'finalizing') return false
    if (answer.startedAt == null) answer.startedAt = at
    answer.lastSpeechStartedAt = at
    log('candidate-speech-started')
    return true
  }

  function markSpeechEnded(at = now()) {
    if (currentAnswer.value?.startedAt == null) return false
    currentAnswer.value.lastSpeechEndedAt = at
    log('candidate-speech-ended')
    return true
  }

  function addSegment(metadata = {}) {
    const answer = currentAnswer.value
    if (!answer || answer.finalizationState === 'disposed') return null
    const segment = {
      answerId: answer.answerId,
      segmentId: newId('segment'),
      sequence: ++answer.segmentSequence,
      captureStartedAt: metadata.captureStartedAt ?? null,
      captureEndedAt: metadata.captureEndedAt ?? now(),
      triggerReason: normalizeTrigger(metadata.reason),
      transcriptionState: 'pending',
      transcript: '',
      retryCount: 0,
    }
    answer.segments.push(segment)
    answer.pendingSegmentCount++
    log('segment-finalized', { segmentId: segment.segmentId, sequence: segment.sequence, triggerReason: segment.triggerReason })
    return segment
  }

  function settleSegment(answerId, segmentId, state, text = '', error = null) {
    const answer = currentAnswer.value
    if (!answer || answer.answerId !== answerId) {
      log('stale-asr-result-ignored', { staleAnswerId: answerId, segmentId })
      return false
    }
    const segment = answer.segments.find((item) => item.segmentId === segmentId)
    if (!segment || !['pending', 'timed-out'].includes(segment.transcriptionState)) return false
    const wasPending = segment.transcriptionState === 'pending'
    segment.transcriptionState = state
    segment.transcript = state === 'completed' ? normalizeText(text) : segment.transcript
    segment.error = error ? String(error?.message || error) : null
    if (wasPending) answer.pendingSegmentCount = Math.max(0, answer.pendingSegmentCount - 1)
    if (state === 'completed') answer.failedSegments = answer.failedSegments.filter((id) => id !== segmentId)
    if (state === 'failed' && !answer.failedSegments.includes(segmentId)) answer.failedSegments.push(segmentId)
    return true
  }

  const resolveSegment = (answerId, segmentId, text) => settleSegment(answerId, segmentId, 'completed', text)
  const failSegment = (answerId, segmentId, error) => settleSegment(answerId, segmentId, 'failed', '', error)

  function retrySegment(segmentId) {
    const answer = currentAnswer.value
    const segment = answer?.segments.find((item) => item.segmentId === segmentId)
    if (!segment || !['failed', 'timed-out'].includes(segment.transcriptionState)) return null
    segment.transcriptionState = 'pending'
    segment.retryCount++
    segment.error = null
    answer.failedSegments = answer.failedSegments.filter((id) => id !== segmentId)
    answer.pendingSegmentCount++
    return segment
  }

  function ignoreFailedSegments() {
    const answer = currentAnswer.value
    if (!answer) return
    for (const segment of answer.segments) {
      if (['failed', 'timed-out'].includes(segment.transcriptionState)) segment.transcriptionState = 'ignored'
    }
    answer.failedSegments = []
  }

  function failPendingSegments(error = 'ASR finalization timeout') {
    const answer = currentAnswer.value
    if (!answer) return 0
    const pending = answer.segments.filter((segment) => segment.transcriptionState === 'pending')
    for (const segment of pending) {
      segment.transcriptionState = 'timed-out'
      segment.error = String(error)
      answer.pendingSegmentCount = Math.max(0, answer.pendingSegmentCount - 1)
      if (!answer.failedSegments.includes(segment.segmentId)) answer.failedSegments.push(segment.segmentId)
    }
    return pending.length
  }

  function beginFinalization(source) {
    const answer = currentAnswer.value
    if (!answer || answer.startedAt == null) return { acquired: false, reason: 'no-valid-speech' }
    if (!['collecting', 'recoverable-error'].includes(answer.finalizationState)) {
      log('duplicate-submit-blocked', { source })
      return { acquired: false, reason: 'already-finalizing' }
    }
    answer.finalizationState = 'finalizing'
    answer.submitState = 'waiting-asr'
    answer.finalizationSource = source
    answer.submissionId ||= newId('submission')
    log('answer-finalization-started', { source })
    return { acquired: true, answerId: answer.answerId, answerEpoch: answer.answerEpoch }
  }

  function markSubmitting() {
    const answer = currentAnswer.value
    if (!answer || answer.finalizationState !== 'finalizing' || answer.pendingSegmentCount) return null
    if (answer.failedSegments.length) return null
    const answerText = mergeTranscript(answer)
    if (!answerText) {
      log('empty-answer-blocked')
      return null
    }
    answer.submitState = 'submitting'
    return {
      answerId: answer.answerId,
      submissionId: answer.submissionId,
      questionId: answer.questionId,
      answer: answerText,
      source: answer.finalizationSource,
    }
  }

  function markSubmitSucceeded() {
    if (!currentAnswer.value) return
    currentAnswer.value.finalizationState = 'finalized'
    currentAnswer.value.submitState = 'succeeded'
    log('answer-submit-succeeded')
  }

  function markRecoverableError(reason) {
    if (!currentAnswer.value) return
    currentAnswer.value.finalizationState = 'recoverable-error'
    currentAnswer.value.submitState = 'failed'
    currentAnswer.value.finalizationError = reason
    log('answer-submit-failed', { reason })
  }

  function dispose() {
    epoch++
    if (currentAnswer.value) currentAnswer.value.finalizationState = 'disposed'
    currentAnswer.value = null
  }

  return {
    currentAnswer: readonly(currentAnswer), transcript,
    createAnswer, markSpeechStarted, markSpeechEnded, addSegment,
    resolveSegment, failSegment, retrySegment, ignoreFailedSegments, failPendingSegments,
    beginFinalization, markSubmitting, markSubmitSucceeded, markRecoverableError, dispose,
  }
}

export function mergeTranscript(answer) {
  if (!answer) return ''
  return answer.segments
    .filter((segment) => segment.transcriptionState === 'completed' && normalizeText(segment.transcript))
    .sort((left, right) => left.sequence - right.sequence)
    .map((segment) => normalizeText(segment.transcript))
    .join(' ')
    .trim()
}

function normalizeTrigger(reason) {
  if (reason === 'silence') return 'segment-silence'
  if (reason === 'max-duration') return 'max-duration'
  if (reason === 'manual-submit') return 'manual-submit'
  if (reason === 'auto-finish') return 'auto-finish'
  return reason || 'segment-silence'
}
