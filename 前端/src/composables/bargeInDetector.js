import { AudioGateState } from './useInterviewAudioGate'
import { ConversationState } from './useInterviewConversation'

export const BargeInState = Object.freeze({
  IDLE: 'IDLE',
  POSSIBLE_BARGE_IN: 'POSSIBLE_BARGE_IN',
  CONFIRMED_BARGE_IN: 'CONFIRMED_BARGE_IN',
  REJECTED_AS_NOISE: 'REJECTED_AS_NOISE',
})

const DEFAULTS = Object.freeze({
  warmupMs: 450,
  confirmationMs: 700,
  allowedGapMs: 120,
  rejectionHoldMs: 160,
  minRmsWithAec: 0.035,
  minRmsWithoutAec: 0.05,
  minPeakWithAec: 0.07,
  minPeakWithoutAec: 0.1,
  aecNoiseRatio: 3.5,
  noAecNoiseRatio: 5.5,
  thresholdMargin: 0.008,
  fallbackEchoFloor: 0.006,
  maxEchoFloor: 0.025,
  baselineWindowFrames: 240,
})

export function createBargeInDetector(options = {}) {
  const config = { ...DEFAULTS, ...options }
  let state = BargeInState.IDLE
  let activeSpeechId = null
  let stateDurationMs = 0
  let candidateDurationMs = 0
  let gapDurationMs = 0
  let warmupDurationMs = 0
  let echoFloor = config.fallbackEchoFloor
  let startThreshold = config.minRmsWithAec
  let peakThreshold = config.minPeakWithAec
  let interruptionConfidence = 0
  let detectionReason = 'inactive'
  let baselineFrames = []

  function reset(reason = 'reset') {
    state = BargeInState.IDLE
    activeSpeechId = null
    stateDurationMs = 0
    candidateDurationMs = 0
    gapDurationMs = 0
    warmupDurationMs = 0
    echoFloor = config.fallbackEchoFloor
    startThreshold = config.minRmsWithAec
    peakThreshold = config.minPeakWithAec
    interruptionConfidence = 0
    detectionReason = reason
    baselineFrames = []
    return getSnapshot()
  }

  function processAudioFrame(samples, metadata = {}) {
    const durationMs = positive(metadata.durationMs, inferDuration(samples, metadata.sampleRate))
    const eligibility = checkEligibility(metadata)
    if (!eligibility.eligible) {
      if (activeSpeechId || state !== BargeInState.IDLE) reset(eligibility.reason)
      detectionReason = eligibility.reason
      return { ...getSnapshot(), confirmed: false, rejected: false }
    }

    if (activeSpeechId !== metadata.speechId) {
      reset('speech-context-changed')
      activeSpeechId = metadata.speechId
    }

    const rms = Number.isFinite(metadata.rms) ? metadata.rms : calculateRms(samples)
    const peak = Number.isFinite(metadata.peak) ? metadata.peak : calculatePeak(samples)
    const aecEnabled = metadata.aecEnabled === true
    if (
      warmupDurationMs < config.warmupMs
      && Number.isFinite(metadata.blockedBaselineRms)
      && metadata.blockedBaselineRms > 0
    ) {
      echoFloor = Math.min(config.maxEchoFloor, Math.max(echoFloor, metadata.blockedBaselineRms))
    }

    warmupDurationMs += durationMs
    updateThresholds(aecEnabled)
    if (warmupDurationMs <= config.warmupMs) {
      updateEchoBaseline(rms)
      detectionReason = 'playback-echo-warmup'
      return { ...getSnapshot(), rms, peak, confirmed: false, rejected: false }
    }

    const aboveThreshold = rms >= startThreshold && peak >= peakThreshold
    let confirmed = false
    let rejected = false
    stateDurationMs += durationMs

    if (state === BargeInState.CONFIRMED_BARGE_IN) {
      return { ...getSnapshot(), rms, peak, confirmed: false, rejected: false }
    }

    if (state === BargeInState.REJECTED_AS_NOISE) {
      if (stateDurationMs >= config.rejectionHoldMs) {
        state = BargeInState.IDLE
        stateDurationMs = 0
        detectionReason = 'ready-after-noise-rejection'
      }
      if (!aboveThreshold) updateEchoBaseline(rms)
      return { ...getSnapshot(), rms, peak, confirmed: false, rejected: false }
    }

    if (state === BargeInState.IDLE) {
      if (!aboveThreshold) {
        updateEchoBaseline(rms)
        detectionReason = 'below-conservative-threshold'
        interruptionConfidence = 0
        return { ...getSnapshot(), rms, peak, confirmed: false, rejected: false }
      }
      state = BargeInState.POSSIBLE_BARGE_IN
      stateDurationMs = 0
      candidateDurationMs = durationMs
      gapDurationMs = 0
      detectionReason = aecEnabled ? 'sustained-energy-candidate-with-aec' : 'sustained-energy-candidate-no-aec'
    } else if (aboveThreshold) {
      candidateDurationMs += durationMs
      gapDurationMs = 0
    } else {
      gapDurationMs += durationMs
      if (gapDurationMs > config.allowedGapMs) {
        state = BargeInState.REJECTED_AS_NOISE
        stateDurationMs = 0
        candidateDurationMs = 0
        gapDurationMs = 0
        interruptionConfidence = 0
        detectionReason = 'energy-not-sustained'
        rejected = true
      }
    }

    if (state === BargeInState.POSSIBLE_BARGE_IN) {
      const durationConfidence = Math.min(1, candidateDurationMs / config.confirmationMs)
      const energyConfidence = Math.min(1, Math.max(0, rms / Math.max(startThreshold, 1e-6) - 1) / 1.5)
      interruptionConfidence = Number((durationConfidence * 0.7 + energyConfidence * 0.3).toFixed(3))
      if (candidateDurationMs >= config.confirmationMs) {
        state = BargeInState.CONFIRMED_BARGE_IN
        stateDurationMs = 0
        interruptionConfidence = Math.max(0.85, interruptionConfidence)
        detectionReason = 'candidate-speech-sustained'
        confirmed = true
      }
    }

    return { ...getSnapshot(), rms, peak, confirmed, rejected }
  }

  function updateThresholds(aecEnabled) {
    const minRms = aecEnabled ? config.minRmsWithAec : config.minRmsWithoutAec
    const ratio = aecEnabled ? config.aecNoiseRatio : config.noAecNoiseRatio
    startThreshold = Math.max(minRms, echoFloor * ratio + config.thresholdMargin)
    peakThreshold = Math.max(
      aecEnabled ? config.minPeakWithAec : config.minPeakWithoutAec,
      startThreshold * 1.8,
    )
  }

  function updateEchoBaseline(rms) {
    if (!Number.isFinite(rms) || rms < 0 || rms >= startThreshold * 0.85) return
    baselineFrames.push(Math.min(rms, config.maxEchoFloor))
    if (baselineFrames.length > config.baselineWindowFrames) baselineFrames.shift()
    if (baselineFrames.length < 8) return
    const sorted = [...baselineFrames].sort((left, right) => left - right)
    const percentile = sorted[Math.floor((sorted.length - 1) * 0.3)]
    echoFloor = Math.min(config.maxEchoFloor, Math.max(config.fallbackEchoFloor, percentile))
  }

  function getSnapshot() {
    return {
      state,
      activeSpeechId,
      echoFloor,
      startThreshold,
      peakThreshold,
      candidateDurationMs,
      warmupRemainingMs: Math.max(0, config.warmupMs - warmupDurationMs),
      interruptionConfidence,
      detectionReason,
    }
  }

  return { processAudioFrame, reset, getSnapshot }
}

function checkEligibility(metadata) {
  if (!metadata.enabled) return { eligible: false, reason: 'feature-disabled' }
  if (!metadata.speechId) return { eligible: false, reason: 'no-active-speech' }
  if (metadata.conversationState !== ConversationState.SPEAKING) return { eligible: false, reason: 'conversation-not-speaking' }
  if (!metadata.deviceActive) return { eligible: false, reason: 'microphone-inactive' }
  if (!metadata.interviewActive) return { eligible: false, reason: 'interview-inactive' }
  if (!metadata.ttsPlaying) return { eligible: false, reason: 'tts-not-playing' }
  if (metadata.interrupting) return { eligible: false, reason: 'interrupt-already-running' }
  if (metadata.playbackGuardActive) return { eligible: false, reason: 'playback-guard-active' }
  if (metadata.gateState !== AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN) {
    return { eligible: false, reason: 'audio-gate-not-speaking-blocked' }
  }
  return { eligible: true, reason: 'eligible' }
}

function positive(value, fallback) {
  return Number.isFinite(value) && value > 0 ? value : fallback
}

function inferDuration(samples, sampleRate) {
  return samples?.length && sampleRate ? samples.length / sampleRate * 1000 : 0
}

function calculateRms(samples) {
  if (!samples?.length) return 0
  let energy = 0
  for (const sample of samples) energy += sample * sample
  return Math.sqrt(energy / samples.length)
}

function calculatePeak(samples) {
  if (!samples?.length) return 0
  let peak = 0
  for (const sample of samples) peak = Math.max(peak, Math.abs(sample))
  return peak
}
