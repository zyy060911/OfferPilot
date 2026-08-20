export const DIGITAL_HUMAN_PROTOCOL_VERSION = 1

export function createSpeechId(cryptoApi = globalThis.crypto) {
  if (typeof cryptoApi?.randomUUID === 'function') return cryptoApi.randomUUID()
  return `speech-${Date.now()}-${Math.random().toString(36).slice(2)}`
}

export function isTrustedEmbedMessage(event, frameWindow, allowedOrigins) {
  if (!event || event.source !== frameWindow) return false
  return allowedOrigins.includes(event.origin)
}

export function isSpeechLifecycleMessage(data) {
  return Boolean(
    data
    && data.version === DIGITAL_HUMAN_PROTOCOL_VERSION
    && typeof data.speechId === 'string'
    && data.speechId
    && [
      'offerpilot.embed.speech.accepted',
      'offerpilot.embed.speech.started',
      'offerpilot.embed.speech.ended',
      'offerpilot.embed.speech.error',
      'offerpilot.embed.speech.interrupted',
    ].includes(data.type),
  )
}

export function isDigitalHumanActionMessage(data) {
  return Boolean(
    data
    && data.version === DIGITAL_HUMAN_PROTOCOL_VERSION
    && typeof data.requestId === 'string'
    && data.requestId
    && typeof data.requestedAction === 'string'
    && [
      'offerpilot.embed.action.applied',
      'offerpilot.embed.action.fallback',
      'offerpilot.embed.action.error',
    ].includes(data.type),
  )
}

export function isCurrentDigitalHumanActionMessage(data, activeRequestId) {
  return Boolean(activeRequestId && isDigitalHumanActionMessage(data) && data.requestId === activeRequestId)
}

export function createSpeechWatchdog({ timeoutMs, onTimeout, setTimer = setTimeout, clearTimer = clearTimeout }) {
  let timer = null

  function stop() {
    if (timer !== null) clearTimer(timer)
    timer = null
  }

  return {
    start(speechId) {
      stop()
      timer = setTimer(() => {
        timer = null
        onTimeout(speechId)
      }, timeoutMs)
    },
    stop,
    dispose: stop,
  }
}
