import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AudioGateState as G } from './useInterviewAudioGate'
import { DeviceCaptureState as D, useMicrophone } from './useMicrophone'

function createHarness() {
  const listeners = new Map()
  const track = {
    enabled: true,
    stop: vi.fn(),
    getSettings: vi.fn(() => ({
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: false,
      sampleRate: 48000,
      channelCount: 1,
      deviceId: 'private-device-id',
    })),
    getConstraints: vi.fn(() => ({ echoCancellation: true })),
    addEventListener: vi.fn((name, handler) => listeners.set(name, handler)),
    removeEventListener: vi.fn((name) => listeners.delete(name)),
  }
  const stream = {
    getAudioTracks: () => [track],
    getTracks: () => [track],
  }
  const mediaDevices = { getUserMedia: vi.fn(async () => stream) }

  class Node {
    constructor() {
      this.connect = vi.fn()
      this.disconnect = vi.fn()
    }
  }
  class FakeAudioWorkletNode extends Node {
    constructor() {
      super()
      this.port = { onmessage: null }
    }
  }
  class FakeAudioContext {
    constructor() {
      this.sampleRate = 48000
      this.destination = {}
      this.audioWorklet = { addModule: vi.fn(async () => {}) }
      this.resume = vi.fn(async () => {})
      this.close = vi.fn(async () => {})
      this.createMediaStreamSource = vi.fn(() => new Node())
      this.createGain = vi.fn(() => Object.assign(new Node(), { gain: { value: 1 } }))
    }
  }

  let currentTime = 1000
  const onSegment = vi.fn()
  const onEndpointing = vi.fn()
  const onDeviceError = vi.fn()
  const onReliableSpeechStarted = vi.fn()
  const onReliableSpeechEnded = vi.fn()
  const onBlockedAudioFrame = vi.fn()
  const microphone = useMicrophone({
    onSegment,
    onEndpointing,
    onDeviceError,
    onReliableSpeechStarted,
    onReliableSpeechEnded,
    onBlockedAudioFrame,
    mediaDevices,
    AudioContextClass: FakeAudioContext,
    AudioWorkletNodeClass: FakeAudioWorkletNode,
    logger: { info: vi.fn() },
    now: () => currentTime,
  })

  return {
    microphone,
    mediaDevices,
    track,
    listeners,
    onSegment,
    onEndpointing,
    onDeviceError,
    onReliableSpeechStarted,
    onReliableSpeechEnded,
    onBlockedAudioFrame,
    advance(ms) { currentTime += ms },
  }
}

describe('useMicrophone continuous half-duplex capture', () => {
  let harness

  beforeEach(() => {
    harness = createHarness()
  })

  it('keeps the device and AudioWorklet active after first authorization', async () => {
    expect(await harness.microphone.initializeMicrophone()).toBe(true)
    expect(harness.microphone.deviceState.value).toBe(D.ACTIVE)
    expect(harness.microphone.isAudioWorkletRunning.value).toBe(true)
  })

  it('does not call getUserMedia again for the next question', async () => {
    await harness.microphone.initializeMicrophone()
    await harness.microphone.initializeMicrophone()
    expect(harness.mediaDevices.getUserMedia).toHaveBeenCalledOnce()
  })

  it('closes the business gate while keeping track and worklet running', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.BLOCKED_DURING_DIGITAL_HUMAN, { reason: 'speech-started' })
    expect(harness.track.enabled).toBe(true)
    expect(harness.track.stop).not.toHaveBeenCalled()
    expect(harness.microphone.isAudioWorkletRunning.value).toBe(true)
  })

  it('does not buffer, upload, or set isSpeaking while the gate is closed', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.BLOCKED_DURING_DIGITAL_HUMAN, { reason: 'speech-started' })
    harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
    harness.microphone.finishSegment('test')

    expect(harness.microphone.getCaptureSnapshot().segmentChunkCount).toBe(0)
    expect(harness.onSegment).not.toHaveBeenCalled()
    expect(harness.onEndpointing).not.toHaveBeenCalled()
    expect(harness.onBlockedAudioFrame).toHaveBeenCalledOnce()
    expect(harness.microphone.isSpeaking.value).toBe(false)
  })

  it('submitting a valid segment does not stop MediaStreamTrack', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO, { reason: 'candidate-answer' })
    for (let index = 0; index < 8; index++) {
      harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
      harness.advance(43)
    }
    expect(harness.microphone.finishSegment('manual-submit')).toBe(true)
    expect(harness.onSegment).toHaveBeenCalledOnce()
    expect(harness.track.stop).not.toHaveBeenCalled()
    expect(harness.microphone.deviceState.value).toBe(D.ACTIVE)
  })

  it('only emits reliable speech after the minimum voiced duration', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO)
    harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
    expect(harness.onReliableSpeechStarted).not.toHaveBeenCalled()
    for (let index = 0; index < 7; index++) {
      harness.advance(43)
      harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
    }
    expect(harness.onReliableSpeechStarted).toHaveBeenCalledOnce()
  })

  it('uses the calibrated adaptive threshold instead of requiring the legacy 0.018 level', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO)
    for (let index = 0; index < 29; index++) {
      harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.003))
      harness.advance(43)
    }
    expect(harness.microphone.getCaptureSnapshot().vadCalibrationActive).toBe(false)

    for (let index = 0; index < 8; index++) {
      harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.01))
      harness.advance(43)
    }
    expect(harness.onReliableSpeechStarted).toHaveBeenCalledOnce()
    expect(harness.microphone.getCaptureSnapshot().vadStartThreshold).toBeLessThan(0.018)
  })

  it('does not update the candidate noise baseline from gate-blocked audio', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO)
    for (let index = 0; index < 29; index++) {
      harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.003))
      harness.advance(43)
    }
    const before = harness.microphone.getCaptureSnapshot().noiseBaseline
    harness.microphone.setAudioGate(G.BLOCKED_DURING_DIGITAL_HUMAN, { reason: 'speech-started' })
    for (let index = 0; index < 20; index++) {
      harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.2))
      harness.advance(43)
    }
    expect(harness.microphone.getCaptureSnapshot().noiseBaseline).toBe(before)
    expect(harness.microphone.getCaptureSnapshot().vadSuspended).toBe(true)
  })

  it('short noise does not emit a reliable start/end pair', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO)
    harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
    harness.advance(1600)
    harness.microphone.handleAudioChunk(new Float32Array(2048))
    expect(harness.onReliableSpeechStarted).not.toHaveBeenCalled()
    expect(harness.onReliableSpeechEnded).not.toHaveBeenCalled()
  })

  it('max-duration flush does not emit answer-level speech ended', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO)
    for (let index = 0; index < 8; index++) {
      harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
      harness.advance(43)
    }
    harness.advance(28000)
    harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
    expect(harness.onSegment).toHaveBeenCalledOnce()
    expect(harness.onReliableSpeechEnded).not.toHaveBeenCalled()
  })

  it('manual pause only closes the gate and resets capture state', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO)
    harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
    expect(harness.microphone.isSpeaking.value).toBe(true)

    harness.microphone.setAudioGate(G.BLOCKED_WHEN_INTERVIEW_INACTIVE, { reason: 'manual-pause' })
    expect(harness.track.stop).not.toHaveBeenCalled()
    expect(harness.microphone.getCaptureSnapshot()).toMatchObject({
      segmentChunkCount: 0,
      preRollChunkCount: 0,
      segmentStarted: false,
    })
  })

  it('resume starts with empty pre-roll and VAD state', async () => {
    await harness.microphone.initializeMicrophone()
    harness.microphone.setAudioGate(G.BLOCKED_DURING_TRANSITION)
    harness.microphone.handleAudioChunk(new Float32Array(2048).fill(0.5))
    harness.microphone.setAudioGate(G.ACCEPTING_CANDIDATE_AUDIO, { reason: 'guard-completed' })
    expect(harness.microphone.getCaptureSnapshot()).toMatchObject({
      segmentChunkCount: 0,
      preRollChunkCount: 0,
      segmentStarted: false,
      voicedDurationMs: 0,
    })
  })

  it('releases tracks and the audio graph only on explicit stop', async () => {
    await harness.microphone.initializeMicrophone()
    await harness.microphone.stopMicrophone({ reason: 'interview-ended' })
    expect(harness.track.stop).toHaveBeenCalledOnce()
    expect(harness.microphone.deviceState.value).toBe(D.STOPPED)
    expect(harness.microphone.isAudioWorkletRunning.value).toBe(false)
  })

  it('enters ERROR and cleans resources when the device ends unexpectedly', async () => {
    await harness.microphone.initializeMicrophone()
    const ended = harness.listeners.get('ended')
    await ended()
    expect(harness.microphone.deviceState.value).toBe(D.ERROR)
    expect(harness.onDeviceError).toHaveBeenCalledOnce()
    expect(harness.microphone.isAudioWorkletRunning.value).toBe(false)
  })
})
