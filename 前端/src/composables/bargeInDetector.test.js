import { describe, expect, it } from 'vitest'
import { AudioGateState } from './useInterviewAudioGate'
import { ConversationState } from './useInterviewConversation'
import { BargeInState, createBargeInDetector } from './bargeInDetector'

const eligible = {
  enabled: true,
  speechId: 'speech-1',
  conversationState: ConversationState.SPEAKING,
  deviceActive: true,
  interviewActive: true,
  ttsPlaying: true,
  interrupting: false,
  playbackGuardActive: false,
  gateState: AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN,
  aecEnabled: true,
  durationMs: 20,
}

function feed(detector, count, metadata = eligible) {
  let snapshot
  for (let index = 0; index < count; index++) snapshot = detector.processAudioFrame(null, metadata)
  return snapshot
}

describe('bargeInDetector', () => {
  it('is disabled by default conditions and never confirms', () => {
    const detector = createBargeInDetector({ warmupMs: 0 })
    const result = detector.processAudioFrame(null, { ...eligible, enabled: false, rms: 0.2, peak: 0.4 })
    expect(result.state).toBe(BargeInState.IDLE)
    expect(result.confirmed).toBe(false)
    expect(result.detectionReason).toBe('feature-disabled')
  })

  it('rejects a short impulse instead of interrupting TTS', () => {
    const detector = createBargeInDetector({ warmupMs: 0, confirmationMs: 200, allowedGapMs: 40 })
    detector.processAudioFrame(null, { ...eligible, rms: 0.08, peak: 0.2 })
    const result = feed(detector, 3, { ...eligible, rms: 0.005, peak: 0.01 })
    expect(result.state).toBe(BargeInState.REJECTED_AS_NOISE)
    expect(result.confirmed).toBe(false)
    expect(result.detectionReason).toBe('energy-not-sustained')
  })

  it('confirms only one edge after sustained candidate speech', () => {
    const detector = createBargeInDetector({ warmupMs: 40, confirmationMs: 200 })
    feed(detector, 3, { ...eligible, rms: 0.006, peak: 0.01 })
    let confirmations = 0
    for (let index = 0; index < 14; index++) {
      const result = detector.processAudioFrame(null, { ...eligible, rms: 0.08, peak: 0.2 })
      if (result.confirmed) confirmations++
    }
    expect(confirmations).toBe(1)
    expect(detector.getSnapshot().state).toBe(BargeInState.CONFIRMED_BARGE_IN)
    expect(detector.getSnapshot().interruptionConfidence).toBeGreaterThanOrEqual(0.85)
  })

  it('uses stricter thresholds when browser AEC is unavailable', () => {
    const detector = createBargeInDetector({ warmupMs: 0 })
    const result = detector.processAudioFrame(null, {
      ...eligible,
      aecEnabled: false,
      rms: 0.04,
      peak: 0.08,
    })
    expect(result.state).toBe(BargeInState.IDLE)
    expect(result.startThreshold).toBeGreaterThanOrEqual(0.05)
  })

  it('resets ownership when speechId changes and rejects guard frames', () => {
    const detector = createBargeInDetector({ warmupMs: 0, confirmationMs: 100 })
    feed(detector, 3, { ...eligible, rms: 0.08, peak: 0.2 })
    const changed = detector.processAudioFrame(null, {
      ...eligible,
      speechId: 'speech-2',
      playbackGuardActive: true,
      rms: 0.08,
      peak: 0.2,
    })
    expect(changed.state).toBe(BargeInState.IDLE)
    expect(changed.activeSpeechId).toBeNull()
    expect(changed.detectionReason).toBe('playback-guard-active')
  })
})
