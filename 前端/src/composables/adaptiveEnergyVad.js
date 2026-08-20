export const SpeechActivityState = Object.freeze({
  SILENCE: 'SILENCE',
  POSSIBLE_SPEECH: 'POSSIBLE_SPEECH',
  SPEECH: 'SPEECH',
  POSSIBLE_SILENCE: 'POSSIBLE_SILENCE',
})

const DEFAULTS = Object.freeze({
  fallbackStartThreshold: 0.018,
  fallbackContinueThreshold: 0.012,
  minAbsoluteStart: 0.008,
  minAbsoluteContinue: 0.005,
  maxStartThreshold: 0.08,
  maxContinueThreshold: 0.05,
  startRatio: 3,
  continueRatio: 1.8,
  minimumSpeechMs: 280,
  speechEndHangoverMs: 120,
  calibrationMs: 1200,
  staleCalibrationMs: 30000,
  noiseWindowMs: 4000,
  noisePercentile: 0.35,
  initialNoiseFloor: 0.003,
  maxNoiseRisePerSecond: 0.35,
  noiseFallAlpha: 0.18,
})

export function createAdaptiveEnergyVad(options = {}) {
  const config = { ...DEFAULTS, ...options }
  let state
  let suspended
  let suspendedAt
  let suspendReason
  let calibrationActive
  let calibrationDurationMs
  let noiseFloor
  let noiseSamples
  let possibleSpeechDurationMs
  let possibleSilenceDurationMs
  let validSpeechDuration
  let lastRms
  let lastPeak
  let lastReason
  let lastTimestamp
  let speechStartedAt
  let lastSpeechAt

  reset('created')

  function processAudioFrame(samples, metadata = {}) {
    const sampleRate = positive(metadata.sampleRate, 48000)
    const durationMs = positive(metadata.durationMs, samples.length / sampleRate * 1000)
    const timestamp = Number.isFinite(metadata.timestamp) ? metadata.timestamp : performance.now()
    const { rms, peak } = measure(samples)
    lastRms = rms
    lastPeak = peak
    lastTimestamp = timestamp

    if (suspended || metadata.gateOpen === false) {
      return output({ reason: suspended ? `suspended:${suspendReason}` : 'gate-closed' })
    }

    const thresholds = calculateThresholds()
    const startThreshold = calibrationActive
      ? Math.max(thresholds.startThreshold, config.fallbackStartThreshold)
      : thresholds.startThreshold
    const continueThreshold = calibrationActive
      ? Math.max(thresholds.continueThreshold, config.fallbackContinueThreshold)
      : thresholds.continueThreshold
    let speechStarted = false
    let speechEnded = false
    let reason = 'silence'

    if (state === SpeechActivityState.SILENCE) {
      if (rms >= startThreshold) {
        state = SpeechActivityState.POSSIBLE_SPEECH
        possibleSpeechDurationMs = durationMs
        speechStartedAt = timestamp - durationMs
        lastSpeechAt = timestamp
        reason = calibrationActive ? 'fallback-start-threshold' : 'start-threshold-crossed'
      } else {
        updateNoiseFloor(rms, durationMs)
        reason = calibrationActive ? 'calibrating-silence' : 'adaptive-silence'
      }
    } else if (state === SpeechActivityState.POSSIBLE_SPEECH) {
      if (rms >= continueThreshold) {
        possibleSpeechDurationMs += durationMs
        lastSpeechAt = timestamp
        if (possibleSpeechDurationMs >= config.minimumSpeechMs) {
          state = SpeechActivityState.SPEECH
          validSpeechDuration = possibleSpeechDurationMs
          speechStarted = true
          reason = 'minimum-speech-confirmed'
        } else {
          reason = 'speech-confirming'
        }
      } else {
        state = SpeechActivityState.SILENCE
        possibleSpeechDurationMs = 0
        speechStartedAt = 0
        updateNoiseFloor(rms, durationMs)
        reason = 'possible-speech-rejected'
      }
    } else if (state === SpeechActivityState.SPEECH) {
      if (rms >= continueThreshold) {
        validSpeechDuration += durationMs
        lastSpeechAt = timestamp
        reason = 'speech-continued'
      } else {
        state = SpeechActivityState.POSSIBLE_SILENCE
        possibleSilenceDurationMs = durationMs
        reason = 'possible-silence-started'
      }
    } else if (rms >= continueThreshold) {
      state = SpeechActivityState.SPEECH
      validSpeechDuration += durationMs
      possibleSilenceDurationMs = 0
      lastSpeechAt = timestamp
      reason = 'speech-resumed-during-hangover'
    } else {
      possibleSilenceDurationMs += durationMs
      if (possibleSilenceDurationMs >= config.speechEndHangoverMs) {
        state = SpeechActivityState.SILENCE
        speechEnded = true
        possibleSpeechDurationMs = 0
        possibleSilenceDurationMs = 0
        reason = 'speech-end-hangover-completed'
      } else {
        reason = 'silence-confirming'
      }
    }

    if (calibrationActive && state === SpeechActivityState.SILENCE) {
      calibrationDurationMs += durationMs
      if (calibrationDurationMs >= config.calibrationMs) {
        calibrationActive = false
        reason = 'calibration-completed'
      }
    }
    lastReason = reason
    return output({ speechStarted, speechEnded, reason, startThreshold, continueThreshold })
  }

  function updateNoiseFloor(rms, durationMs) {
    // Values close to a speech onset or impulsive noise never enter the baseline window.
    const admissionThreshold = Math.max(config.fallbackStartThreshold, noiseFloor * config.startRatio)
    if (!Number.isFinite(rms) || rms < 0 || rms >= admissionThreshold) return
    noiseSamples.push({ rms, durationMs })
    let retainedMs = noiseSamples.reduce((sum, sample) => sum + sample.durationMs, 0)
    while (noiseSamples.length > 1 && retainedMs > config.noiseWindowMs) {
      retainedMs -= noiseSamples.shift().durationMs
    }
    const sorted = noiseSamples.map((sample) => sample.rms).sort((a, b) => a - b)
    const index = Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * config.noisePercentile))
    const robustEstimate = sorted[index] ?? noiseFloor
    if (robustEstimate <= noiseFloor) {
      noiseFloor += (robustEstimate - noiseFloor) * config.noiseFallAlpha
      return
    }
    const maxRise = Math.max(0.00001, noiseFloor * config.maxNoiseRisePerSecond * durationMs / 1000)
    noiseFloor = Math.min(robustEstimate, noiseFloor + maxRise)
  }

  function calculateThresholds() {
    return {
      startThreshold: clamp(
        Math.max(config.minAbsoluteStart, noiseFloor * config.startRatio),
        config.minAbsoluteStart,
        config.maxStartThreshold,
      ),
      continueThreshold: clamp(
        Math.max(config.minAbsoluteContinue, noiseFloor * config.continueRatio),
        config.minAbsoluteContinue,
        config.maxContinueThreshold,
      ),
    }
  }

  function beginCalibration(reason = 'calibration-requested') {
    calibrationActive = true
    calibrationDurationMs = 0
    noiseSamples = []
    lastReason = reason
  }

  function suspend(reason = 'suspended', timestamp = performance.now()) {
    if (!suspended) suspendedAt = timestamp
    suspended = true
    suspendReason = reason
    state = SpeechActivityState.SILENCE
    possibleSpeechDurationMs = 0
    possibleSilenceDurationMs = 0
    validSpeechDuration = 0
    speechStartedAt = 0
    lastSpeechAt = 0
    lastReason = reason
  }

  function resume(reason = 'resumed', timestamp = performance.now()) {
    const suspendedDurationMs = suspendedAt == null ? 0 : Math.max(0, timestamp - suspendedAt)
    suspended = false
    suspendedAt = null
    suspendReason = null
    lastReason = reason
    if (suspendedDurationMs >= config.staleCalibrationMs) beginCalibration('long-pause-recalibration')
    return getSnapshot()
  }

  function reset(reason = 'reset', { preserveCalibration = false } = {}) {
    const retainedCalibrationActive = calibrationActive
    const retainedCalibrationDurationMs = calibrationDurationMs
    const retainedNoiseFloor = noiseFloor
    const retainedNoiseSamples = noiseSamples
    state = SpeechActivityState.SILENCE
    suspended = false
    suspendedAt = null
    suspendReason = null
    calibrationActive = preserveCalibration ? retainedCalibrationActive : true
    calibrationDurationMs = preserveCalibration ? retainedCalibrationDurationMs : 0
    noiseFloor = preserveCalibration ? retainedNoiseFloor : config.initialNoiseFloor
    noiseSamples = preserveCalibration ? retainedNoiseSamples : []
    possibleSpeechDurationMs = 0
    possibleSilenceDurationMs = 0
    validSpeechDuration = 0
    lastRms = 0
    lastPeak = 0
    lastReason = reason
    lastTimestamp = 0
    speechStartedAt = 0
    lastSpeechAt = 0
  }

  function output(overrides = {}) {
    const thresholds = calculateThresholds()
    const startThreshold = overrides.startThreshold ?? (calibrationActive
      ? Math.max(thresholds.startThreshold, config.fallbackStartThreshold)
      : thresholds.startThreshold)
    const continueThreshold = overrides.continueThreshold ?? (calibrationActive
      ? Math.max(thresholds.continueThreshold, config.fallbackContinueThreshold)
      : thresholds.continueThreshold)
    return {
      state,
      speechStarted: false,
      speechEnded: false,
      rms: lastRms,
      peak: lastPeak,
      noiseFloor,
      startThreshold,
      continueThreshold,
      signalToNoiseRatio: noiseFloor > 0 ? lastRms / noiseFloor : null,
      validSpeechDuration,
      confidence: confidence(lastRms, continueThreshold, startThreshold),
      reason: lastReason,
      calibrationActive,
      calibrationProgress: Math.min(1, calibrationDurationMs / config.calibrationMs),
      suspended,
      timestamp: lastTimestamp,
      speechStartedAt: speechStartedAt || null,
      lastSpeechAt: lastSpeechAt || null,
      ...overrides,
    }
  }

  function getSnapshot() {
    return output()
  }

  return { processAudioFrame, reset, suspend, resume, beginCalibration, getSnapshot }
}

function measure(samples) {
  let energy = 0
  let peak = 0
  for (let index = 0; index < samples.length; index++) {
    const sample = samples[index]
    energy += sample * sample
    peak = Math.max(peak, Math.abs(sample))
  }
  return { rms: samples.length ? Math.sqrt(energy / samples.length) : 0, peak }
}

function confidence(rms, continueThreshold, startThreshold) {
  if (rms <= continueThreshold) return 0
  if (startThreshold <= continueThreshold) return 1
  return clamp((rms - continueThreshold) / (startThreshold - continueThreshold), 0, 1)
}

function positive(value, fallback) {
  return Number.isFinite(value) && value > 0 ? value : fallback
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value))
}
