import { readonly, ref } from 'vue'

export const AudioGateState = Object.freeze({
  ACCEPTING_CANDIDATE_AUDIO: 'ACCEPTING_CANDIDATE_AUDIO',
  BLOCKED_DURING_DIGITAL_HUMAN: 'BLOCKED_DURING_DIGITAL_HUMAN',
  BLOCKED_DURING_TRANSITION: 'BLOCKED_DURING_TRANSITION',
  BLOCKED_WHEN_INTERVIEW_INACTIVE: 'BLOCKED_WHEN_INTERVIEW_INACTIVE',
})

export const DEFAULT_PLAYBACK_GUARD_MS = 500

export function canResumeCandidateAudio({ conversationState, gateState, speechId }) {
  return !['SPEAKING', 'THINKING'].includes(conversationState)
    && gateState !== AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN
    && !speechId
}

export function canFinalizeManualSubmit({ requested, pending, hasError }) {
  return requested && pending === 0 && !hasError
}

export function useInterviewAudioGate({
  playbackGuardMs = DEFAULT_PLAYBACK_GUARD_MS,
  getSessionId = () => null,
  getQuestionId = () => null,
  logger = console,
  setTimer = setTimeout,
  clearTimer = clearTimeout,
  onGuardCompleted = () => {},
} = {}) {
  const gateState = ref(AudioGateState.BLOCKED_WHEN_INTERVIEW_INACTIVE)
  const gateReason = ref('microphone-not-authorized')
  const speechId = ref(null)
  const gateEpoch = ref(0)
  let guardTimer = null

  function log(event, metadata = {}) {
    logger.info?.('[InterviewAudioGate]', {
      event,
      gateState: gateState.value,
      gateReason: gateReason.value,
      speechId: metadata.speechId ?? speechId.value,
      sessionId: getSessionId(),
      questionId: getQuestionId(),
      timestamp: new Date().toISOString(),
      ...metadata,
    })
  }

  function cancelGuard(reason = 'superseded') {
    gateEpoch.value++
    if (guardTimer !== null) {
      clearTimer(guardTimer)
      guardTimer = null
      log('playback-guard-cancelled', { reason })
    }
  }

  function setGate(nextState, reason, metadata = {}) {
    const previousState = gateState.value
    gateState.value = nextState
    gateReason.value = reason
    log(nextState === AudioGateState.ACCEPTING_CANDIDATE_AUDIO ? 'audio-gate-opened' : 'audio-gate-closed', {
      previousState,
      reason,
      ...metadata,
    })
  }

  function open(reason = 'candidate-listening', metadata = {}) {
    cancelGuard('gate-opened-explicitly')
    speechId.value = null
    setGate(AudioGateState.ACCEPTING_CANDIDATE_AUDIO, reason, metadata)
  }

  function blockInactive(reason = 'interview-inactive', metadata = {}) {
    cancelGuard(reason)
    speechId.value = null
    setGate(AudioGateState.BLOCKED_WHEN_INTERVIEW_INACTIVE, reason, metadata)
  }

  function blockForTransition(nextSpeechId, reason = 'speech-requested', metadata = {}) {
    cancelGuard('new-transition')
    speechId.value = nextSpeechId || null
    setGate(AudioGateState.BLOCKED_DURING_TRANSITION, reason, { speechId: nextSpeechId, ...metadata })
  }

  function blockForSpeaking(currentSpeechId, metadata = {}) {
    if (!currentSpeechId || currentSpeechId !== speechId.value) {
      log('audio-gate-stale-event', { speechId: currentSpeechId, event: 'speech-started' })
      return false
    }
    cancelGuard('speech-started')
    setGate(AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN, 'speech-started', {
      speechId: currentSpeechId,
      ...metadata,
    })
    return true
  }

  function startPlaybackGuard(currentSpeechId, reason = 'speech-ended', metadata = {}) {
    if (!currentSpeechId || currentSpeechId !== speechId.value) {
      log('audio-gate-stale-event', { speechId: currentSpeechId, event: reason })
      return false
    }

    cancelGuard('guard-restarted')
    setGate(AudioGateState.BLOCKED_DURING_TRANSITION, 'playback-tail-guard', {
      speechId: currentSpeechId,
      ...metadata,
    })
    const epoch = gateEpoch.value
    log('playback-guard-started', { speechId: currentSpeechId, playbackGuardMs, reason })
    guardTimer = setTimer(() => {
      guardTimer = null
      if (epoch !== gateEpoch.value || currentSpeechId !== speechId.value) {
        log('playback-guard-stale-callback', { speechId: currentSpeechId, epoch })
        return
      }
      speechId.value = null
      log('playback-guard-completed', { speechId: currentSpeechId, playbackGuardMs, reason })
      onGuardCompleted({ speechId: currentSpeechId, epoch, reason })
    }, playbackGuardMs)
    return true
  }

  function dispose(reason = 'page-unloaded') {
    cancelGuard(reason)
    speechId.value = null
    setGate(AudioGateState.BLOCKED_WHEN_INTERVIEW_INACTIVE, reason)
  }

  return {
    gateState: readonly(gateState),
    gateReason: readonly(gateReason),
    speechId: readonly(speechId),
    gateEpoch: readonly(gateEpoch),
    open,
    blockInactive,
    blockForTransition,
    blockForSpeaking,
    startPlaybackGuard,
    cancelGuard,
    dispose,
  }
}
