import { computed, ref } from 'vue'

export const PreflightState = Object.freeze({
  LOADING: 'LOADING',
  READY: 'READY',
  STARTED: 'STARTED',
  ERROR: 'ERROR',
})

export const PREFLIGHT_CHECKS = Object.freeze(['backend', 'digitalHuman', 'media'])

export function useInterviewPreflight({ timeoutMs = 60000 } = {}) {
  const state = ref(PreflightState.LOADING)
  const checks = ref(createChecks())
  const error = ref(null)
  let timeoutId = null

  const completedCount = computed(() => (
    PREFLIGHT_CHECKS.filter((check) => checks.value[check]).length
  ))
  const progress = computed(() => Math.round((completedCount.value / PREFLIGHT_CHECKS.length) * 100))
  const isReady = computed(() => state.value === PreflightState.READY)

  function start({ resetChecks = true } = {}) {
    clearTimer()
    if (resetChecks) checks.value = createChecks()
    error.value = null
    state.value = PreflightState.LOADING
    timeoutId = setTimeout(() => {
      if (state.value !== PreflightState.LOADING) return
      fail('timeout', new Error('面试环境准备超时，请检查后端和数字人服务'))
    }, timeoutMs)
  }

  function markReady(check) {
    if (!PREFLIGHT_CHECKS.includes(check) || state.value === PreflightState.STARTED) return false
    checks.value = { ...checks.value, [check]: true }
    if (PREFLIGHT_CHECKS.every((name) => checks.value[name])) {
      clearTimer()
      error.value = null
      state.value = PreflightState.READY
    }
    return true
  }

  function fail(source, cause) {
    if (state.value === PreflightState.STARTED) return false
    clearTimer()
    error.value = {
      source,
      message: cause?.message || String(cause || '准备面试环境失败'),
      timestamp: new Date().toISOString(),
    }
    state.value = PreflightState.ERROR
    return true
  }

  function invalidate(check) {
    if (!PREFLIGHT_CHECKS.includes(check) || state.value === PreflightState.STARTED) return false
    checks.value = { ...checks.value, [check]: false }
    return true
  }

  function retry({ resetChecks = false } = {}) {
    start({ resetChecks })
  }

  function beginInterview() {
    if (state.value !== PreflightState.READY) return false
    clearTimer()
    state.value = PreflightState.STARTED
    return true
  }

  function dispose() {
    clearTimer()
  }

  function clearTimer() {
    if (timeoutId !== null) clearTimeout(timeoutId)
    timeoutId = null
  }

  return {
    state,
    checks,
    error,
    completedCount,
    progress,
    isReady,
    start,
    markReady,
    invalidate,
    fail,
    retry,
    beginInterview,
    dispose,
  }
}

function createChecks() {
  return {
    backend: false,
    digitalHuman: false,
    media: false,
  }
}
