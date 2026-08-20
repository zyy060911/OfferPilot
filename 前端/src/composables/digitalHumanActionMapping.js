import { ConversationState } from './useInterviewConversation'
import { AudioGateState } from './useInterviewAudioGate'

export const DigitalHumanActionState = Object.freeze({
  NEUTRAL: 'NEUTRAL',
  LISTENING: 'LISTENING',
  LISTENING_PAUSE: 'LISTENING_PAUSE',
  THINKING: 'THINKING',
  SPEAKING: 'SPEAKING',
  ERROR: 'ERROR',
})

const C = ConversationState
const A = DigitalHumanActionState

export function mapConversationToDigitalHumanAction({
  conversationState,
  audioGateState,
  microphoneAuthorized = false,
  candidatePaused = false,
} = {}) {
  if (conversationState === C.ERROR) return A.ERROR
  if (conversationState === C.SPEAKING) return A.SPEAKING
  if (conversationState === C.THINKING) return A.THINKING
  if (conversationState === C.POSSIBLE_END) return A.LISTENING_PAUSE
  if ([C.LISTENING, C.ENDPOINTING, C.TRANSCRIBING].includes(conversationState)) return A.LISTENING
  if (
    conversationState === C.WAITING
    && microphoneAuthorized
    && !candidatePaused
    && audioGateState === AudioGateState.ACCEPTING_CANDIDATE_AUDIO
  ) return A.LISTENING
  return A.NEUTRAL
}

export function isDigitalHumanActionState(value) {
  return Object.values(A).includes(value)
}
