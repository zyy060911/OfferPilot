import { readonly, ref } from 'vue'

export const ConversationState = Object.freeze({
  CONNECTING: 'CONNECTING',
  WAITING: 'WAITING',
  LISTENING: 'LISTENING',
  ENDPOINTING: 'ENDPOINTING',
  TRANSCRIBING: 'TRANSCRIBING',
  POSSIBLE_END: 'POSSIBLE_END',
  THINKING: 'THINKING',
  SPEAKING: 'SPEAKING',
  INTERRUPTING: 'INTERRUPTING',
  ERROR: 'ERROR',
})

const S = ConversationState

const ALLOWED_TRANSITIONS = Object.freeze({
  [S.CONNECTING]: new Set([S.WAITING, S.SPEAKING, S.ERROR]),
  [S.WAITING]: new Set([S.CONNECTING, S.LISTENING, S.ENDPOINTING, S.THINKING, S.SPEAKING, S.ERROR]),
  [S.LISTENING]: new Set([S.WAITING, S.ENDPOINTING, S.TRANSCRIBING, S.POSSIBLE_END, S.THINKING, S.SPEAKING, S.ERROR]),
  [S.ENDPOINTING]: new Set([S.WAITING, S.LISTENING, S.TRANSCRIBING, S.POSSIBLE_END, S.THINKING, S.ERROR]),
  [S.TRANSCRIBING]: new Set([S.WAITING, S.LISTENING, S.ENDPOINTING, S.POSSIBLE_END, S.THINKING, S.ERROR]),
  [S.POSSIBLE_END]: new Set([S.LISTENING, S.ENDPOINTING, S.TRANSCRIBING, S.THINKING, S.ERROR]),
  [S.THINKING]: new Set([S.WAITING, S.SPEAKING, S.ERROR]),
  [S.SPEAKING]: new Set([S.WAITING, S.LISTENING, S.INTERRUPTING, S.ERROR]),
  [S.INTERRUPTING]: new Set([S.WAITING, S.LISTENING, S.SPEAKING, S.ERROR]),
  [S.ERROR]: new Set([S.CONNECTING, S.WAITING, S.LISTENING, S.THINKING, S.SPEAKING]),
})

export function canTransition(fromState, toState) {
  if (fromState === toState) return true
  return Boolean(ALLOWED_TRANSITIONS[fromState]?.has(toState))
}

export function useInterviewConversation({
  initialState = S.CONNECTING,
  getSessionId = () => null,
  getQuestionId = () => null,
  logger = console,
  dev = import.meta.env?.DEV ?? false,
} = {}) {
  if (!Object.values(S).includes(initialState)) {
    throw new Error(`Unknown interview conversation state: ${initialState}`)
  }

  const currentState = ref(initialState)
  const previousState = ref(null)
  const transitionHistory = ref([])
  const lastError = ref(null)
  const activeSpeechId = ref(null)
  const handledSpeechEvents = new Set()

  function buildRecord(fromState, toState, event, metadata, accepted, changed) {
    return {
      fromState,
      toState,
      event: event || 'unspecified',
      sessionId: metadata.sessionId ?? getSessionId() ?? null,
      questionId: metadata.questionId ?? getQuestionId() ?? null,
      timestamp: new Date().toISOString(),
      error: metadata.error ? String(metadata.error?.message || metadata.error) : null,
      accepted,
      changed,
      metadata: metadata.details || null,
    }
  }

  function transitionTo(nextState, event, metadata = {}) {
    const fromState = currentState.value
    const knownState = Object.values(S).includes(nextState)
    const accepted = knownState && canTransition(fromState, nextState)

    if (!accepted) {
      const record = buildRecord(fromState, nextState, event, metadata, false, false)
      transitionHistory.value.push(record)
      if (dev) {
        logger.warn?.('[InterviewConversation] illegal transition', record)
      }
      return { accepted: false, changed: false, record }
    }

    if (fromState === nextState) {
      if (nextState === S.ERROR && metadata.error) {
        lastError.value = metadata.error
      }
      const record = buildRecord(fromState, nextState, event, metadata, true, false)
      transitionHistory.value.push(record)
      logger.debug?.('[InterviewConversation] duplicate event ignored', record)
      return { accepted: true, changed: false, record }
    }

    previousState.value = fromState
    currentState.value = nextState
    if (nextState === S.ERROR) {
      lastError.value = metadata.error || metadata.details || event || 'unknown error'
    } else {
      lastError.value = null
    }

    const record = buildRecord(fromState, nextState, event, metadata, true, true)
    transitionHistory.value.push(record)
    logger.info?.('[InterviewConversation] transition', record)
    return { accepted: true, changed: true, record }
  }

  function recoverFromError(event = 'error.recovered', metadata = {}, fallbackState = S.WAITING) {
    if (currentState.value !== S.ERROR) {
      return transitionTo(currentState.value, event, metadata)
    }

    const candidate = previousState.value
    const recoveryState = candidate && canTransition(S.ERROR, candidate)
      ? candidate
      : fallbackState
    return transitionTo(recoveryState, event, metadata)
  }

  function recordSpeechEvent(event, payload, extra = {}) {
    return transitionTo(currentState.value, `digital-human.${event}`, {
      details: { ...payload, ...extra },
    })
  }

  function handleSpeechLifecycle(event, payload = {}) {
    const speechId = payload.speechId
    if (!speechId) return recordSpeechEvent(event, payload, { invalid: true })

    const eventKey = `${speechId}:${event}`
    if (handledSpeechEvents.has(eventKey)) {
      return recordSpeechEvent(event, payload, { duplicate: true })
    }
    handledSpeechEvents.add(eventKey)

    if (event === 'speech-requested') {
      const replacedSpeechId = activeSpeechId.value
      activeSpeechId.value = speechId
      return recordSpeechEvent(event, payload, {
        replacedSpeechId: replacedSpeechId && replacedSpeechId !== speechId ? replacedSpeechId : null,
      })
    }

    if (speechId !== activeSpeechId.value) {
      return recordSpeechEvent('speech-stale', payload, { staleEvent: event })
    }

    if (event === 'speech-accepted') {
      return recordSpeechEvent(event, payload)
    }
    if (event === 'speech-started') {
      return transitionTo(S.SPEAKING, 'digital-human.speech-started', { details: payload })
    }
    if (event === 'speech-ended' || event === 'speech-interrupted') {
      activeSpeechId.value = null
      if (currentState.value === S.SPEAKING || currentState.value === S.INTERRUPTING) {
        return transitionTo(S.WAITING, `digital-human.${event}`, { details: payload })
      }
      return recordSpeechEvent(event, payload)
    }
    if (event === 'speech-error') {
      activeSpeechId.value = null
      return transitionTo(S.ERROR, 'digital-human.speech-error', {
        error: payload.error || '数字人播报失败',
        details: payload,
      })
    }
    return recordSpeechEvent(event, payload, { unknown: true })
  }

  return {
    currentState: readonly(currentState),
    previousState: readonly(previousState),
    transitionHistory: readonly(transitionHistory),
    lastError: readonly(lastError),
    activeSpeechId: readonly(activeSpeechId),
    transitionTo,
    recoverFromError,
    handleSpeechLifecycle,
    canTransition,
  }
}
