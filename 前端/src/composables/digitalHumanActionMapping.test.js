import { describe, expect, it } from 'vitest'
import { ConversationState as C } from './useInterviewConversation'
import { AudioGateState as G } from './useInterviewAudioGate'
import {
  DigitalHumanActionState as A,
  mapConversationToDigitalHumanAction,
} from './digitalHumanActionMapping'

describe('digital human action mapping', () => {
  it.each([
    [C.CONNECTING, A.NEUTRAL],
    [C.WAITING, A.NEUTRAL],
    [C.LISTENING, A.LISTENING],
    [C.ENDPOINTING, A.LISTENING],
    [C.TRANSCRIBING, A.LISTENING],
    [C.POSSIBLE_END, A.LISTENING_PAUSE],
    [C.THINKING, A.THINKING],
    [C.SPEAKING, A.SPEAKING],
    [C.ERROR, A.ERROR],
  ])('maps %s to %s', (conversationState, expected) => {
    expect(mapConversationToDigitalHumanAction({ conversationState })).toBe(expected)
  })

  it('maps WAITING to LISTENING only when candidate audio is really open', () => {
    expect(mapConversationToDigitalHumanAction({
      conversationState: C.WAITING,
      microphoneAuthorized: true,
      candidatePaused: false,
      audioGateState: G.ACCEPTING_CANDIDATE_AUDIO,
    })).toBe(A.LISTENING)
    expect(mapConversationToDigitalHumanAction({
      conversationState: C.WAITING,
      microphoneAuthorized: true,
      candidatePaused: true,
      audioGateState: G.ACCEPTING_CANDIDATE_AUDIO,
    })).toBe(A.NEUTRAL)
  })
})
