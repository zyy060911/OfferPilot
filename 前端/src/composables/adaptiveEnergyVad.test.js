import { describe, expect, it } from 'vitest'
import { createAdaptiveEnergyVad, SpeechActivityState } from './adaptiveEnergyVad'

const SAMPLE_RATE = 48000
const FRAME_SAMPLES = 480

function frame(level) {
  return new Float32Array(FRAME_SAMPLES).fill(level)
}

function feed(detector, level, count, startAt = 0) {
  const results = []
  for (let index = 0; index < count; index++) {
    results.push(detector.processAudioFrame(frame(level), {
      sampleRate: SAMPLE_RATE,
      timestamp: startAt + (index + 1) * 10,
    }))
  }
  return results
}

describe('adaptive energy VAD', () => {
  it('calibrates from gated-open non-speech without blocking immediate speech', () => {
    const detector = createAdaptiveEnergyVad({ calibrationMs: 100, minimumSpeechMs: 30 })
    const calibration = feed(detector, 0.0035, 10)
    expect(calibration.at(-1).calibrationActive).toBe(false)
    expect(calibration.at(-1).noiseFloor).toBeGreaterThan(0)

    detector.beginCalibration()
    const speech = feed(detector, 0.03, 3, 100)
    expect(speech.some((result) => result.speechStarted)).toBe(true)
    expect(speech.at(-1).state).toBe(SpeechActivityState.SPEECH)
  })

  it('uses separate start and continue thresholds for hysteresis', () => {
    const detector = createAdaptiveEnergyVad({ calibrationMs: 10, minimumSpeechMs: 30 })
    feed(detector, 0.002, 1)
    const first = detector.processAudioFrame(frame(0.01), { sampleRate: SAMPLE_RATE, timestamp: 20 })
    const second = detector.processAudioFrame(frame(0.006), { sampleRate: SAMPLE_RATE, timestamp: 30 })
    const third = detector.processAudioFrame(frame(0.006), { sampleRate: SAMPLE_RATE, timestamp: 40 })

    expect(first.startThreshold).toBeGreaterThan(first.continueThreshold)
    expect(first.state).toBe(SpeechActivityState.POSSIBLE_SPEECH)
    expect(second.state).toBe(SpeechActivityState.POSSIBLE_SPEECH)
    expect(third.speechStarted).toBe(true)
  })

  it('accumulates the minimum speech duration across worklet frames', () => {
    const detector = createAdaptiveEnergyVad({ calibrationMs: 10, minimumSpeechMs: 280 })
    feed(detector, 0.002, 1)
    const results = feed(detector, 0.03, 28, 10)
    expect(results.slice(0, -1).every((result) => !result.speechStarted)).toBe(true)
    expect(results.at(-1).speechStarted).toBe(true)
    expect(results.at(-1).validSpeechDuration).toBeCloseTo(280)
  })

  it('rejects an impulsive keyboard-like peak and does not inflate the baseline', () => {
    const detector = createAdaptiveEnergyVad({ calibrationMs: 50, minimumSpeechMs: 40 })
    feed(detector, 0.003, 5)
    const before = detector.getSnapshot().noiseFloor
    const impulse = detector.processAudioFrame(frame(0.4), { sampleRate: SAMPLE_RATE, timestamp: 60 })
    const after = feed(detector, 0.003, 5, 60)

    expect(impulse.state).toBe(SpeechActivityState.POSSIBLE_SPEECH)
    expect(after.some((result) => result.speechStarted)).toBe(false)
    expect(detector.getSnapshot().noiseFloor).toBeLessThanOrEqual(before * 1.1)
  })

  it('emits one start and one end around a speech run', () => {
    const detector = createAdaptiveEnergyVad({
      calibrationMs: 10,
      minimumSpeechMs: 30,
      speechEndHangoverMs: 30,
    })
    feed(detector, 0.002, 1)
    const results = [
      ...feed(detector, 0.03, 6, 10),
      ...feed(detector, 0.001, 6, 70),
    ]
    expect(results.filter((result) => result.speechStarted)).toHaveLength(1)
    expect(results.filter((result) => result.speechEnded)).toHaveLength(1)
    expect(results.at(-1).state).toBe(SpeechActivityState.SILENCE)
  })

  it('does not learn or emit while suspended and retains a fresh baseline on resume', () => {
    const detector = createAdaptiveEnergyVad({ calibrationMs: 30, staleCalibrationMs: 1000 })
    feed(detector, 0.003, 3)
    const before = detector.getSnapshot().noiseFloor
    detector.suspend('digital-human-speaking', 100)
    const blocked = detector.processAudioFrame(frame(0.5), { sampleRate: SAMPLE_RATE, timestamp: 200 })
    expect(blocked.suspended).toBe(true)
    expect(blocked.speechStarted).toBe(false)
    expect(blocked.noiseFloor).toBe(before)

    const resumed = detector.resume('playback-guard-completed', 500)
    expect(resumed.calibrationActive).toBe(false)
    expect(resumed.noiseFloor).toBe(before)
  })

  it('recalibrates after a long pause or a detector reset', () => {
    const detector = createAdaptiveEnergyVad({ calibrationMs: 20, staleCalibrationMs: 100 })
    feed(detector, 0.003, 2)
    expect(detector.getSnapshot().calibrationActive).toBe(false)
    detector.suspend('paused', 100)
    expect(detector.resume('resumed', 250).calibrationActive).toBe(true)
    detector.reset('device-changed')
    expect(detector.getSnapshot()).toMatchObject({
      state: SpeechActivityState.SILENCE,
      calibrationActive: true,
      reason: 'device-changed',
    })
  })

  it('tracks gradual background drift with a bounded noise-floor rise', () => {
    const detector = createAdaptiveEnergyVad({
      calibrationMs: 20,
      maxNoiseRisePerSecond: 0.5,
      noiseWindowMs: 1000,
    })
    feed(detector, 0.003, 2)
    const before = detector.getSnapshot().noiseFloor
    feed(detector, 0.006, 20, 20)
    const after = detector.getSnapshot().noiseFloor
    expect(after).toBeGreaterThan(before)
    expect(after).toBeLessThan(0.006)
  })
})
