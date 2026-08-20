import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  ConversationState as S,
  canTransition,
  useInterviewConversation,
} from './useInterviewConversation'

describe('useInterviewConversation', () => {
  let logger
  let conversation

  beforeEach(() => {
    logger = {
      debug: vi.fn(),
      info: vi.fn(),
      warn: vi.fn(),
    }
    conversation = useInterviewConversation({
      getSessionId: () => 17,
      getQuestionId: () => 23,
      logger,
      dev: true,
    })
  })

  it('supports legal initialization and manual microphone transitions', () => {
    expect(conversation.currentState.value).toBe(S.CONNECTING)

    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.LISTENING, 'microphone.opened')

    expect(conversation.currentState.value).toBe(S.LISTENING)
    expect(conversation.previousState.value).toBe(S.WAITING)
    expect(conversation.transitionHistory.value.at(-1)).toMatchObject({
      fromState: S.WAITING,
      toState: S.LISTENING,
      event: 'microphone.opened',
      sessionId: 17,
      questionId: 23,
      accepted: true,
      changed: true,
    })
  })

  it('rejects illegal transitions without changing the current state', () => {
    const result = conversation.transitionTo(S.TRANSCRIBING, 'asr.processing.started')

    expect(result).toMatchObject({ accepted: false, changed: false })
    expect(conversation.currentState.value).toBe(S.CONNECTING)
    expect(logger.warn).toHaveBeenCalledOnce()
  })

  it('enters ENDPOINTING and TRANSCRIBING while an ASR segment is finalized', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.LISTENING, 'microphone.opened')
    conversation.transitionTo(S.ENDPOINTING, 'audio.endpointing.silence')
    conversation.transitionTo(S.TRANSCRIBING, 'asr.processing.started')

    expect(conversation.currentState.value).toBe(S.TRANSCRIBING)
    expect(conversation.transitionHistory.value.slice(-2).map((item) => item.toState))
      .toEqual([S.ENDPOINTING, S.TRANSCRIBING])
  })

  it('returns to LISTENING after an intermediate ASR segment completes', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.LISTENING, 'microphone.opened')
    conversation.transitionTo(S.ENDPOINTING, 'audio.endpointing.max-duration')
    conversation.transitionTo(S.TRANSCRIBING, 'asr.processing.started')
    conversation.transitionTo(S.LISTENING, 'asr.processing.completed')

    expect(conversation.currentState.value).toBe(S.LISTENING)
  })

  it('enters THINKING only after the complete answer is submitted', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.LISTENING, 'microphone.opened')
    conversation.transitionTo(S.THINKING, 'answer.submitted')

    expect(conversation.currentState.value).toBe(S.THINKING)
  })

  it('does not enter SPEAKING when a broadcast is only requested or accepted', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.THINKING, 'answer.submitted')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'speech-1' })
    conversation.handleSpeechLifecycle('speech-accepted', { speechId: 'speech-1' })

    expect(conversation.currentState.value).toBe(S.THINKING)
  })

  it('enters SPEAKING only on started and returns to WAITING on ended', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'speech-1' })
    conversation.handleSpeechLifecycle('speech-started', { speechId: 'speech-1' })
    expect(conversation.currentState.value).toBe(S.SPEAKING)

    conversation.handleSpeechLifecycle('speech-ended', { speechId: 'speech-1' })
    expect(conversation.currentState.value).toBe(S.WAITING)
    expect(conversation.activeSpeechId.value).toBeNull()
  })

  it('routes a current speech error to ERROR', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'speech-1' })
    conversation.handleSpeechLifecycle('speech-error', { speechId: 'speech-1', error: 'tts failed' })

    expect(conversation.currentState.value).toBe(S.ERROR)
    expect(conversation.lastError.value).toBe('tts failed')
  })

  it('recovers from a prior speech error when a new speech really starts', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'failed' })
    conversation.handleSpeechLifecycle('speech-error', { speechId: 'failed', error: 'tts failed' })
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'retry' })
    conversation.handleSpeechLifecycle('speech-started', { speechId: 'retry' })

    expect(conversation.currentState.value).toBe(S.SPEAKING)
    expect(conversation.lastError.value).toBeNull()
  })

  it('keeps lifecycle events idempotent', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'speech-1' })
    conversation.handleSpeechLifecycle('speech-started', { speechId: 'speech-1' })
    const duplicate = conversation.handleSpeechLifecycle('speech-started', { speechId: 'speech-1' })

    expect(conversation.currentState.value).toBe(S.SPEAKING)
    expect(duplicate).toMatchObject({ accepted: true, changed: false })
    expect(duplicate.record.metadata.duplicate).toBe(true)
  })

  it('distinguishes answer confirmation from ASR segment endpointing', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.LISTENING, 'microphone.opened')
    expect(conversation.transitionTo(S.POSSIBLE_END, 'answer.possible-end-entered').accepted).toBe(true)
    expect(conversation.transitionTo(S.LISTENING, 'answer.possible-end-cancelled').accepted).toBe(true)
  })

  it('ignores late events from a replaced speechId', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'old' })
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'new' })
    conversation.handleSpeechLifecycle('speech-started', { speechId: 'old' })
    conversation.handleSpeechLifecycle('speech-ended', { speechId: 'old' })

    expect(conversation.currentState.value).toBe(S.WAITING)
    expect(conversation.activeSpeechId.value).toBe('new')
    expect(conversation.transitionHistory.value.at(-1).metadata).toMatchObject({
      staleEvent: 'speech-ended',
    })
  })

  it('does not let ended override a manually opened microphone', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'speech-1' })
    conversation.handleSpeechLifecycle('speech-started', { speechId: 'speech-1' })
    conversation.transitionTo(S.LISTENING, 'microphone.opened')
    conversation.handleSpeechLifecycle('speech-ended', { speechId: 'speech-1' })

    expect(conversation.currentState.value).toBe(S.LISTENING)
  })

  it.each([
    ['microphone.error', 'permission denied'],
    ['asr.error', 'recognition failed'],
  ])('enters ERROR for %s', (event, error) => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.ERROR, event, { error })

    expect(conversation.currentState.value).toBe(S.ERROR)
    expect(conversation.lastError.value).toBe(error)
  })

  it('supports a recoverable ERROR path back to a reasonable previous state', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.transitionTo(S.ERROR, 'microphone.error', { error: 'permission denied' })
    conversation.recoverFromError('microphone.recovered')
    conversation.transitionTo(S.LISTENING, 'microphone.opened')

    expect(conversation.currentState.value).toBe(S.LISTENING)
    expect(conversation.lastError.value).toBeNull()
  })

  it('treats repeated events as accepted no-ops', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    const result = conversation.transitionTo(S.WAITING, 'question.displayed')

    expect(result).toMatchObject({ accepted: true, changed: false })
    expect(conversation.currentState.value).toBe(S.WAITING)
    expect(conversation.previousState.value).toBe(S.CONNECTING)
    expect(logger.debug).toHaveBeenCalledOnce()
  })

  it('predefines INTERRUPTING transitions without activating interruption behavior', () => {
    expect(canTransition(S.SPEAKING, S.INTERRUPTING)).toBe(true)
    expect(canTransition(S.INTERRUPTING, S.LISTENING)).toBe(true)
  })

  it('waits for confirmed interrupted lifecycle before leaving INTERRUPTING', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'speech-1' })
    conversation.handleSpeechLifecycle('speech-started', { speechId: 'speech-1' })
    conversation.transitionTo(S.INTERRUPTING, 'candidate.barge-in-confirmed')
    expect(conversation.currentState.value).toBe(S.INTERRUPTING)

    conversation.handleSpeechLifecycle('speech-interrupted', { speechId: 'speech-1' })

    expect(conversation.currentState.value).toBe(S.WAITING)
    expect(conversation.activeSpeechId.value).toBeNull()
  })

  it('recovers when speech naturally ends while an interrupt request races it', () => {
    conversation.transitionTo(S.WAITING, 'question.displayed')
    conversation.handleSpeechLifecycle('speech-requested', { speechId: 'speech-1' })
    conversation.handleSpeechLifecycle('speech-started', { speechId: 'speech-1' })
    conversation.transitionTo(S.INTERRUPTING, 'candidate.barge-in-confirmed')

    conversation.handleSpeechLifecycle('speech-ended', { speechId: 'speech-1' })

    expect(conversation.currentState.value).toBe(S.WAITING)
    expect(conversation.activeSpeechId.value).toBeNull()
  })
})
