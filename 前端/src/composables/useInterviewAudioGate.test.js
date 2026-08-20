import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  AudioGateState as G,
  canFinalizeManualSubmit,
  canResumeCandidateAudio,
  useInterviewAudioGate,
} from './useInterviewAudioGate'

describe('useInterviewAudioGate', () => {
  let scheduled
  let clearTimer
  let onGuardCompleted
  let gate

  beforeEach(() => {
    scheduled = new Map()
    clearTimer = vi.fn((id) => scheduled.delete(id))
    onGuardCompleted = vi.fn()
    let nextId = 0
    gate = useInterviewAudioGate({
      playbackGuardMs: 500,
      logger: { info: vi.fn() },
      setTimer: (callback) => {
        const id = ++nextId
        scheduled.set(id, callback)
        return id
      },
      clearTimer,
      onGuardCompleted,
    })
  })

  it('closes from requested and remains closed while the digital human speaks', () => {
    gate.open()
    gate.blockForTransition('speech-1')
    expect(gate.gateState.value).toBe(G.BLOCKED_DURING_TRANSITION)
    expect(gate.blockForSpeaking('speech-1')).toBe(true)
    expect(gate.gateState.value).toBe(G.BLOCKED_DURING_DIGITAL_HUMAN)
  })

  it('does not open immediately on speech-ended', () => {
    gate.blockForTransition('speech-1')
    gate.blockForSpeaking('speech-1')
    gate.startPlaybackGuard('speech-1')
    expect(gate.gateState.value).toBe(G.BLOCKED_DURING_TRANSITION)
    expect(onGuardCompleted).not.toHaveBeenCalled()
  })

  it('opens only through the owner after playback guard completes', () => {
    gate.blockForTransition('speech-1')
    gate.startPlaybackGuard('speech-1')
    scheduled.values().next().value()
    expect(onGuardCompleted).toHaveBeenCalledWith(expect.objectContaining({ speechId: 'speech-1' }))
    expect(gate.gateState.value).toBe(G.BLOCKED_DURING_TRANSITION)
    gate.open('guard-completed')
    expect(gate.gateState.value).toBe(G.ACCEPTING_CANDIDATE_AUDIO)
  })

  it('cancels an old guard when a new speech is requested', () => {
    gate.blockForTransition('old')
    gate.startPlaybackGuard('old')
    const oldCallback = scheduled.values().next().value
    gate.blockForTransition('new')
    oldCallback()
    expect(onGuardCompleted).not.toHaveBeenCalled()
    expect(gate.speechId.value).toBe('new')
  })

  it('ignores stale speech IDs', () => {
    gate.blockForTransition('new')
    expect(gate.blockForSpeaking('old')).toBe(false)
    expect(gate.startPlaybackGuard('old')).toBe(false)
    expect(gate.gateState.value).toBe(G.BLOCKED_DURING_TRANSITION)
  })

  it('dispose cancels timers and leaves the interview inactive', () => {
    gate.blockForTransition('speech-1')
    gate.startPlaybackGuard('speech-1')
    gate.dispose()
    expect(clearTimer).toHaveBeenCalled()
    expect(gate.gateState.value).toBe(G.BLOCKED_WHEN_INTERVIEW_INACTIVE)
  })

  it('does not allow manual resume while the digital human is speaking', () => {
    expect(canResumeCandidateAudio({
      conversationState: 'SPEAKING',
      gateState: G.BLOCKED_DURING_DIGITAL_HUMAN,
      speechId: 'speech-1',
    })).toBe(false)
  })

  it('does not finalize manual submission until every ASR request finishes', () => {
    expect(canFinalizeManualSubmit({ requested: true, pending: 1, hasError: false })).toBe(false)
    expect(canFinalizeManualSubmit({ requested: true, pending: 0, hasError: false })).toBe(true)
    expect(canFinalizeManualSubmit({ requested: true, pending: 0, hasError: true })).toBe(false)
  })
})
