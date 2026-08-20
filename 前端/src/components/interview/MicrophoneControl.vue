<template>
  <div class="voice-answer">
    <span v-if="errorMessage" class="mic-error">{{ errorMessage }}</span>
    <div v-if="hasFailedSegments" class="recovery-actions">
      <button type="button" class="btn-ghost" @click="retryFailedRecognition">重试识别</button>
      <button v-if="transcript" type="button" class="btn-ghost" @click="submitRecognizedText">提交已识别文字</button>
    </div>

    <div class="voice-footer">
      <div class="mic-copy">
        <span class="mic-status">{{ statusText }}</span>
        <span class="voice-only-hint">语音文字显示在上方，可滚轮翻阅</span>
      </div>

      <div class="voice-actions">
        <button type="button" class="btn-ghost" :disabled="disabled" @click="requestSkip">
          跳过
        </button>
        <button
          type="button"
          class="btn-send"
          :disabled="disabled || isRequesting || (!transcript && !isAcceptingAudio)"
          @click="requestSubmit"
        >
          提交
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>
          </svg>
        </button>
        <button
          type="button"
          :class="['mic-control', { open: isAcceptingAudio, speaking: isSpeaking, active: isDeviceActive }]"
          :style="{ '--voice-level': level }"
          :disabled="isRequesting || disabled"
          :title="statusText"
          @click="toggleMicrophone"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line v-if="!isAcceptingAudio" x1="4" y1="4" x2="20" y2="20"/>
          </svg>
        </button>
      </div>
    </div>
    <details v-if="debugEnabled" class="audio-diagnostics">
      <summary>音频诊断</summary>
      <pre>{{ formattedDiagnostics }}</pre>
    </details>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { transcribeSpeech } from '../../api'
import { useMicrophone } from '../../composables/useMicrophone'
import { AudioGateState } from '../../composables/useInterviewAudioGate'
import { ConversationState } from '../../composables/useInterviewConversation'
import { resolveInterviewAudioTiming } from '../../composables/interviewAudioTiming'
import { useAnswerAggregation } from '../../composables/useAnswerAggregation'
import { useAnswerEndpointing } from '../../composables/useAnswerEndpointing'
import { detectEnumerationProgress, evaluateAnswerCompleteness } from '../../composables/answerCompleteness'
import { createBargeInDetector } from '../../composables/bargeInDetector'

const props = defineProps({
  sessionId: { type: Number, default: null },
  questionId: { type: Number, default: null },
  questionText: { type: String, default: '' },
  questionType: { type: String, default: '' },
  transcript: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  audioGateState: { type: String, default: AudioGateState.BLOCKED_WHEN_INTERVIEW_INACTIVE },
  audioGateReason: { type: String, default: '' },
  conversationState: { type: String, default: ConversationState.WAITING },
  resumeBlocked: { type: Boolean, default: false },
  activeSpeechId: { type: String, default: null },
  bargeInEnabled: { type: Boolean, default: false },
  interviewActive: { type: Boolean, default: false },
})

const emit = defineEmits([
  'transcript', 'processing', 'submit', 'skip', 'microphone-opened', 'microphone-muted',
  'microphone-device-started', 'submit-requested', 'diagnostic', 'endpointing', 'possible-end',
  'possible-end-cancelled', 'finalization-error', 'error',
  'barge-in',
])
const pendingCount = ref(0)
const recognitionError = ref('')
const interactionHint = ref('')
const debugEnabled = import.meta.env.DEV || import.meta.env.VITE_INTERVIEW_AUDIO_DEBUG === 'true'
const diagnosticSnapshot = ref(null)
const lastBlockedMetrics = ref(null)
const bargeInDetector = createBargeInDetector()
const bargeInSnapshot = ref(bargeInDetector.getSnapshot())
const bargeInInterrupting = ref(false)
const timing = resolveInterviewAudioTiming()
const aggregation = useAnswerAggregation()
const segmentAudio = new Map()
let generation = 0
let finalizationTimer = null

const hasFailedSegments = computed(() => Boolean(aggregation.currentAnswer.value?.failedSegments.length))
const formattedDiagnostics = computed(() => JSON.stringify(diagnosticSnapshot.value, null, 2))
const endpointing = useAnswerEndpointing({
  timing,
  isEligible: isEndpointingEligible,
  onPossibleEnd: (metadata) => emit('possible-end', metadata),
  onPossibleEndCancelled: (metadata) => emit('possible-end-cancelled', metadata),
  onConfirmed: () => requestFinalization('auto'),
  evaluateConfirmation: evaluateCompletenessAtPossibleEnd,
})

const {
  deviceState, level, isSpeaking, errorMessage: deviceError, isDeviceActive, isAcceptingAudio,
  isAudioWorkletRunning, isRequesting, initializeMicrophone, setAudioGate, finishSegment,
  stopMicrophone: stopDevice, getCaptureSnapshot,
} = useMicrophone({
  onSegment: queueTranscription,
  onEndpointing: handleEndpointing,
  onReliableSpeechStarted: handleReliableSpeechStarted,
  onReliableSpeechEnded: handleReliableSpeechEnded,
  onDeviceError: (error) => emit('error', error),
  onDiagnostic: handleDiagnostic,
  onBlockedAudioFrame: handleBlockedAudioFrame,
  segmentSilenceMs: timing.segmentSilenceMs,
  maxSegmentMs: timing.maxSegmentMs,
})

let diagnosticTimer = null
if (debugEnabled) {
  diagnosticTimer = setInterval(refreshDiagnostics, 250)
  refreshDiagnostics()
}

watch(
  () => [props.activeSpeechId, props.conversationState, props.audioGateState, props.bargeInEnabled],
  ([speechId, conversationState, gateState, enabled], previous = []) => {
    const speechChanged = speechId !== previous[0]
    if (speechChanged || !enabled || conversationState !== ConversationState.SPEAKING
      || gateState !== AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN) {
      bargeInSnapshot.value = bargeInDetector.reset(
        !enabled ? 'feature-disabled' : speechChanged ? 'speech-context-changed' : 'barge-in-ineligible',
      )
    }
    if (speechChanged || ![ConversationState.SPEAKING, ConversationState.INTERRUPTING].includes(conversationState)) {
      bargeInInterrupting.value = false
    }
  },
  { immediate: true },
)

const errorMessage = computed(() => interactionHint.value || recognitionError.value || deviceError.value)
const statusText = computed(() => {
  const answerState = aggregation.currentAnswer.value
  if (isRequesting.value) return '正在申请麦克风权限...'
  if (answerState?.submitState === 'submitting') return '正在提交'
  if (answerState?.finalizationState === 'finalizing' && pendingCount.value > 0) return '正在识别最后一段'
  if (props.conversationState === ConversationState.POSSIBLE_END) return '检测到停顿，等待继续回答'
  if (pendingCount.value > 0) return '正在整理回答'
  if (isDeviceActive.value && props.audioGateState === AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN) {
    return props.bargeInEnabled ? '面试官正在说话，持续讲话可打断' : '面试官正在说话，麦克风保持采集但不会识别'
  }
  if (isDeviceActive.value && props.audioGateState === AudioGateState.BLOCKED_DURING_TRANSITION) return '正在等待面试官语音结束，请稍候'
  if (isSpeaking.value) return '正在讲话，停顿后自动识别'
  if (isAcceptingAudio.value) return '正在聆听，点击可暂停回答'
  if (isDeviceActive.value) return '回答已暂停，设备仍在采集；点击恢复回答'
  if (deviceState.value === 'error') return '麦克风异常，点击重试'
  return '点击开始回答并授权麦克风'
})

watch(() => [props.audioGateState, props.audioGateReason], ([nextState, reason]) => {
  if (nextState === AudioGateState.ACCEPTING_CANDIDATE_AUDIO) interactionHint.value = ''
  else endpointing.cancel(`gate-closed:${reason}`)
  setAudioGate(nextState, { reason: reason || 'parent-state-updated', residualPolicy: 'discard' })
}, { immediate: true, flush: 'sync' })

watch(() => [props.sessionId, props.questionId], ([nextSessionId, nextQuestionId]) => {
  if (nextSessionId && nextQuestionId && !aggregation.currentAnswer.value) beginAnswer({ sessionId: nextSessionId, questionId: nextQuestionId })
}, { immediate: true })

function ensureAnswer() {
  return aggregation.currentAnswer.value || beginAnswer({ sessionId: props.sessionId, questionId: props.questionId })
}

function beginAnswer({ sessionId = props.sessionId, questionId = props.questionId } = {}) {
  endpointing.cancel('new-answer')
  clearTimeout(finalizationTimer)
  recognitionError.value = ''
  segmentAudio.clear()
  const answer = aggregation.createAnswer({ sessionId, questionId })
  emit('transcript', '')
  return answer
}

function queueTranscription(blob, duration, capture = {}) {
  if (!props.sessionId) return
  ensureAnswer()
  const segment = aggregation.addSegment(capture)
  if (!segment) return
  segmentAudio.set(segment.segmentId, { blob, duration })
  transcribeSegment(segment, blob, duration)
}

function transcribeSegment(segment, blob, duration) {
  const currentGeneration = generation
  pendingCount.value++
  recognitionError.value = ''
  emitProcessing(true)
  Promise.resolve(transcribeSpeech(blob, props.sessionId, duration))
    .then((result) => {
      if (currentGeneration !== generation) return
      aggregation.resolveSegment(segment.answerId, segment.segmentId, result?.text || '')
      emit('transcript', aggregation.transcript.value)
    })
    .catch((error) => {
      if (currentGeneration !== generation) return
      recognitionError.value = error.response?.data?.message || error.message || '语音识别失败，请重试。'
      aggregation.failSegment(segment.answerId, segment.segmentId, recognitionError.value)
    })
    .finally(() => {
      if (currentGeneration !== generation) return
      pendingCount.value = Math.max(0, pendingCount.value - 1)
      if (pendingCount.value === 0) emitProcessing(false, { failed: hasFailedSegments.value })
      processFinalizationIfReady()
    })
}

function endpointContext(metadata = {}) {
  const answer = aggregation.currentAnswer.value
  return { ...metadata, sessionId: answer?.sessionId, questionId: answer?.questionId, answerId: answer?.answerId, answerEpoch: answer?.answerEpoch }
}

function evaluateCompletenessAtPossibleEnd(metadata = {}) {
  const answerState = aggregation.currentAnswer.value
  const completedSegments = (answerState?.segments || [])
    .filter((segment) => segment.transcriptionState === 'completed' && segment.transcript)
    .sort((left, right) => left.sequence - right.sequence)
  const transcript = aggregation.transcript.value
  return evaluateAnswerCompleteness({
    questionText: props.questionText,
    questionType: props.questionType,
    transcript,
    lastCompletedSegmentText: completedSegments.at(-1)?.transcript || '',
    pendingSegmentCount: answerState?.pendingSegmentCount ?? pendingCount.value,
    silenceDurationMs: metadata.endedAt == null ? 0 : Math.max(0, performance.now() - metadata.endedAt),
    answerId: answerState?.answerId || metadata.answerId,
    isPossibleEnd: true,
    enumerationProgress: detectEnumerationProgress(props.questionText, transcript),
  }, {
    fallbackConfirmMs: timing.answerConfirmMs,
    minimumSilenceMs: timing.answerFinishMs,
  })
}

function isEndpointingEligible(context = {}) {
  const answer = aggregation.currentAnswer.value
  return Boolean(answer && context.answerId === answer.answerId && context.answerEpoch === answer.answerEpoch
    && answer.startedAt != null && answer.finalizationState === 'collecting'
    && props.audioGateState === AudioGateState.ACCEPTING_CANDIDATE_AUDIO
    && [ConversationState.LISTENING, ConversationState.ENDPOINTING, ConversationState.TRANSCRIBING, ConversationState.POSSIBLE_END].includes(props.conversationState))
}

function handleReliableSpeechStarted(metadata) {
  ensureAnswer()
  aggregation.markSpeechStarted(metadata.startedAt)
  endpointing.speechStarted(endpointContext(metadata))
}

function handleReliableSpeechEnded(metadata) {
  if (aggregation.markSpeechEnded(metadata.endedAt)) endpointing.speechEnded(endpointContext(metadata))
}

function handleEndpointing(details) {
  emit('endpointing', { ...details, microphoneOpen: isAcceptingAudio.value })
}

function emitProcessing(active, extra = {}) {
  emit('processing', { active, pendingCount: pendingCount.value, microphoneOpen: isAcceptingAudio.value, ...extra })
}

function handleDiagnostic(summary) {
  lastBlockedMetrics.value = summary
  emit('diagnostic', summary)
}

function handleBlockedAudioFrame(samples, metadata = {}) {
  const result = bargeInDetector.processAudioFrame(samples, {
    ...metadata,
    enabled: props.bargeInEnabled,
    speechId: props.activeSpeechId,
    conversationState: props.conversationState,
    deviceActive: isDeviceActive.value,
    interviewActive: props.interviewActive,
    ttsPlaying: props.conversationState === ConversationState.SPEAKING,
    interrupting: bargeInInterrupting.value,
    playbackGuardActive: props.audioGateReason === 'playback-tail-guard',
    gateState: props.audioGateState,
    aecEnabled: metadata.actualDeviceSettings?.echoCancellation === true,
  })
  bargeInSnapshot.value = result
  if (!result.confirmed || bargeInInterrupting.value) return
  bargeInInterrupting.value = true
  emit('barge-in', {
    speechId: props.activeSpeechId,
    interruptionConfidence: result.interruptionConfidence,
    detectionReason: result.detectionReason,
    echoFloor: result.echoFloor,
    startThreshold: result.startThreshold,
    timestamp: new Date().toISOString(),
  })
}

function refreshDiagnostics() {
  const answer = aggregation.currentAnswer.value
  const capture = getCaptureSnapshot()
  diagnosticSnapshot.value = {
    conversationState: props.conversationState,
    deviceState: capture.deviceState,
    audioGateState: props.audioGateState,
    audioGateReason: props.audioGateReason,
    answerId: answer?.answerId ?? null,
    answerEpoch: answer?.answerEpoch ?? null,
    segmentSequence: answer?.segmentSequence ?? 0,
    rms: Number(capture.currentRms || 0).toFixed(5),
    noiseBaseline: capture.noiseBaseline,
    vadState: capture.vadState,
    vadReason: capture.vadReason,
    vadConfidence: capture.vadConfidence,
    vadSignalToNoiseRatio: capture.vadSignalToNoiseRatio,
    vadStartThreshold: capture.vadStartThreshold,
    vadContinueThreshold: capture.vadContinueThreshold,
    vadPeak: capture.vadPeak,
    vadCalibrationActive: capture.vadCalibrationActive,
    vadCalibrationProgress: capture.vadCalibrationProgress,
    vadSuspended: capture.vadSuspended,
    isSpeaking: capture.isSpeaking,
    voicedDurationMs: Math.round(capture.voicedDurationMs || 0),
    ...endpointing.getSnapshot(),
    pendingSegmentCount: answer?.pendingSegmentCount ?? 0,
    finalizationState: answer?.finalizationState ?? null,
    submitSource: answer?.finalizationSource ?? null,
    playbackGuardActive: props.audioGateReason === 'playback-tail-guard',
    actualDeviceSettings: capture.actualDeviceSettings,
    blockedPeriodRmsSummary: lastBlockedMetrics.value,
    bargeInEnabled: props.bargeInEnabled,
    bargeInState: bargeInSnapshot.value.state,
    bargeInConfidence: bargeInSnapshot.value.interruptionConfidence,
    bargeInReason: bargeInSnapshot.value.detectionReason,
    bargeInEchoFloor: bargeInSnapshot.value.echoFloor,
    bargeInStartThreshold: bargeInSnapshot.value.startThreshold,
    bargeInCandidateDurationMs: bargeInSnapshot.value.candidateDurationMs,
  }
}

async function toggleMicrophone() {
  interactionHint.value = ''
  if (isAcceptingAudio.value) {
    finishSegment('manual-pause-answer')
    emit('microphone-muted', { reason: 'manual-pause-answer' })
    return
  }
  if (props.resumeBlocked) {
    interactionHint.value = '面试官正在说话或准备下一题，请稍候再开始回答。'
    return
  }
  const wasActive = isDeviceActive.value
  const opened = await initializeMicrophone()
  if (opened) {
    if (!wasActive) emit('microphone-device-started', { deviceState: deviceState.value, audioWorkletRunning: isAudioWorkletRunning.value })
    emit('microphone-opened', { source: wasActive ? 'manual-resume-answer' : 'first-authorization' })
  } else emit('error', { source: 'microphone', error: deviceError.value || '麦克风开启失败', recoverable: true })
}

function muteMicrophone({ reason = 'external-mute' } = {}) { emit('microphone-muted', { reason }) }
function requestSubmit() { if (!props.disabled) requestFinalization('manual') }

function requestFinalization(source) {
  ensureAnswer()
  const ownership = aggregation.beginFinalization(source)
  if (!ownership.acquired) {
    interactionHint.value = ownership.reason === 'already-finalizing' ? '正在提交，请稍候。' : '尚未检测到有效语音。'
    return false
  }
  endpointing.cancel(`${source}-finalization`)
  if (isAcceptingAudio.value) finishSegment(source === 'auto' ? 'auto-finish' : 'manual-submit')
  setAudioGate(AudioGateState.BLOCKED_DURING_TRANSITION, { reason: 'answer-submit-requested', residualPolicy: 'discard' })
  emit('submit-requested', { pendingCount: pendingCount.value, source, answerId: ownership.answerId })
  clearTimeout(finalizationTimer)
  finalizationTimer = setTimeout(() => failFinalization('语音识别等待超时，可重试识别或提交已识别文字。'), timing.asrFinalizationTimeoutMs)
  processFinalizationIfReady()
  return true
}

function processFinalizationIfReady() {
  const answer = aggregation.currentAnswer.value
  if (!answer || answer.finalizationState !== 'finalizing' || answer.pendingSegmentCount > 0) return
  if (answer.failedSegments.length) return failFinalization('部分语音识别失败，可重试识别或提交已识别文字。')
  const payload = aggregation.markSubmitting()
  if (!payload) return failFinalization('未识别到有效回答，请继续作答。')
  clearTimeout(finalizationTimer)
  emit('submit', payload)
}

function failFinalization(message) {
  clearTimeout(finalizationTimer)
  aggregation.failPendingSegments(message)
  pendingCount.value = aggregation.currentAnswer.value?.pendingSegmentCount || 0
  aggregation.markRecoverableError(message)
  recognitionError.value = message
  emit('finalization-error', { source: 'asr-finalization', error: message, recoverable: true })
}

function retryFailedRecognition() {
  const failedIds = [...(aggregation.currentAnswer.value?.failedSegments || [])]
  if (!failedIds.length || !aggregation.beginFinalization('retry').acquired) return
  recognitionError.value = ''
  for (const segmentId of failedIds) {
    const segment = aggregation.retrySegment(segmentId)
    const audio = segmentAudio.get(segmentId)
    if (segment && audio) transcribeSegment(segment, audio.blob, audio.duration)
    else if (segment) aggregation.failSegment(segment.answerId, segment.segmentId, '原始音频已释放，无法重试')
  }
  finalizationTimer = setTimeout(() => failFinalization('语音识别等待超时，可再次重试。'), timing.asrFinalizationTimeoutMs)
  processFinalizationIfReady()
}

function submitRecognizedText() {
  aggregation.ignoreFailedSegments()
  requestFinalization('manual-confirm-recognized')
}

async function requestSkip() {
  generation++
  endpointing.cancel('question-skipped')
  pendingCount.value = 0
  emitProcessing(false)
  setAudioGate(AudioGateState.BLOCKED_DURING_TRANSITION, { reason: 'question-skip-requested', residualPolicy: 'discard' })
  emit('skip')
}

async function stopMicrophone() {
  generation++
  endpointing.dispose()
  aggregation.dispose()
  clearTimeout(finalizationTimer)
  pendingCount.value = 0
  emitProcessing(false)
  await stopDevice()
}

function completeSubmission({ success, error } = {}) {
  if (success) aggregation.markSubmitSucceeded()
  else failFinalization(error || '提交回答失败，请重试。')
}

function getDeviceSnapshot() {
  return { deviceState: deviceState.value, active: isDeviceActive.value, audioWorkletRunning: isAudioWorkletRunning.value }
}

onUnmounted(() => clearInterval(diagnosticTimer))

defineExpose({ stopMicrophone, muteMicrophone, getDeviceSnapshot, beginAnswer, completeSubmission, requestSubmit })
</script>

<style scoped>
.voice-answer {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--surface-elevated);
}

.voice-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-height: 52px;
  padding-top: 6px;
  border-top: 1px solid var(--neutral-100);
}

.mic-control {
  --voice-level: 0;
  position: relative;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: 2px solid var(--neutral-300);
  background: var(--neutral-50);
  color: var(--neutral-500);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-normal);
  flex-shrink: 0;
}

.mic-control.open {
  border-color: var(--accent-500);
  background: var(--accent-50);
  color: var(--accent-700);
  box-shadow: 0 0 0 calc(5px + var(--voice-level) * 14px) rgba(16, 185, 129, 0.12);
}

.mic-control.speaking {
  background: var(--accent-600);
  color: white;
}

.mic-control:disabled {
  cursor: wait;
  opacity: 0.6;
}

.mic-status {
  color: var(--neutral-700);
  font-size: var(--text-sm);
  font-weight: 500;
}

.mic-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.voice-only-hint {
  color: var(--neutral-400);
  font-size: 11px;
}

.mic-error {
  padding: 0 var(--space-3);
  color: var(--color-error);
  font-size: var(--text-xs);
}

.recovery-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}

.audio-diagnostics {
  max-height: 210px;
  overflow: auto;
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-sm);
  padding: 6px 8px;
  color: var(--neutral-600);
  font-size: 11px;
}

.audio-diagnostics pre {
  margin-top: 6px;
  white-space: pre-wrap;
  word-break: break-all;
}

.voice-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.btn-ghost {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-sm);
  background: var(--surface-elevated);
  color: var(--neutral-600);
  font-size: var(--text-sm);
}

.btn-send {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-5);
  border: none;
  border-radius: var(--radius-sm);
  background: var(--accent-600);
  color: white;
  font-size: var(--text-sm);
  font-weight: 600;
}

.btn-ghost:disabled,
.btn-send:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

@media (max-width: 640px) {
  .voice-footer {
    align-items: flex-end;
  }
  .voice-only-hint {
    display: none;
  }
}
</style>
