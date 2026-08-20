const DEFAULTS = Object.freeze({
  segmentSilenceMs: 3000,
  answerFinishMs: 7000,
  answerConfirmMs: 800,
  maxSegmentMs: 28000,
  asrFinalizationTimeoutMs: 15000,
})

function positiveNumber(value, fallback, name, logger) {
  const parsed = Number(value)
  if (Number.isFinite(parsed) && parsed > 0) return parsed
  if (value !== undefined && value !== null && value !== '') {
    logger.warn?.(`[InterviewAudioTiming] ${name} 非法，已回退到 ${fallback}ms`)
  }
  return fallback
}

export function resolveInterviewAudioTiming(env = import.meta.env || {}, logger = console) {
  const timing = {
    segmentSilenceMs: positiveNumber(env.VITE_SEGMENT_SILENCE_MS, DEFAULTS.segmentSilenceMs, 'VITE_SEGMENT_SILENCE_MS', logger),
    answerFinishMs: positiveNumber(env.VITE_ANSWER_FINISH_MS, DEFAULTS.answerFinishMs, 'VITE_ANSWER_FINISH_MS', logger),
    answerConfirmMs: positiveNumber(env.VITE_ANSWER_CONFIRM_MS, DEFAULTS.answerConfirmMs, 'VITE_ANSWER_CONFIRM_MS', logger),
    maxSegmentMs: positiveNumber(env.VITE_MAX_ASR_SEGMENT_MS, DEFAULTS.maxSegmentMs, 'VITE_MAX_ASR_SEGMENT_MS', logger),
    asrFinalizationTimeoutMs: positiveNumber(env.VITE_ASR_FINALIZATION_TIMEOUT_MS, DEFAULTS.asrFinalizationTimeoutMs, 'VITE_ASR_FINALIZATION_TIMEOUT_MS', logger),
  }
  if (timing.answerFinishMs <= timing.segmentSilenceMs) {
    logger.warn?.('[InterviewAudioTiming] 回答结束阈值必须大于切片静音阈值，已使用安全默认值')
    timing.answerFinishMs = DEFAULTS.answerFinishMs
    if (timing.answerFinishMs <= timing.segmentSilenceMs) {
      timing.answerFinishMs = timing.segmentSilenceMs + DEFAULTS.answerConfirmMs
    }
  }
  return Object.freeze(timing)
}

export const DEFAULT_INTERVIEW_AUDIO_TIMING = DEFAULTS
