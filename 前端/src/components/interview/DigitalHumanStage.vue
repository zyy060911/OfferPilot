<template>
  <div class="digital-human" :data-action-state="actionState">
    <iframe
      ref="frameRef"
      class="digital-human-frame"
      :src="embedUrl"
      title="AI 数字人面试官"
      allow="autoplay; fullscreen"
      @load="handleFrameLoad"
    />

    <div class="connection-status" :class="connectionState">
      <span class="status-dot"></span>
      {{ statusText }}
    </div>

    <button
      v-if="connectionState === 'error'"
      type="button"
      class="retry-button"
      @click="reload"
    >
      重新连接
    </button>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import {
  DIGITAL_HUMAN_PROTOCOL_VERSION,
  createSpeechWatchdog,
  createSpeechId,
  isSpeechLifecycleMessage,
  isDigitalHumanActionMessage,
  isCurrentDigitalHumanActionMessage,
  isTrustedEmbedMessage,
} from '../../utils/digitalHumanMessaging'
import { DigitalHumanActionState, isDigitalHumanActionState } from '../../composables/digitalHumanActionMapping'

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  speechKey: {
    type: Number,
    default: 0,
  },
  actionState: {
    type: String,
    default: DigitalHumanActionState.NEUTRAL,
  },
})

const emit = defineEmits([
  'connection-ready',
  'media-ready',
  'connection-error',
  'speech-requested',
  'speech-accepted',
  'speech-started',
  'speech-ended',
  'speech-error',
  'speech-interrupted',
  'action-applied',
  'action-fallback',
  'action-error',
])

const embedBaseUrl = import.meta.env.VITE_DIGITAL_HUMAN_EMBED_URL
  || '/digital-human/offerpilot-embed.html'
const embedUrl = withLayoutVersion(embedBaseUrl)

const frameRef = ref(null)
const connectionState = ref('connecting')
const pendingSpeech = ref(null)
const activeSpeechId = ref(null)
const pendingAction = ref(null)
const activeActionRequestId = ref(null)
let actionSequence = 0
let connectionTimer = null
let interruptTimer = null
const speechWatchdogMs = Number(import.meta.env.VITE_DIGITAL_HUMAN_SPEECH_WATCHDOG_MS) || 120000
const speechWatchdog = createSpeechWatchdog({
  timeoutMs: speechWatchdogMs,
  onTimeout: (speechId) => {
    if (activeSpeechId.value === speechId) activeSpeechId.value = null
    clearTimeout(interruptTimer)
    interruptTimer = null
    emit('speech-error', {
      speechId,
      event: 'speech-error',
      timestamp: new Date().toISOString(),
      error: '数字人播报已开始，但服务端长期未报告最后音频帧输出',
      watchdog: true,
    })
  },
})

const statusText = computed(() => ({
  connecting: '数字人连接中',
  ready: '数字人已连接',
  error: '数字人连接失败',
})[connectionState.value] || '数字人连接中')

function postToFrame(message) {
  const targetWindow = frameRef.value?.contentWindow
  if (!targetWindow) return false

  targetWindow.postMessage(message, resolveTargetOrigin())
  return true
}

function resolveTargetOrigin() {
  try {
    return new URL(embedUrl, window.location.href).origin
  } catch {
    return window.location.origin
  }
}

function withLayoutVersion(url) {
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}offerpilotLayout=4&parentOrigin=${encodeURIComponent(window.location.origin)}`
}

function setAction(action) {
  pendingAction.value = {
    action: isDigitalHumanActionState(action) ? action : DigitalHumanActionState.ERROR,
    requestId: `action-${Date.now()}-${++actionSequence}`,
  }
  return dispatchPendingAction()
}

function dispatchPendingAction() {
  if (connectionState.value !== 'ready' || !pendingAction.value) return false
  const request = pendingAction.value
  if (!postToFrame({
    type: 'offerpilot.action.set',
    version: DIGITAL_HUMAN_PROTOCOL_VERSION,
    ...request,
  })) return false
  activeActionRequestId.value = request.requestId
  pendingAction.value = null
  return true
}

function speak(text, key = '') {
  const normalized = text?.trim()
  if (!normalized) return

  pendingSpeech.value = { text: normalized, key, speechId: createSpeechId() }
  dispatchPendingSpeech()
}

function dispatchPendingSpeech() {
  if (connectionState.value !== 'ready' || !pendingSpeech.value) return false

  const speech = pendingSpeech.value
  if (!postToFrame({ type: 'offerpilot.speak', version: DIGITAL_HUMAN_PROTOCOL_VERSION, ...speech })) return false
  pendingSpeech.value = null
  speechWatchdog.stop()
  activeSpeechId.value = speech.speechId
  emit('speech-requested', { ...speech, event: 'speech-requested', timestamp: new Date().toISOString() })
  return true
}

function stop() {
  postToFrame({ type: 'offerpilot.stop' })
  if (connectionState.value !== 'error') connectionState.value = 'ready'
}

function interruptSpeech(expectedSpeechId) {
  if (!expectedSpeechId || expectedSpeechId !== activeSpeechId.value) return false
  const dispatched = postToFrame({
    type: 'offerpilot.speech.interrupt',
    version: DIGITAL_HUMAN_PROTOCOL_VERSION,
    speechId: expectedSpeechId,
  })
  if (!dispatched) return false
  clearTimeout(interruptTimer)
  interruptTimer = setTimeout(() => {
    if (activeSpeechId.value !== expectedSpeechId) return
    interruptTimer = null
    activeSpeechId.value = null
    speechWatchdog.stop()
    emit('speech-error', {
      speechId: expectedSpeechId,
      event: 'speech-error',
      timestamp: new Date().toISOString(),
      error: '数字人已收到打断请求，但未在期限内确认停止输出',
      recoverable: true,
      interruptWatchdog: true,
    })
  }, 8000)
  return true
}

function close() {
  postToFrame({ type: 'offerpilot.close' })
  pendingSpeech.value = null
  activeSpeechId.value = null
  pendingAction.value = null
  activeActionRequestId.value = null
  speechWatchdog.stop()
  clearTimeout(interruptTimer)
  interruptTimer = null
}

function unlockAudio() {
  postToFrame({ type: 'offerpilot.unlockAudio' })
}

function handleFrameLoad() {
  clearTimeout(interruptTimer)
  interruptTimer = null
  if (activeSpeechId.value) {
    emit('speech-error', {
      speechId: activeSpeechId.value,
      event: 'speech-error',
      timestamp: new Date().toISOString(),
      error: '数字人嵌入页在播报期间重新加载',
      recoverable: true,
    })
    activeSpeechId.value = null
    speechWatchdog.stop()
  }
  pendingAction.value = {
    action: isDigitalHumanActionState(props.actionState) ? props.actionState : DigitalHumanActionState.ERROR,
    requestId: `action-${Date.now()}-${++actionSequence}`,
  }
  applyEmbeddedLayout()
  connectionState.value = 'connecting'
  startConnectionTimeout()
}

function applyEmbeddedLayout() {
  try {
    const document = frameRef.value?.contentDocument
    if (!document?.head) return

    let style = document.getElementById('offerpilot-layout-override')
    if (!style) {
      style = document.createElement('style')
      style.id = 'offerpilot-layout-override'
      document.head.appendChild(style)
    }
    style.textContent = `
      .stage {
        border-radius: 18px !important;
        background:
          radial-gradient(circle at 50% 42%, rgba(255,255,255,.96),
          rgba(225,234,247,.86) 58%, rgba(205,218,237,.9)) !important;
      }
      video {
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important;
        object-position: center center !important;
      }
      .status { display: none !important; }
      .connect[disabled] { display: none !important; }
    `
  } catch {
    // 跨域部署时无法访问 iframe 文档，改由数字人嵌入页自身样式控制。
  }
}

function reload() {
  connectionState.value = 'connecting'
  startConnectionTimeout()
  const frame = frameRef.value
  if (!frame) return

  try {
    frame.src = withLayoutVersion(`${embedBaseUrl}${embedBaseUrl.includes('?') ? '&' : '?'}reload=${Date.now()}`)
  } catch {
    frame.src = embedUrl
  }
}

function handleMessage(event) {
  if (!isTrustedEmbedMessage(event, frameRef.value?.contentWindow, [resolveTargetOrigin()])) return

  const data = event.data || {}
  if (data.type === 'offerpilot.embed.ready') {
    clearTimeout(connectionTimer)
    connectionState.value = 'ready'
    emit('connection-ready', { sessionId: data.sessionId || null })
    unlockAudio()
    dispatchPendingAction()
    dispatchPendingSpeech()
  } else if (data.type === 'offerpilot.embed.media.ready') {
    emit('media-ready', {
      sessionId: data.sessionId || null,
      timestamp: data.timestamp || new Date().toISOString(),
      audioTrackReady: Boolean(data.audioTrackReady),
      videoFrameReady: Boolean(data.videoFrameReady),
    })
  } else if (data.type === 'offerpilot.embed.disconnected') {
    clearTimeout(connectionTimer)
    clearTimeout(interruptTimer)
    interruptTimer = null
    connectionState.value = 'error'
    if (activeSpeechId.value) {
      emit('speech-error', {
        speechId: activeSpeechId.value,
        event: 'speech-error',
        timestamp: new Date().toISOString(),
        error: '数字人 WebRTC 连接已断开',
        recoverable: true,
      })
      activeSpeechId.value = null
      speechWatchdog.stop()
    }
    emit('connection-error', { error: '数字人连接已断开', recoverable: true })
  } else if (isDigitalHumanActionMessage(data)) {
    if (!isCurrentDigitalHumanActionMessage(data, activeActionRequestId.value)) return
    activeActionRequestId.value = null
    emit(`action-${data.type.split('.').at(-1)}`, data)
  } else if (isSpeechLifecycleMessage(data)) {
    const eventName = data.type.split('.').at(-1)
    emit(`speech-${eventName}`, data)
    if (data.speechId !== activeSpeechId.value) return
    if (eventName === 'started') {
      speechWatchdog.start(data.speechId)
    } else if (['ended', 'error', 'interrupted'].includes(eventName)) {
      speechWatchdog.stop()
      clearTimeout(interruptTimer)
      interruptTimer = null
      activeSpeechId.value = null
    }
  }
}

function startConnectionTimeout() {
  clearTimeout(connectionTimer)
  connectionTimer = setTimeout(() => {
    if (connectionState.value === 'connecting') {
      connectionState.value = 'error'
      emit('connection-error', { error: '数字人连接超时', recoverable: true })
    }
  }, 20000)
}

watch(
  () => [props.text, props.speechKey],
  ([text, key]) => speak(text, key),
  { immediate: true },
)

watch(
  () => props.actionState,
  (action) => setAction(action),
  { immediate: true },
)

window.addEventListener('message', handleMessage)

onBeforeUnmount(() => {
  clearTimeout(connectionTimer)
  clearTimeout(interruptTimer)
  speechWatchdog.dispose()
  close()
  window.removeEventListener('message', handleMessage)
})

defineExpose({
  speak,
  stop,
  close,
  unlockAudio,
  reload,
  setAction,
  interruptSpeech,
})
</script>

<style scoped>
.digital-human {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 18px;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
  background: #e3ebf6;
}

.digital-human-frame {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #e3ebf6;
}

.connection-status {
  position: absolute;
  top: 14px;
  left: 14px;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.84);
  background: rgba(5, 12, 24, 0.58);
  backdrop-filter: blur(10px);
  font-size: 11px;
  pointer-events: none;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.14);
}

.connection-status.ready .status-dot {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.connection-status.error .status-dot {
  background: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.retry-button {
  position: absolute;
  left: 50%;
  bottom: 24px;
  transform: translateX(-50%);
  padding: 8px 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  background: rgba(15, 23, 42, 0.82);
}
</style>
