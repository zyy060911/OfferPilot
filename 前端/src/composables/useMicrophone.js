import { computed, onUnmounted, ref } from 'vue'
import { AudioGateState } from './useInterviewAudioGate'
import { createAdaptiveEnergyVad, SpeechActivityState } from './adaptiveEnergyVad'

const TARGET_SAMPLE_RATE = 16000
const PRE_ROLL_MS = 300
const BLOCKED_METRICS_INTERVAL_MS = 2000

export const DeviceCaptureState = Object.freeze({
  IDLE: 'idle',
  REQUESTING: 'requesting',
  ACTIVE: 'active',
  STOPPED: 'stopped',
  ERROR: 'error',
})

export function useMicrophone({
  onSegment,
  onEndpointing,
  onReliableSpeechStarted,
  onReliableSpeechEnded,
  onDeviceError,
  onDiagnostic,
  onBlockedAudioFrame,
  mediaDevices = globalThis.navigator?.mediaDevices,
  AudioContextClass = globalThis.AudioContext,
  AudioWorkletNodeClass = globalThis.AudioWorkletNode,
  logger = console,
  now = () => performance.now(),
  segmentSilenceMs = 3000,
  maxSegmentMs = 28000,
  speechActivityDetector = createAdaptiveEnergyVad(),
} = {}) {
  const deviceState = ref(DeviceCaptureState.IDLE)
  const gateState = ref(AudioGateState.BLOCKED_WHEN_INTERVIEW_INACTIVE)
  const gateReason = ref('microphone-not-authorized')
  const level = ref(0)
  const isSpeaking = ref(false)
  const errorMessage = ref('')

  let stream = null
  let audioContext = null
  let sourceNode = null
  let processorNode = null
  let silentGainNode = null
  let disposed = false
  let stopping = false
  let requestId = 0
  let segmentChunks = []
  let preRollChunks = []
  let segmentStartedAt = 0
  let lastVoiceAt = 0
  let voicedDurationMs = 0
  let reliableSpeechActive = false
  let reliableSpeechStartedAt = 0
  let blockedMetrics = createBlockedMetrics()
  let currentRms = 0
  let actualDeviceSettings = null
  let currentVadSnapshot = speechActivityDetector.getSnapshot()

  const isDeviceActive = computed(() => deviceState.value === DeviceCaptureState.ACTIVE)
  const isRequesting = computed(() => deviceState.value === DeviceCaptureState.REQUESTING)
  const isAcceptingAudio = computed(() => (
    isDeviceActive.value && gateState.value === AudioGateState.ACCEPTING_CANDIDATE_AUDIO
  ))
  const isAudioWorkletRunning = computed(() => Boolean(isDeviceActive.value && processorNode && audioContext))

  function log(event, metadata = {}) {
    logger.info?.('[MicrophoneCapture]', {
      event,
      deviceState: deviceState.value,
      gateState: gateState.value,
      gateReason: gateReason.value,
      timestamp: new Date().toISOString(),
      ...metadata,
    })
  }

  async function initializeMicrophone() {
    if (stream && isDeviceActive.value) return true
    if (!mediaDevices?.getUserMedia || !AudioContextClass || !AudioWorkletNodeClass) {
      deviceState.value = DeviceCaptureState.ERROR
      errorMessage.value = '当前浏览器不支持麦克风，请使用最新版 Chrome 或 Edge。'
      return false
    }

    deviceState.value = DeviceCaptureState.REQUESTING
    errorMessage.value = ''
    const currentRequestId = ++requestId

    try {
      const newStream = await mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
        },
        video: false,
      })

      if (disposed || currentRequestId !== requestId) {
        newStream.getTracks().forEach((track) => track.stop())
        return false
      }

      stream = newStream
      audioContext = new AudioContextClass()
      await audioContext.audioWorklet.addModule('/audio/pcm-capture-processor.js')
      sourceNode = audioContext.createMediaStreamSource(stream)
      processorNode = new AudioWorkletNodeClass(audioContext, 'pcm-capture-processor')
      silentGainNode = audioContext.createGain()
      silentGainNode.gain.value = 0
      processorNode.port.onmessage = ({ data }) => handleAudioChunk(new Float32Array(data))
      sourceNode.connect(processorNode)
      processorNode.connect(silentGainNode)
      silentGainNode.connect(audioContext.destination)

      for (const track of stream.getAudioTracks()) {
        track.enabled = true
        track.addEventListener?.('ended', handleTrackEnded)
        logDeviceCapabilities(track)
      }
      await audioContext.resume()
      speechActivityDetector.reset('audio-context-created')
      if (gateState.value !== AudioGateState.ACCEPTING_CANDIDATE_AUDIO) {
        speechActivityDetector.suspend(gateReason.value, now())
      }
      currentVadSnapshot = speechActivityDetector.getSnapshot()
      deviceState.value = DeviceCaptureState.ACTIVE
      log('microphone-device-started', { sampleRate: audioContext.sampleRate })
      return true
    } catch (error) {
      await cleanupAudioGraph()
      deviceState.value = DeviceCaptureState.ERROR
      setDeviceErrorMessage(error)
      log('microphone-device-error', { error: error?.message || String(error) })
      return false
    }
  }

  function logDeviceCapabilities(track) {
    const settings = track.getSettings?.() || {}
    const constraints = track.getConstraints?.() || {}
    actualDeviceSettings = {
      echoCancellation: settings.echoCancellation ?? null,
      noiseSuppression: settings.noiseSuppression ?? null,
      autoGainControl: settings.autoGainControl ?? null,
      sampleRate: settings.sampleRate ?? null,
      channelCount: settings.channelCount ?? null,
    }
    log('microphone-device-capabilities', {
      requestedConstraints: constraints,
      actualSettings: {
        ...actualDeviceSettings,
        deviceIdPresent: Boolean(settings.deviceId),
      },
    })
  }

  function setDeviceErrorMessage(error) {
    if (error?.name === 'NotAllowedError' || error?.name === 'SecurityError') {
      errorMessage.value = '麦克风权限被拒绝，请在浏览器地址栏中允许访问。'
    } else if (error?.name === 'NotFoundError') {
      errorMessage.value = '没有找到可用的麦克风设备。'
    } else if (error?.name === 'NotReadableError' || error?.name === 'AbortError') {
      errorMessage.value = '麦克风可能正被其他程序占用，请关闭后重试。'
    } else {
      errorMessage.value = '麦克风开启失败，请检查设备和浏览器权限。'
    }
  }

  function setAudioGate(nextState, {
    reason = 'unspecified',
    residualPolicy = 'discard',
    speechId = null,
  } = {}) {
    flushBlockedMetrics('gate-state-changed')
    const wasAccepting = gateState.value === AudioGateState.ACCEPTING_CANDIDATE_AUDIO
    const willAccept = nextState === AudioGateState.ACCEPTING_CANDIDATE_AUDIO
    if (wasAccepting && !willAccept && segmentStartedAt) {
      if (residualPolicy === 'flush') {
        finishSegment(`gate-closed:${reason}`)
      } else {
        log('audio-gate-residual-discarded', {
          reason,
          speechId,
          chunkCount: segmentChunks.length,
          voicedDurationMs,
        })
        resetSegment()
      }
    } else {
      resetSegment()
    }

    gateState.value = nextState
    gateReason.value = reason
    if (willAccept) speechActivityDetector.resume(reason, now())
    else speechActivityDetector.suspend(reason, now())
    currentVadSnapshot = speechActivityDetector.getSnapshot()
    blockedMetrics = createBlockedMetrics()
    log(willAccept ? 'audio-gate-opened' : 'audio-gate-closed', { reason, speechId, residualPolicy })
  }

  function handleAudioChunk(chunk) {
    if (!isDeviceActive.value || !audioContext) return

    const rms = calculateRms(chunk)
    currentRms = rms
    if (!isAcceptingAudio.value) {
      collectBlockedMetrics(chunk, rms)
      return
    }

    const currentTime = now()
    const chunkDurationMs = chunk.length / audioContext.sampleRate * 1000
    const vad = speechActivityDetector.processAudioFrame(chunk, {
      timestamp: currentTime,
      durationMs: chunkDurationMs,
      sampleRate: audioContext.sampleRate,
      gateOpen: true,
    })
    currentVadSnapshot = vad
    currentRms = vad.rms
    level.value = Math.min(1, level.value * 0.62 + rms * 8 * 0.38)
    const possibleVoice = [SpeechActivityState.POSSIBLE_SPEECH, SpeechActivityState.SPEECH].includes(vad.state)

    if (!segmentStartedAt) {
      preRollChunks.push(chunk)
      trimPreRoll(audioContext.sampleRate)
      if (!possibleVoice) return

      segmentStartedAt = vad.speechStartedAt || currentTime - chunkDurationMs
      lastVoiceAt = vad.lastSpeechAt || currentTime
      voicedDurationMs = vad.speechStarted ? vad.validSpeechDuration : 0
      segmentChunks = preRollChunks
      preRollChunks = []
      isSpeaking.value = true
      if (vad.speechStarted) emitReliableSpeechStarted(vad, currentTime)
      return
    }

    segmentChunks.push(chunk)
    if (vad.state === SpeechActivityState.SPEECH) {
      lastVoiceAt = vad.lastSpeechAt || currentTime
      voicedDurationMs += vad.speechStarted ? vad.validSpeechDuration : chunkDurationMs
      isSpeaking.value = true
      if (vad.speechStarted) emitReliableSpeechStarted(vad, currentTime)
    } else if (vad.state === SpeechActivityState.POSSIBLE_SPEECH) {
      isSpeaking.value = true
    } else if (vad.state === SpeechActivityState.POSSIBLE_SILENCE) {
      isSpeaking.value = true
    } else {
      isSpeaking.value = false
      if (vad.speechEnded && vad.lastSpeechAt) lastVoiceAt = vad.lastSpeechAt
    }

    if (lastVoiceAt && currentTime - lastVoiceAt >= segmentSilenceMs) {
      finishSegment('silence')
      return
    }

    if (currentTime - segmentStartedAt >= maxSegmentMs) finishSegment('max-duration')
  }

  function emitReliableSpeechStarted(vad, currentTime) {
    if (reliableSpeechActive) return
    reliableSpeechActive = true
    reliableSpeechStartedAt = vad.speechStartedAt || segmentStartedAt
    onReliableSpeechStarted?.({ startedAt: reliableSpeechStartedAt, detectedAt: currentTime })
  }

  function collectBlockedMetrics(chunk, rms) {
    blockedMetrics.chunkCount++
    blockedMetrics.sampleCount += chunk.length
    blockedMetrics.sumSquares += rms * rms * chunk.length
    let chunkPeak = 0
    for (let index = 0; index < chunk.length; index++) {
      chunkPeak = Math.max(chunkPeak, Math.abs(chunk[index]))
      blockedMetrics.peak = Math.max(blockedMetrics.peak, chunkPeak)
    }
    level.value = 0
    isSpeaking.value = false

    const currentTime = now()
    if (!blockedMetrics.startedAt) blockedMetrics.startedAt = currentTime
    onBlockedAudioFrame?.(chunk, {
      timestamp: currentTime,
      durationMs: audioContext ? chunk.length / audioContext.sampleRate * 1000 : 0,
      sampleRate: audioContext?.sampleRate || null,
      rms,
      peak: chunkPeak,
      blockedBaselineRms: blockedMetrics.sampleCount
        ? Math.sqrt(blockedMetrics.sumSquares / blockedMetrics.sampleCount)
        : 0,
      gateState: gateState.value,
      gateReason: gateReason.value,
      actualDeviceSettings,
    })
    if (currentTime - blockedMetrics.startedAt < BLOCKED_METRICS_INTERVAL_MS) return
    flushBlockedMetrics('periodic')
  }

  function flushBlockedMetrics(flushReason) {
    if (!blockedMetrics.chunkCount) return
    const currentTime = now()
    const summary = {
      reason: gateReason.value,
      flushReason,
      durationMs: Math.max(0, currentTime - blockedMetrics.startedAt),
      rms: blockedMetrics.sampleCount
        ? Math.sqrt(blockedMetrics.sumSquares / blockedMetrics.sampleCount)
        : 0,
      peak: blockedMetrics.peak,
      chunkCount: blockedMetrics.chunkCount,
      asrSegmentsCreated: 0,
    }
    log('blocked-period-rms-summary', summary)
    onDiagnostic?.(summary)
    blockedMetrics = createBlockedMetrics()
  }

  function trimPreRoll(inputSampleRate) {
    const maxSamples = Math.round(inputSampleRate * PRE_ROLL_MS / 1000)
    let total = preRollChunks.reduce((sum, chunk) => sum + chunk.length, 0)
    while (preRollChunks.length > 1 && total > maxSamples) total -= preRollChunks.shift().length
  }

  function finishSegment(reason = 'manual-flush') {
    if (!segmentStartedAt) return false
    const chunks = segmentChunks
    const inputSampleRate = audioContext?.sampleRate || 48000
    const duration = chunks.reduce((sum, chunk) => sum + chunk.length, 0) / inputSampleRate
    const shouldSend = reliableSpeechActive && duration > 0
    const captureStartedAt = segmentStartedAt
    const captureEndedAt = reason === 'silence' ? lastVoiceAt : now()
    const preserveReliableSpeech = reason === 'max-duration' && reliableSpeechActive
    onEndpointing?.({ reason, duration, willTranscribe: shouldSend, captureStartedAt, captureEndedAt })
    if (reliableSpeechActive && !preserveReliableSpeech) {
      onReliableSpeechEnded?.({
        startedAt: reliableSpeechStartedAt,
        endedAt: captureEndedAt,
        detectedAt: now(),
        reason,
      })
    }
    resetSegment({ preserveReliableSpeech })
    if (!preserveReliableSpeech) {
      speechActivityDetector.reset(`segment-finished:${reason}`, { preserveCalibration: true })
      currentVadSnapshot = speechActivityDetector.getSnapshot()
    }

    if (shouldSend) {
      const merged = mergeChunks(chunks)
      const resampled = resampleAudio(merged, inputSampleRate, TARGET_SAMPLE_RATE)
      onSegment?.(
        encodeWav(resampled, TARGET_SAMPLE_RATE),
        Math.min(duration, maxSegmentMs / 1000),
        { reason, captureStartedAt, captureEndedAt },
      )
    }
    return shouldSend
  }

  function resetSegment({ preserveReliableSpeech = false } = {}) {
    segmentChunks = []
    preRollChunks = []
    segmentStartedAt = 0
    lastVoiceAt = 0
    voicedDurationMs = 0
    if (!preserveReliableSpeech) {
      reliableSpeechActive = false
      reliableSpeechStartedAt = 0
    }
    isSpeaking.value = false
    level.value = 0
  }

  async function stopMicrophone({ flush = false, reason = 'device-stop' } = {}) {
    requestId++
    flushBlockedMetrics('device-stopped')
    if (flush && isAcceptingAudio.value) finishSegment(reason)
    else resetSegment()
    await cleanupAudioGraph()
    speechActivityDetector.reset(reason)
    currentVadSnapshot = speechActivityDetector.getSnapshot()
    if (deviceState.value !== DeviceCaptureState.ERROR) deviceState.value = DeviceCaptureState.STOPPED
    errorMessage.value = ''
    log('microphone-device-stopped', { reason })
  }

  async function cleanupAudioGraph() {
    stopping = true
    processorNode?.disconnect()
    sourceNode?.disconnect()
    silentGainNode?.disconnect()
    if (processorNode) processorNode.port.onmessage = null
    for (const track of stream?.getTracks?.() || []) {
      track.removeEventListener?.('ended', handleTrackEnded)
      track.stop()
    }
    try {
      await audioContext?.close?.()
    } catch {
      // 设备清理继续完成，关闭失败只影响浏览器内部状态。
    }
    stream = null
    audioContext = null
    sourceNode = null
    processorNode = null
    silentGainNode = null
    stopping = false
  }

  async function handleTrackEnded() {
    if (stopping || disposed) return
    const error = '麦克风设备已断开。'
    deviceState.value = DeviceCaptureState.ERROR
    errorMessage.value = error
    resetSegment()
    speechActivityDetector.reset('device-track-ended')
    currentVadSnapshot = speechActivityDetector.getSnapshot()
    await cleanupAudioGraph()
    log('microphone-device-error', { error })
    onDeviceError?.({ source: 'microphone', error, recoverable: true })
  }

  function getCaptureSnapshot() {
    return {
      segmentChunkCount: segmentChunks.length,
      preRollChunkCount: preRollChunks.length,
      segmentStarted: Boolean(segmentStartedAt),
      voicedDurationMs,
      reliableSpeechActive,
      deviceState: deviceState.value,
      gateState: gateState.value,
      currentRms,
      level: level.value,
      isSpeaking: isSpeaking.value,
      noiseBaseline: currentVadSnapshot.noiseFloor,
      vadState: currentVadSnapshot.state,
      vadReason: currentVadSnapshot.reason,
      vadConfidence: currentVadSnapshot.confidence,
      vadSignalToNoiseRatio: currentVadSnapshot.signalToNoiseRatio,
      vadStartThreshold: currentVadSnapshot.startThreshold,
      vadContinueThreshold: currentVadSnapshot.continueThreshold,
      vadPeak: currentVadSnapshot.peak,
      vadCalibrationActive: currentVadSnapshot.calibrationActive,
      vadCalibrationProgress: currentVadSnapshot.calibrationProgress,
      vadSuspended: currentVadSnapshot.suspended,
      actualDeviceSettings,
      blockedChunkCount: blockedMetrics.chunkCount,
    }
  }

  onUnmounted(() => {
    disposed = true
    void stopMicrophone({ reason: 'component-unmounted' })
  })

  return {
    deviceState,
    gateState,
    gateReason,
    level,
    isSpeaking,
    errorMessage,
    isDeviceActive,
    isRequesting,
    isAcceptingAudio,
    isAudioWorkletRunning,
    initializeMicrophone,
    openMicrophone: initializeMicrophone,
    setAudioGate,
    finishSegment,
    resetSegment,
    stopMicrophone,
    handleAudioChunk,
    getCaptureSnapshot,
  }
}

function createBlockedMetrics() {
  return { startedAt: 0, chunkCount: 0, sampleCount: 0, sumSquares: 0, peak: 0 }
}

function calculateRms(chunk) {
  let energy = 0
  for (let index = 0; index < chunk.length; index++) energy += chunk[index] * chunk[index]
  return chunk.length ? Math.sqrt(energy / chunk.length) : 0
}

function mergeChunks(chunks) {
  const length = chunks.reduce((sum, chunk) => sum + chunk.length, 0)
  const merged = new Float32Array(length)
  let offset = 0
  for (const chunk of chunks) {
    merged.set(chunk, offset)
    offset += chunk.length
  }
  return merged
}

function resampleAudio(input, inputRate, outputRate) {
  if (inputRate === outputRate) return input
  const outputLength = Math.round(input.length * outputRate / inputRate)
  const output = new Float32Array(outputLength)
  const ratio = inputRate / outputRate
  for (let index = 0; index < outputLength; index++) {
    const position = index * ratio
    const left = Math.floor(position)
    const right = Math.min(left + 1, input.length - 1)
    const fraction = position - left
    output[index] = input[left] * (1 - fraction) + input[right] * fraction
  }
  return output
}

function encodeWav(samples, sampleRate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)
  writeAscii(view, 0, 'RIFF')
  view.setUint32(4, 36 + samples.length * 2, true)
  writeAscii(view, 8, 'WAVE')
  writeAscii(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeAscii(view, 36, 'data')
  view.setUint32(40, samples.length * 2, true)

  let offset = 44
  for (let index = 0; index < samples.length; index++, offset += 2) {
    const sample = Math.max(-1, Math.min(1, samples[index]))
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
  }
  return new Blob([buffer], { type: 'audio/wav' })
}

function writeAscii(view, offset, text) {
  for (let index = 0; index < text.length; index++) view.setUint8(offset + index, text.charCodeAt(index))
}
