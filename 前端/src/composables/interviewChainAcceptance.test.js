import { afterEach, describe, expect, it, vi } from 'vitest'
import { useAnswerAggregation } from './useAnswerAggregation'
import { AudioGateState, useInterviewAudioGate } from './useInterviewAudioGate'
import { ConversationState, useInterviewConversation } from './useInterviewConversation'

describe('three-question interview chain acceptance', () => {
  afterEach(() => vi.useRealTimers())

  it('isolates speech, answer and guard ownership across three questions', () => {
    vi.useFakeTimers()
    let questionId = 1
    const conversation = useInterviewConversation({ getQuestionId: () => questionId })
    const aggregation = useAnswerAggregation({ logger: { info: vi.fn() } })
    const answerIds = []
    const submittedAnswers = []
    const gate = useInterviewAudioGate({
      playbackGuardMs: 500,
      logger: { info: vi.fn() },
      onGuardCompleted: ({ speechId }) => {
        gate.open('playback-guard-completed', { speechId })
        conversation.transitionTo(ConversationState.LISTENING, 'digital-human.playback-guard-completed')
      },
    })

    conversation.transitionTo(ConversationState.WAITING, 'question.displayed')
    let staleSegment = null
    for (questionId = 1; questionId <= 3; questionId++) {
      const speechId = `speech-${questionId}`
      conversation.handleSpeechLifecycle('speech-requested', { speechId })
      gate.blockForTransition(speechId)
      conversation.handleSpeechLifecycle('speech-accepted', { speechId })
      expect(conversation.currentState.value).not.toBe(ConversationState.SPEAKING)

      conversation.handleSpeechLifecycle('speech-started', { speechId })
      gate.blockForSpeaking(speechId)
      expect(conversation.currentState.value).toBe(ConversationState.SPEAKING)
      expect(gate.gateState.value).toBe(AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN)

      conversation.handleSpeechLifecycle('speech-ended', { speechId })
      gate.startPlaybackGuard(speechId)
      expect(gate.gateState.value).toBe(AudioGateState.BLOCKED_DURING_TRANSITION)
      vi.advanceTimersByTime(499)
      expect(gate.gateState.value).toBe(AudioGateState.BLOCKED_DURING_TRANSITION)
      vi.advanceTimersByTime(1)
      expect(conversation.currentState.value).toBe(ConversationState.LISTENING)
      expect(gate.gateState.value).toBe(AudioGateState.ACCEPTING_CANDIDATE_AUDIO)

      const answer = aggregation.createAnswer({ sessionId: 7, questionId })
      answerIds.push(answer.answerId)
      if (staleSegment) {
        expect(aggregation.resolveSegment(staleSegment.answerId, staleSegment.segmentId, '迟到结果')).toBe(false)
      }
      aggregation.markSpeechStarted(questionId * 1000)
      aggregation.markSpeechEnded(questionId * 1000 + 500)
      const segment = aggregation.addSegment({ reason: 'silence' })
      expect(aggregation.resolveSegment(answer.answerId, segment.segmentId, `第${questionId}题回答`)).toBe(true)
      expect(aggregation.beginFinalization('auto').acquired).toBe(true)
      expect(aggregation.beginFinalization('auto').acquired).toBe(false)
      const submission = aggregation.markSubmitting()
      expect(submission.answerId).toBe(answer.answerId)
      submittedAnswers.push(submission.submissionId)
      aggregation.markSubmitSucceeded()
      staleSegment = segment

      if (questionId < 3) {
        conversation.transitionTo(ConversationState.THINKING, 'answer.submitted')
        conversation.transitionTo(ConversationState.WAITING, 'next-question.received')
      }
    }

    expect(new Set(answerIds).size).toBe(3)
    expect(new Set(submittedAnswers).size).toBe(3)
    gate.dispose('interview-ended')
    aggregation.dispose()
    expect(gate.gateState.value).toBe(AudioGateState.BLOCKED_WHEN_INTERVIEW_INACTIVE)
    expect(aggregation.currentAnswer.value).toBeNull()
  })
})
