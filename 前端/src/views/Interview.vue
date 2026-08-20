<template>
  <div class="interview-page" :data-conversation-state="currentState">
    <!-- Topbar -->
    <header class="topbar">
      <div class="topbar-left">
        <router-link to="/home" class="back-btn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </router-link>
        <span class="session-tag">{{ jobTitle }} 面试</span>
      </div>
      <div class="topbar-center">
        <div class="timer" :class="{ warning: timeLeft < 300, danger: timeLeft < 60 }">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>{{ formatTime(timeLeft) }}</span>
        </div>
      </div>
      <div class="topbar-right">
        <button class="ctrl-btn" @click="togglePause" :title="isPaused ? '继续' : '暂停'">
          <svg v-if="!isPaused" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
        </button>
        <button class="end-btn" @click="endInterview">结束面试</button>
      </div>
    </header>

    <!-- Progress -->
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
    </div>

    <!-- Body -->
    <div class="interview-body">
      <!-- Digital Human + Conversation Panel -->
      <div class="chat-panel">
        <div class="digital-human-stage">
          <DigitalHumanStage
            ref="digitalHumanRef"
            :text="digitalHumanText"
            :speech-key="digitalHumanSpeechKey"
            :action-state="digitalHumanActionState"
            @connection-ready="handleDigitalHumanReady"
            @media-ready="handleDigitalHumanMediaReady"
            @connection-error="handleDigitalHumanConnectionError"
            @speech-requested="handleDigitalHumanSpeechRequested"
            @speech-accepted="handleDigitalHumanSpeechAccepted"
            @speech-started="handleDigitalHumanSpeechStarted"
            @speech-ended="handleDigitalHumanSpeechEnded"
            @speech-error="handleDigitalHumanSpeechError"
            @speech-interrupted="handleDigitalHumanSpeechInterrupted"
            @action-applied="handleDigitalHumanActionEvent('applied', $event)"
            @action-fallback="handleDigitalHumanActionEvent('fallback', $event)"
            @action-error="handleDigitalHumanActionEvent('error', $event)"
          />
        </div>

        <!-- Scrollable conversation and voice controls -->
        <div class="input-bar">
          <div class="conversation-scroll" ref="messagesRef">
            <div
              v-for="(msg, i) in messages"
              :key="i"
              :class="['conversation-entry', msg.role]"
            >
              <div class="conversation-meta">
                <span>{{ msg.role === 'ai' ? '面试官' : '我的回答' }}</span>
                <span v-if="msg.followup" class="followup-pill">追问</span>
              </div>
              <p>{{ msg.text }}</p>
            </div>

            <div v-if="answer" class="conversation-entry user draft">
              <div class="conversation-meta">
                <span>当前语音回答</span>
                <span class="draft-pill">{{ draftStatusText }}</span>
              </div>
              <p>{{ answer }}</p>
            </div>

            <div v-if="isAiTyping" class="conversation-entry ai typing-entry">
              <div class="conversation-meta"><span>面试官</span></div>
              <p>正在思考下一步问题……</p>
            </div>
          </div>

          <MicrophoneControl
            ref="microphoneRef"
            :session-id="sessionId"
            :question-id="currentQuestionId"
            :question-text="currentQuestionTextForCompleteness"
            :question-type="currentQuestionTypeForCompleteness"
            :transcript="answer"
            :disabled="isSubmitting"
            :audio-gate-state="audioGateState"
            :audio-gate-reason="audioGateReason"
            :conversation-state="currentState"
            :resume-blocked="isCandidateResumeBlocked"
            :active-speech-id="activeSpeechId"
            :barge-in-enabled="bargeInEnabled"
            :interview-active="preflightState === PreflightState.STARTED && Boolean(sessionId)"
            @transcript="appendSpeechTranscript"
            @processing="handleSpeechProcessing"
            @microphone-opened="handleMicrophoneOpened"
            @microphone-muted="handleMicrophoneMuted"
            @microphone-device-started="handleMicrophoneDeviceStarted"
            @submit-requested="handleSubmitRequested"
            @diagnostic="handleAudioDiagnostic"
            @endpointing="handleEndpointing"
            @possible-end="handlePossibleEnd"
            @possible-end-cancelled="handlePossibleEndCancelled"
            @finalization-error="handleFinalizationError"
            @error="handleConversationError"
            @barge-in="handleBargeIn"
            @submit="submitAnswerFn"
            @skip="skipQuestion"
          />
        </div>
      </div>

      <!-- Info Panel -->
      <aside class="info-panel">
        <!-- VR Card -->
        <div class="vr-card">
          <CameraPreview ref="cameraPreviewRef" />
        </div>

        <!-- Question Card -->
        <div class="info-card">
          <div class="q-head">
            <span class="q-num">第 {{ currentQuestion }} 题</span>
            <span class="q-of">/ {{ totalQuestions }}</span>
          </div>
          <div class="q-progress">
            <div class="q-bar" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <div class="q-rows">
            <div class="q-row"><span class="ql">类型</span><span class="qv">{{ questionTypes[currentQuestion - 1] || '技术问题' }}</span></div>
            <div class="q-row"><span class="ql">难度</span><span class="qv">{{ questionDifficulties[currentQuestion - 1] || '中等' }}</span></div>
            <div class="q-row"><span class="ql">考察</span><span class="qv">{{ questionSkills[currentQuestion - 1] || '综合能力' }}</span></div>
          </div>
        </div>

        <!-- Eval Card -->
        <div class="info-card">
          <h3 class="info-card-title">实时评估</h3>
          <div class="eval-list">
            <div v-for="(e, i) in evalItems" :key="i" class="eval-row">
              <span class="eval-label">{{ e.name }}</span>
              <div class="eval-track">
                <div class="eval-fill" :style="{ width: e.value + '%', background: e.color }"></div>
              </div>
              <span class="eval-val">{{ e.value }}%</span>
            </div>
          </div>
          <p class="eval-footnote">面试结束后查看完整报告</p>
        </div>
      </aside>
    </div>

    <div
      v-if="preflightState !== PreflightState.STARTED"
      class="preflight-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="preflight-title"
    >
      <section class="preflight-card">
        <div class="preflight-visual" :class="{ ready: preflightState === PreflightState.READY, error: preflightState === PreflightState.ERROR }">
          <div class="preflight-ring"><span>{{ preflightProgress }}%</span></div>
          <div class="preflight-pulse"></div>
        </div>

        <div class="preflight-copy">
          <p class="preflight-eyebrow">OfferPilot 面试环境</p>
          <h1 id="preflight-title">{{ preflightTitle }}</h1>
          <p>{{ preflightDescription }}</p>
        </div>

        <div class="preflight-checks" aria-live="polite">
          <div v-for="item in preflightItems" :key="item.key" class="preflight-check" :class="{ done: item.done }">
            <span class="preflight-check-icon">{{ item.done ? '✓' : '' }}</span>
            <span>{{ item.label }}</span>
            <small>{{ item.done ? '已就绪' : '准备中' }}</small>
          </div>
        </div>

        <p v-if="preflightError" class="preflight-error">{{ preflightError.message }}</p>
        <button
          v-if="preflightState === PreflightState.READY"
          type="button"
          class="preflight-primary"
          @click="beginInterviewExperience"
        >
          开始面试
        </button>
        <button
          v-else-if="preflightState === PreflightState.ERROR"
          type="button"
          class="preflight-secondary"
          @click="retryPreflight"
        >
          重新准备
        </button>
        <p class="preflight-note">麦克风将在你首次开麦时请求授权，加载期间不会录音。</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { startInterview, submitAnswer, getNextQuestion, finishInterview } from '../api'
import CameraPreview from '../components/interview/CameraPreview.vue'
import DigitalHumanStage from '../components/interview/DigitalHumanStage.vue'
import MicrophoneControl from '../components/interview/MicrophoneControl.vue'
import {
  ConversationState,
  useInterviewConversation,
} from '../composables/useInterviewConversation'
import {
  AudioGateState,
  DEFAULT_PLAYBACK_GUARD_MS,
  canResumeCandidateAudio,
  useInterviewAudioGate,
} from '../composables/useInterviewAudioGate'
import { mapConversationToDigitalHumanAction } from '../composables/digitalHumanActionMapping'
import { PreflightState, useInterviewPreflight } from '../composables/useInterviewPreflight'

const router = useRouter()
const route = useRoute()

// --- Session state ---
const sessionId = ref(null)
const currentQuestionId = ref(null)
const jobTitle = ref('前端开发工程师')
const currentQuestion = ref(1)
const totalQuestions = ref(8)
const timeLeft = ref(1800)
const answer = ref('')
const isPaused = ref(false)
const isSubmitting = ref(false)
const messagesRef = ref(null)
const cameraPreviewRef = ref(null)
const microphoneRef = ref(null)
const digitalHumanRef = ref(null)
const digitalHumanText = ref('')
const digitalHumanSpeechKey = ref(0)
const MAX_QUESTIONS = 8
const playbackGuardMs = Number(import.meta.env.VITE_PLAYBACK_GUARD_MS) || DEFAULT_PLAYBACK_GUARD_MS
const bargeInEnabled = import.meta.env.VITE_BARGE_IN_ENABLED === 'true'
const microphoneAuthorized = ref(false)
const userPausedAnswer = ref(false)
const preparedFirstQuestion = ref('')

const {
  state: preflightState,
  checks: preflightChecks,
  error: preflightError,
  progress: preflightProgress,
  start: startPreflight,
  markReady: markPreflightReady,
  invalidate: invalidatePreflightCheck,
  fail: failPreflight,
  retry: retryPreflightState,
  beginInterview: commitPreflightStart,
  dispose: disposePreflight,
} = useInterviewPreflight({
  timeoutMs: Number(import.meta.env.VITE_INTERVIEW_PREFLIGHT_TIMEOUT_MS) || 60000,
})

const preflightTitle = computed(() => ({
  [PreflightState.LOADING]: '正在准备你的面试',
  [PreflightState.READY]: '面试环境已准备好',
  [PreflightState.ERROR]: '面试环境准备失败',
})[preflightState.value] || '正在准备你的面试')
const preflightDescription = computed(() => ({
  [PreflightState.LOADING]: '正在建立面试会话、启动数字人并等待首个音视频画面。',
  [PreflightState.READY]: '数字人画面和通信链路均已就绪，点击后才会开始计时并播报首题。',
  [PreflightState.ERROR]: '部分服务未能按时准备完成，请确认后端和数字人服务正在运行。',
})[preflightState.value] || '')
const preflightItems = computed(() => [
  { key: 'backend', label: '面试会话与首题', done: preflightChecks.value.backend },
  { key: 'digitalHuman', label: '数字人通信连接', done: preflightChecks.value.digitalHuman },
  { key: 'media', label: '数字人首个音视频画面', done: preflightChecks.value.media },
])

const {
  currentState,
  previousState,
  transitionTo,
  recoverFromError,
  handleSpeechLifecycle,
  activeSpeechId,
} = useInterviewConversation({
  getSessionId: () => sessionId.value,
  getQuestionId: () => currentQuestionId.value,
})

const {
  gateState: audioGateState,
  gateReason: audioGateReason,
  speechId: audioGateSpeechId,
  open: openAudioGate,
  blockInactive: blockAudioGateInactive,
  blockForTransition,
  blockForSpeaking,
  startPlaybackGuard,
  dispose: disposeAudioGate,
} = useInterviewAudioGate({
  playbackGuardMs,
  getSessionId: () => sessionId.value,
  getQuestionId: () => currentQuestionId.value,
  onGuardCompleted: handlePlaybackGuardCompleted,
})

const isAiTyping = computed(() => currentState.value === ConversationState.THINKING)
const digitalHumanActionState = computed(() => mapConversationToDigitalHumanAction({
  conversationState: currentState.value,
  audioGateState: audioGateState.value,
  microphoneAuthorized: microphoneAuthorized.value,
  candidatePaused: userPausedAnswer.value,
}))
const draftStatusText = computed(() => {
  if (currentState.value === ConversationState.TRANSCRIBING) return '识别中'
  if (currentState.value === ConversationState.ENDPOINTING) return '正在切片'
  if (currentState.value === ConversationState.POSSIBLE_END) return '等待继续'
  return '回答中'
})
const isCandidateResumeBlocked = computed(() => !canResumeCandidateAudio({
  conversationState: currentState.value,
  gateState: audioGateState.value,
  speechId: audioGateSpeechId.value,
}))

const questionTypes = ref([])
const questionDifficulties = ref([])
const questionSkills = ref([])

const difficultyLabels = { 1: '简单', 2: '中等', 3: '困难', 4: '困难' }

const messages = ref([])
const currentQuestionTextForCompleteness = computed(() => (
  [...messages.value].reverse().find((message) => message.role === 'ai')?.text || ''
))
const currentQuestionTypeForCompleteness = computed(() => {
  const latestQuestion = [...messages.value].reverse().find((message) => message.role === 'ai')
  if (latestQuestion?.followup) return 'FOLLOWUP'
  return questionTypes.value[currentQuestion.value - 1] || ''
})

const evalItems = ref([
  { name: '表达能力', value: 0, color: '#10b981' },
  { name: '逻辑性', value: 0, color: '#3b82f6' },
  { name: '技术深度', value: 0, color: '#8b5cf6' },
])

const progressPercent = computed(() => (currentQuestion.value / totalQuestions.value) * 100)

let timerInterval = null

// --- Initialize interview on mount ---
onMounted(() => {
  transitionTo(ConversationState.CONNECTING, 'page.mounted')
  startPreflight({ resetChecks: false })
  void prepareInterviewBackend()
})

async function prepareInterviewBackend() {
  // Get jobId from query param, default to 1
  const jobId = Number(route.query.jobId) || 1

  try {
    const res = await startInterview({ jobId })
    sessionId.value = res.sessionId
    jobTitle.value = res.jobName || '模拟面试'

    // Set first question
    if (res.question) {
      currentQuestionId.value = res.question.id
      questionTypes.value.push(mapQuestionType(res.question.type))
      questionDifficulties.value.push(difficultyLabels[res.question.difficulty] || '中等')
      questionSkills.value.push(res.question.abilityTag || '综合能力')
      messages.value.push({
        role: 'ai',
        text: res.question.content,
        followup: res.question.type === 'FOLLOWUP',
      })
      preparedFirstQuestion.value = res.question.content
      markPreflightReady('backend')
    } else {
      throw new Error('后端未返回首道面试题')
    }
  } catch (e) {
    console.error('Failed to start interview:', e)
    failPreflight('backend', e)
  }
}

onUnmounted(() => {
  clearInterval(timerInterval)
  disposePreflight()
  releaseMediaDevices()
})

function startInterviewTimer() {
  if (timerInterval !== null) return
  timerInterval = setInterval(() => {
    if (timeLeft.value > 0 && !isPaused.value) timeLeft.value--
  }, 1000)
}

function beginInterviewExperience() {
  if (!preparedFirstQuestion.value || !commitPreflightStart()) return
  digitalHumanRef.value?.unlockAudio()
  startInterviewTimer()
  transitionTo(ConversationState.WAITING, 'preflight.completed', {
    details: { checks: { ...preflightChecks.value } },
  })
  speakQuestion(preparedFirstQuestion.value)
}

function retryPreflight() {
  retryPreflightState({ resetChecks: false })
  if (!preflightChecks.value.backend) void prepareInterviewBackend()
  if (!preflightChecks.value.digitalHuman || !preflightChecks.value.media) {
    invalidatePreflightCheck('digitalHuman')
    invalidatePreflightCheck('media')
    digitalHumanRef.value?.reload()
  }
}

// --- Helpers ---
function mapQuestionType(type) {
  const map = { MAIN: '主问题', FOLLOWUP: '追问', BEHAVIORAL: '行为面试' }
  return map[type] || '技术问题'
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

// --- Unified conversation state events ---
function handleMicrophoneOpened(metadata = {}) {
  if (isCandidateResumeBlocked.value) {
    console.info('[InterviewAudioGate]', {
      event: 'candidate-resume-blocked',
      state: currentState.value,
      speechId: audioGateSpeechId.value,
      sessionId: sessionId.value,
      questionId: currentQuestionId.value,
    })
    return
  }
  userPausedAnswer.value = false
  openAudioGate('candidate-resumed', metadata)
  if (currentState.value === ConversationState.ERROR) {
    recoverFromError('microphone.recovered', { details: metadata }, ConversationState.LISTENING)
  }
  transitionTo(ConversationState.LISTENING, 'microphone.opened', { details: metadata })
}

function handleMicrophoneMuted(metadata = {}) {
  userPausedAnswer.value = true
  blockAudioGateInactive(metadata.reason || 'manual-pause-answer', metadata)
  if ([ConversationState.ENDPOINTING, ConversationState.TRANSCRIBING, ConversationState.THINKING].includes(currentState.value)) {
    return
  }
  if (currentState.value !== ConversationState.ERROR) {
    transitionTo(ConversationState.WAITING, 'microphone.muted', { details: metadata })
  }
}

function handleMicrophoneDeviceStarted(metadata = {}) {
  microphoneAuthorized.value = true
  console.info('[InterviewAudioGate]', {
    event: 'microphone-device-started',
    sessionId: sessionId.value,
    questionId: currentQuestionId.value,
    ...metadata,
  })
}

function handleSubmitRequested(metadata = {}) {
  userPausedAnswer.value = false
  blockForTransition(null, 'answer-submit-requested', metadata)
}

function handleAudioDiagnostic(metadata = {}) {
  console.info('[InterviewAudioGate]', {
    event: 'blocked-period-rms-summary',
    sessionId: sessionId.value,
    questionId: currentQuestionId.value,
    speechId: audioGateSpeechId.value,
    gateReason: audioGateReason.value,
    ...metadata,
  })
}

function handleEndpointing(metadata = {}) {
  if (currentState.value === ConversationState.ERROR) {
    recoverFromError('audio.retry-started', {}, ConversationState.LISTENING)
  }
  transitionTo(ConversationState.ENDPOINTING, `audio.endpointing.${metadata.reason || 'unknown'}`, {
    details: metadata,
  })

  if (!metadata.willTranscribe) {
    transitionTo(
      metadata.microphoneOpen ? ConversationState.LISTENING : ConversationState.WAITING,
      'audio.endpointing.completed-without-asr',
      { details: metadata },
    )
  }
}

function handlePossibleEnd(metadata = {}) {
  transitionTo(ConversationState.POSSIBLE_END, 'answer.possible-end-entered', { details: metadata })
}

function handlePossibleEndCancelled(metadata = {}) {
  if (currentState.value === ConversationState.POSSIBLE_END) {
    transitionTo(ConversationState.LISTENING, 'answer.possible-end-cancelled', { details: metadata })
  }
}

function handleFinalizationError(metadata = {}) {
  if (microphoneAuthorized.value && !userPausedAnswer.value) {
    openAudioGate('answer-finalization-recoverable', metadata)
  }
  handleConversationError(metadata)
}

function handleSpeechProcessing(payload = {}) {
  if (payload.active) {
    transitionTo(ConversationState.TRANSCRIBING, 'asr.processing.started', {
      details: payload,
    })
    return
  }

  if (payload.failed || currentState.value === ConversationState.ERROR) return
  if (![ConversationState.ENDPOINTING, ConversationState.TRANSCRIBING].includes(currentState.value)) return

  transitionTo(
    payload.microphoneOpen ? ConversationState.LISTENING : ConversationState.WAITING,
    'asr.processing.completed',
    { details: payload },
  )
}

function handleDigitalHumanReady(metadata = {}) {
  if (preflightState.value !== PreflightState.STARTED) {
    markPreflightReady('digitalHuman')
    return
  }
  if (currentState.value === ConversationState.ERROR && previousState.value === ConversationState.CONNECTING) {
    recoverFromError('digital-human.connection-recovered', { details: metadata }, ConversationState.CONNECTING)
  }
  if (currentState.value === ConversationState.CONNECTING && currentQuestionId.value) {
    transitionTo(ConversationState.WAITING, 'digital-human.ready', { details: metadata })
  }
}

function handleDigitalHumanMediaReady(metadata = {}) {
  if (preflightState.value !== PreflightState.STARTED) {
    markPreflightReady('media')
  }
  console.info('[InterviewPreflight]', { event: 'digital-human.media-ready', ...metadata })
}

function handleDigitalHumanConnectionError(metadata = {}) {
  if (preflightState.value !== PreflightState.STARTED) {
    invalidatePreflightCheck('digitalHuman')
    invalidatePreflightCheck('media')
    failPreflight('digital-human', new Error(metadata.error || '数字人连接失败'))
    return
  }
  handleConversationError({ source: 'digital-human', ...metadata })
}

function handleDigitalHumanActionEvent(result, metadata = {}) {
  const writer = result === 'error' ? console.warn : console.info
  writer('[DigitalHumanAction]', {
    result,
    sessionId: sessionId.value,
    questionId: currentQuestionId.value,
    conversationState: currentState.value,
    requestedAction: digitalHumanActionState.value,
    ...metadata,
  })
}

function handleDigitalHumanSpeechRequested(metadata = {}) {
  const result = handleSpeechLifecycle('speech-requested', metadata)
  if (activeSpeechId.value === metadata.speechId && !result.record?.metadata?.duplicate) {
    blockForTransition(metadata.speechId, 'speech-requested', metadata)
  }
}

function handleDigitalHumanSpeechAccepted(metadata = {}) {
  handleSpeechLifecycle('speech-accepted', metadata)
}

function handleDigitalHumanSpeechStarted(metadata = {}) {
  const result = handleSpeechLifecycle('speech-started', metadata)
  if (activeSpeechId.value === metadata.speechId && result.accepted && !result.record?.metadata?.duplicate) {
    blockForSpeaking(metadata.speechId, metadata)
  }
}

function handleDigitalHumanSpeechEnded(metadata = {}) {
  const isCurrentSpeech = activeSpeechId.value === metadata.speechId
  const result = handleSpeechLifecycle('speech-ended', metadata)
  if (isCurrentSpeech && !result.record?.metadata?.duplicate) {
    startPlaybackGuard(metadata.speechId, 'speech-ended', metadata)
  }
}

function handleDigitalHumanSpeechInterrupted(metadata = {}) {
  const isCurrentSpeech = activeSpeechId.value === metadata.speechId
  const result = handleSpeechLifecycle('speech-interrupted', metadata)
  if (isCurrentSpeech && !result.record?.metadata?.duplicate) {
    startPlaybackGuard(metadata.speechId, 'speech-interrupted', metadata)
  }
}

function handleBargeIn(metadata = {}) {
  if (!bargeInEnabled || currentState.value !== ConversationState.SPEAKING) return false
  if (!metadata.speechId || metadata.speechId !== activeSpeechId.value) return false
  if (audioGateState.value !== AudioGateState.BLOCKED_DURING_DIGITAL_HUMAN) return false

  const transition = transitionTo(ConversationState.INTERRUPTING, 'candidate.barge-in-confirmed', {
    details: metadata,
  })
  if (!transition.accepted) return false
  const dispatched = digitalHumanRef.value?.interruptSpeech(metadata.speechId)
  if (dispatched) return true

  handleConversationError({
    source: 'barge-in',
    error: '数字人打断请求未能发送',
    recoverable: true,
  })
  return false
}

function handleDigitalHumanSpeechError(metadata = {}) {
  const isCurrentSpeech = activeSpeechId.value === metadata.speechId
  const result = handleSpeechLifecycle('speech-error', metadata)
  if (isCurrentSpeech && !result.record?.metadata?.duplicate) {
    startPlaybackGuard(metadata.speechId, 'speech-error', metadata)
  }
  if (result.accepted && !result.record?.metadata?.staleEvent && !result.record?.metadata?.duplicate) {
    messages.value.push({ role: 'ai', text: '数字人语音播报失败，请检查连接后重试。', followup: false })
    scrollToBottom()
  }
}

function handlePlaybackGuardCompleted(metadata = {}) {
  if (!microphoneAuthorized.value || userPausedAnswer.value) {
    blockAudioGateInactive(
      userPausedAnswer.value ? 'candidate-paused' : 'microphone-not-authorized',
      metadata,
    )
    return
  }

  microphoneRef.value?.beginAnswer({ sessionId: sessionId.value, questionId: currentQuestionId.value })
  openAudioGate('playback-guard-completed', metadata)
  if (currentState.value === ConversationState.ERROR) {
    transitionTo(ConversationState.LISTENING, 'digital-human.playback-guard-recovered', {
      details: metadata,
    })
  } else if (currentState.value === ConversationState.WAITING) {
    transitionTo(ConversationState.LISTENING, 'digital-human.playback-guard-completed', {
      details: metadata,
    })
  }
}

function handleConversationError({ source = 'conversation', error, recoverable = true } = {}) {
  if (source === 'microphone') {
    microphoneAuthorized.value = false
    blockAudioGateInactive('microphone-device-error', { error })
  }
  transitionTo(ConversationState.ERROR, `${source}.error`, {
    error,
    details: { source, recoverable },
  })
}

// --- Submit answer via API ---
async function submitAnswerFn(finalized = {}) {
  const userAnswer = (finalized.answer || answer.value).trim()
  if (!userAnswer || isSubmitting.value || !sessionId.value) return

  // Push user message
  messages.value.push({ role: 'user', text: userAnswer, followup: false })
  answer.value = ''

  transitionTo(ConversationState.THINKING, 'answer.submitted', {
    details: { answerLength: userAnswer.length },
  })
  isSubmitting.value = true
  scrollToBottom()

  try {
    const res = await submitAnswer(sessionId.value, {
      questionId: finalized.questionId || currentQuestionId.value,
      answer: userAnswer,
      answerId: finalized.answerId,
      submissionId: finalized.submissionId,
    })
    microphoneRef.value?.completeSubmission({ success: true })

    if (res.nextAction === 'FOLLOWUP' && res.followupQuestion) {
      // res.followupQuestion is a plain string, use it directly as text
      // questionId stays the same (followup is to the same main question)
      messages.value.push({
        role: 'ai',
        text: res.followupQuestion,
        followup: true,
      })
      speakQuestion(res.followupQuestion)
    } else if (res.nextAction === 'NEXT') {
      // Fetch the next question from the server
      try {
        const nextRes = await getNextQuestion(sessionId.value)
        if (nextRes.question) {
          currentQuestion.value++
          currentQuestionId.value = nextRes.question.id
          questionTypes.value.push(mapQuestionType(nextRes.question.type))
          questionDifficulties.value.push(difficultyLabels[nextRes.question.difficulty] || '中等')
          questionSkills.value.push(nextRes.question.abilityTag || '综合能力')
          messages.value.push({
            role: 'ai',
            text: nextRes.question.content,
            followup: false,
          })
          speakQuestion(nextRes.question.content)
        }
      } catch (nextErr) {
        console.error('Failed to get next question:', nextErr)
        messages.value.push({
          role: 'ai',
          text: '加载下一题失败，你可以手动结束面试。',
          followup: false,
        })
        handleConversationError({ source: 'next-question', error: nextErr, recoverable: true })
      }

      // Auto-finish when max questions reached
      if (currentQuestion.value >= MAX_QUESTIONS) {
        return await autoFinishInterview()
      }
    } else if (res.nextAction === 'FINISHABLE') {
      // Interview can be finished - call finish
      try {
        const finishRes = await finishInterview(sessionId.value)
        releaseMediaDevices()
        messages.value.push({
          role: 'ai',
          text: '面试结束！感谢你的精彩回答。正在生成你的能力报告...',
          followup: false,
        })
        scrollToBottom()
        const reportId = finishRes || 1
        setTimeout(() => router.push(`/history/${reportId}`), 2000)
        return
      } catch (finishErr) {
        console.error('Failed to finish interview:', finishErr)
        handleConversationError({ source: 'interview-finish', error: finishErr, recoverable: true })
        messages.value.push({
          role: 'ai',
          text: '面试结束但报告生成失败，你可以稍后在面试记录中查看。',
          followup: false,
        })
      }
    }

    // Update eval items if server provides them
    if (res.evalItems && Array.isArray(res.evalItems)) {
      evalItems.value = res.evalItems
    } else {
      // Keep local incremental eval as a fallback
      evalItems.value[0].value = Math.min(100, evalItems.value[0].value + Math.floor(Math.random() * 15 + 5))
      evalItems.value[1].value = Math.min(100, evalItems.value[1].value + Math.floor(Math.random() * 12 + 3))
      evalItems.value[2].value = Math.min(100, evalItems.value[2].value + Math.floor(Math.random() * 10 + 5))
    }
  } catch (e) {
    console.error('Failed to submit answer:', e)
    handleConversationError({ source: 'answer-submission', error: e, recoverable: true })
    messages.value.push({
      role: 'ai',
      text: '提交回答失败，请检查网络后重试。',
      followup: false,
    })
    microphoneRef.value?.completeSubmission({ success: false, error: e?.message })
  } finally {
    isSubmitting.value = false
    scrollToBottom()
  }
}

async function skipQuestion() {
  if (isSubmitting.value || !sessionId.value) return
  if ([ConversationState.ENDPOINTING, ConversationState.TRANSCRIBING].includes(currentState.value)) return
  isSubmitting.value = true
  userPausedAnswer.value = false
  blockForTransition(null, 'question-skip-requested')
  transitionTo(ConversationState.THINKING, 'question.skipped')
  scrollToBottom()

  try {
    const res = await getNextQuestion(sessionId.value)

    if (res.nextAction === 'NEXT' && res.question) {
      currentQuestion.value++
      currentQuestionId.value = res.question.id
      questionTypes.value.push(mapQuestionType(res.question.type))
      questionDifficulties.value.push(difficultyLabels[res.question.difficulty] || '中等')
      questionSkills.value.push(res.question.abilityTag || '综合能力')
      messages.value.push({ role: 'ai', text: res.question.content, followup: false })
      speakQuestion(res.question.content)
    } else if (res.nextAction === 'FOLLOWUP' && res.followupQuestion) {
      const followupText = typeof res.followupQuestion === 'string'
        ? res.followupQuestion
        : res.followupQuestion.content
      if (typeof res.followupQuestion !== 'string' && res.followupQuestion.id) {
        currentQuestionId.value = res.followupQuestion.id
      }
      messages.value.push({ role: 'ai', text: followupText, followup: true })
      speakQuestion(followupText)
    } else if (res.nextAction === 'FINISHED') {
      releaseMediaDevices()
      messages.value.push({
        role: 'ai',
        text: '面试结束！感谢你的精彩回答。正在生成你的能力报告...',
        followup: false,
      })
      const reportId = res || 1
      setTimeout(() => router.push(`/history/${reportId}`), 2000)
    }

    // Auto-finish when max questions reached
    if (currentQuestion.value >= MAX_QUESTIONS) {
      return await autoFinishInterview()
    }
  } catch (e) {
    console.error('Failed to skip question:', e)
    handleConversationError({ source: 'question-skip', error: e, recoverable: true })
    messages.value.push({ role: 'ai', text: '操作失败，请重试。', followup: false })
  } finally {
    isSubmitting.value = false
    scrollToBottom()
  }
}

function appendSpeechTranscript(text) {
  answer.value = text?.trim() || ''
  scrollToBottom()
}

function togglePause() {
  isPaused.value = !isPaused.value
  if (isPaused.value) digitalHumanRef.value?.stop()
}

async function endInterview() {
  releaseMediaDevices()
  if (sessionId.value) {
    try {
      const res = await finishInterview(sessionId.value)
      const reportId = res || 1
      router.push(`/history/${reportId}`)
      return
    } catch (e) {
      console.error('Failed to finish interview:', e)
      handleConversationError({ source: 'interview-finish', error: e, recoverable: true })
    }
  }
  // Fallback navigation
  router.push('/history/1')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  })
}

async function autoFinishInterview() {
  releaseMediaDevices()
  transitionTo(ConversationState.THINKING, 'interview.auto-finish')
  try {
    const finishRes = await finishInterview(sessionId.value)
    messages.value.push({
      role: 'ai',
      text: `已达到 ${MAX_QUESTIONS} 道题目，面试自动结束。正在生成你的能力报告...`,
      followup: false,
    })
    scrollToBottom()
    const reportId = finishRes || 1
    setTimeout(() => router.push(`/history/${reportId}`), 2000)
  } catch (e) {
    console.error('Auto-finish failed:', e)
    messages.value.push({
      role: 'ai',
      text: '面试结束但报告生成失败，你可以稍后在面试记录中查看。',
      followup: false,
    })
    handleConversationError({ source: 'interview-auto-finish', error: e, recoverable: true })
  } finally {
    isSubmitting.value = false
  }
}

function speakQuestion(text) {
  const normalized = text?.trim()
  if (!normalized) return
  digitalHumanText.value = normalized
  digitalHumanSpeechKey.value++
}

function releaseMediaDevices() {
  console.info('[InterviewAudioGate]', {
    event: 'microphone-device-stopped',
    sessionId: sessionId.value,
    questionId: currentQuestionId.value,
    reason: 'interview-ended-or-page-unloaded',
  })
  disposeAudioGate('interview-ended')
  cameraPreviewRef.value?.stopCamera()
  microphoneRef.value?.stopMicrophone()
  digitalHumanRef.value?.close()
}
</script>

<style scoped>
.interview-page {
  height: 100dvh;
  overflow: hidden;
  background: var(--surface-primary);
  display: flex;
  flex-direction: column;
}

.preflight-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 50% 32%, rgba(99, 102, 241, 0.2), transparent 34%),
    rgba(241, 245, 249, 0.92);
  backdrop-filter: blur(14px);
}

.preflight-card {
  width: min(540px, 100%);
  padding: 34px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.16);
  text-align: center;
}

.preflight-visual {
  position: relative;
  width: 108px;
  height: 108px;
  margin: 0 auto 22px;
}

.preflight-ring {
  position: absolute;
  inset: 8px;
  z-index: 2;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: var(--accent-700);
  font-family: var(--font-mono);
  font-weight: 700;
  background: white;
  box-shadow: inset 0 0 0 2px rgba(99, 102, 241, 0.2), 0 12px 32px rgba(99, 102, 241, 0.18);
}

.preflight-pulse {
  position: absolute;
  inset: 0;
  border: 3px solid rgba(99, 102, 241, 0.4);
  border-top-color: var(--accent-600);
  border-radius: 50%;
  animation: preflight-spin 1.1s linear infinite;
}

.preflight-visual.ready .preflight-pulse {
  border-color: rgba(16, 185, 129, 0.45);
  animation: preflight-breathe 1.8s ease-in-out infinite;
}

.preflight-visual.error .preflight-pulse {
  border-color: rgba(239, 68, 68, 0.45);
  animation: none;
}

.preflight-eyebrow {
  margin: 0 0 8px;
  color: var(--accent-600);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.preflight-copy h1 {
  margin: 0;
  color: var(--neutral-900);
  font-size: 26px;
}

.preflight-copy > p:last-child {
  margin: 10px auto 0;
  max-width: 430px;
  color: var(--neutral-500);
  font-size: 14px;
  line-height: 1.7;
}

.preflight-checks {
  display: grid;
  gap: 10px;
  margin: 24px 0;
  text-align: left;
}

.preflight-check {
  display: grid;
  grid-template-columns: 24px 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
  color: var(--neutral-600);
  background: var(--neutral-50);
}

.preflight-check.done { color: var(--neutral-800); }
.preflight-check small { color: var(--neutral-400); }
.preflight-check.done small { color: #059669; }

.preflight-check-icon {
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border: 2px solid var(--neutral-300);
  border-radius: 50%;
  color: white;
  font-size: 12px;
}

.preflight-check.done .preflight-check-icon {
  border-color: #10b981;
  background: #10b981;
}

.preflight-error {
  margin: -8px 0 18px;
  padding: 10px 12px;
  border-radius: 10px;
  color: #b91c1c;
  background: #fef2f2;
  font-size: 13px;
}

.preflight-primary,
.preflight-secondary {
  width: 100%;
  padding: 13px 18px;
  border: 0;
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  box-shadow: 0 12px 28px rgba(99, 102, 241, 0.24);
}

.preflight-secondary { background: var(--neutral-800); }

.preflight-note {
  margin: 14px 0 0;
  color: var(--neutral-400);
  font-size: 12px;
}

@keyframes preflight-spin { to { transform: rotate(360deg); } }
@keyframes preflight-breathe { 50% { transform: scale(1.08); opacity: 0.6; } }

/* Topbar */
.topbar {
  height: 56px;
  background: var(--surface-elevated);
  border-bottom: 1px solid var(--neutral-200);
  padding: 0 var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
}
.topbar-left, .topbar-right { display: flex; align-items: center; gap: var(--space-3); }
.topbar-center { display: flex; align-items: center; }
.back-btn { color: var(--neutral-500); padding: var(--space-2); border-radius: var(--radius-sm); display: flex; transition: all var(--duration-fast); }
.back-btn:hover { color: var(--neutral-700); background: var(--neutral-100); }
.session-tag { font-size: var(--text-sm); font-weight: 600; color: var(--neutral-700); padding: var(--space-1) var(--space-3); background: var(--neutral-100); border-radius: var(--radius-full); }
.timer { display: flex; align-items: center; gap: var(--space-2); font-family: var(--font-mono); font-size: var(--text-lg); font-weight: 600; color: var(--accent-600); }
.timer.warning { color: var(--color-warning); }
.timer.danger { color: var(--color-error); }
.ctrl-btn { width: 36px; height: 36px; border-radius: var(--radius-sm); border: 1px solid var(--neutral-200); background: var(--surface-elevated); color: var(--neutral-600); display: flex; align-items: center; justify-content: center; transition: all var(--duration-fast); }
.ctrl-btn:hover { border-color: var(--neutral-300); background: var(--neutral-50); }
.end-btn { padding: var(--space-2) var(--space-4); border: 1px solid rgba(239,68,68,0.3); border-radius: var(--radius-sm); background: rgba(239,68,68,0.05); color: var(--color-error); font-size: var(--text-sm); font-weight: 500; transition: all var(--duration-fast); }
.end-btn:hover { background: rgba(239,68,68,0.1); }

/* Progress */
.progress-track { position: fixed; top: 56px; left: 0; right: 0; height: 3px; background: var(--neutral-200); z-index: 49; }
.progress-fill { height: 100%; background: var(--accent-500); transition: width 0.5s var(--ease-out-expo); }

/* Body */
.interview-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 320px;
  margin-top: 59px;
  height: calc(100dvh - 59px);
  overflow: hidden;
}

/* Digital Human + Conversation Panel */
.chat-panel {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

.digital-human-stage {
  flex: 1;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 10px 14px 0;
  background:
    radial-gradient(circle at 50% 45%, rgba(59, 130, 246, 0.08), transparent 42%),
    linear-gradient(180deg, var(--surface-primary), var(--neutral-50));
}

/* Scrollable conversation and bottom controls */
.input-bar {
  height: clamp(220px, 27vh, 280px);
  border-top: 1px solid var(--neutral-200);
  background: var(--surface-elevated);
  padding: var(--space-3) var(--space-5);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.conversation-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 2px var(--space-2) var(--space-2);
  scroll-behavior: smooth;
  scrollbar-gutter: stable;
}

.conversation-entry {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--neutral-100);
}

.conversation-entry:last-child {
  border-bottom: none;
}

.conversation-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: 4px;
  color: var(--neutral-500);
  font-size: 11px;
  font-weight: 600;
}

.conversation-entry.ai .conversation-meta {
  color: var(--accent-700);
}

.conversation-entry.user .conversation-meta {
  color: #2563eb;
}

.conversation-entry p {
  color: var(--neutral-800);
  font-size: var(--text-sm);
  line-height: 1.65;
  white-space: pre-wrap;
}

.conversation-entry.draft {
  background: rgba(59, 130, 246, 0.035);
}

.followup-pill,
.draft-pill {
  padding: 1px 7px;
  border-radius: var(--radius-full);
  background: var(--accent-50);
  color: var(--accent-700);
  font-size: 10px;
}

.draft-pill {
  background: rgba(59, 130, 246, 0.08);
  color: #2563eb;
}

.typing-entry p {
  color: var(--neutral-400);
}

/* Info Panel — independent scrolling column */
.info-panel {
  width: auto;
  flex-shrink: 0;
  height: 100%;
  overflow-y: auto;
  background: var(--surface-elevated);
  border-left: 1px solid var(--neutral-200);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  scroll-behavior: smooth;
}
.vr-card { aspect-ratio: 16/9; background: var(--neutral-100); border-radius: var(--radius-lg); border: 1px solid var(--neutral-200); display: flex; align-items: center; justify-content: center; flex-shrink: 0; position: sticky; top: 0; z-index: 5; overflow: hidden; }
.info-card { background: var(--neutral-50); border-radius: var(--radius-lg); padding: var(--space-4); flex-shrink: 0; }
.info-card-title { font-size: var(--text-sm); font-weight: 600; color: var(--neutral-700); margin-bottom: var(--space-3); }
.q-head { display: flex; align-items: baseline; gap: var(--space-1); margin-bottom: var(--space-3); }
.q-num { font-family: var(--font-mono); font-size: var(--text-lg); font-weight: 700; color: var(--accent-600); }
.q-of { font-size: var(--text-sm); color: var(--neutral-500); }
.q-progress { height: 4px; background: var(--neutral-200); border-radius: 2px; margin-bottom: var(--space-3); overflow: hidden; }
.q-bar { height: 100%; background: var(--accent-500); border-radius: 2px; transition: width 0.5s var(--ease-out-expo); }
.q-rows { display: flex; flex-direction: column; gap: var(--space-2); }
.q-row { display: flex; justify-content: space-between; }
.ql { font-size: var(--text-sm); color: var(--neutral-500); }
.qv { font-size: var(--text-sm); font-weight: 500; color: var(--neutral-700); }
.eval-list { display: flex; flex-direction: column; gap: var(--space-3); }
.eval-row { display: flex; align-items: center; gap: var(--space-3); }
.eval-label { width: 60px; font-size: var(--text-xs); color: var(--neutral-600); flex-shrink: 0; }
.eval-track { flex: 1; height: 6px; background: var(--neutral-200); border-radius: 3px; overflow: hidden; }
.eval-fill { height: 100%; border-radius: 3px; transition: width 0.8s var(--ease-out-expo); }
.eval-val { width: 34px; text-align: right; font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: var(--neutral-600); }
.eval-footnote { font-size: var(--text-xs); color: var(--neutral-400); text-align: center; margin-top: var(--space-3); }

/* Responsive */
@media (max-width: 1024px) {
  .interview-body {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
    overflow-y: auto;
  }
  .chat-panel { height: 68vh; min-height: 620px; }
  .digital-human-stage { min-height: 360px; }
  .info-panel {
    height: auto;
    max-height: none;
    border-left: none;
    border-top: 1px solid var(--neutral-200);
    flex-direction: row;
    flex-wrap: wrap;
    gap: var(--space-3);
    overflow-y: visible;
  }
  .vr-card { width: 200px; }
  .info-card { flex: 1; min-width: 200px; }
}
@media (prefers-reduced-motion: reduce) {
  .conversation-scroll { scroll-behavior: auto; }
  .preflight-pulse { animation: none; }
}
</style>
