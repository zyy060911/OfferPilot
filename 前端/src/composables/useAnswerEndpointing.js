export function useAnswerEndpointing({
  timing,
  now = () => performance.now(),
  isEligible = () => true,
  onPossibleEnd = () => {},
  onPossibleEndCancelled = () => {},
  onConfirmed = () => {},
  evaluateConfirmation = () => null,
  logger = console,
} = {}) {
  let finishTimer = null
  let confirmTimer = null
  let context = null
  let possible = false
  let finishDeadline = null
  let confirmDeadline = null
  let disposed = false
  let lastCompleteness = null

  function clearTimers() {
    clearTimeout(finishTimer)
    clearTimeout(confirmTimer)
    finishTimer = null
    confirmTimer = null
    finishDeadline = null
    confirmDeadline = null
  }

  function speechStarted(nextContext) {
    if (disposed || !isEligible(nextContext)) return false
    const wasPossible = possible
    clearTimers()
    context = nextContext
    possible = false
    lastCompleteness = null
    if (wasPossible) {
      logger.info?.('[AnswerEndpointing]', { event: 'possible-end-cancelled', ...nextContext })
      onPossibleEndCancelled(nextContext)
    }
    return true
  }

  function speechEnded(nextContext) {
    if (disposed || !isEligible(nextContext)) return false
    clearTimers()
    context = nextContext
    possible = false
    lastCompleteness = null
    const elapsed = Math.max(0, now() - nextContext.endedAt)
    const remaining = Math.max(0, timing.answerFinishMs - elapsed)
    finishDeadline = now() + remaining
    finishTimer = setTimeout(() => enterPossibleEnd(nextContext), remaining)
    return true
  }

  function enterPossibleEnd(expected) {
    finishTimer = null
    finishDeadline = null
    if (disposed || context !== expected || !isEligible(expected)) return
    possible = true
    lastCompleteness = resolveConfirmation(expected)
    const confirmMs = lastCompleteness.recommendedConfirmMs
    const metadata = { ...expected, completeness: lastCompleteness }
    logger.info?.('[AnswerEndpointing]', { event: 'possible-end-entered', confirmMs, ...metadata })
    onPossibleEnd(metadata)
    confirmDeadline = now() + confirmMs
    confirmTimer = setTimeout(() => confirm(expected), confirmMs)
  }

  function confirm(expected) {
    confirmTimer = null
    confirmDeadline = null
    if (disposed || context !== expected || !possible || !isEligible(expected)) return
    possible = false
    onConfirmed({ ...expected, completeness: lastCompleteness })
  }

  function resolveConfirmation(expected) {
    const fallback = {
      score: 0.5,
      classification: 'FALLBACK',
      signals: [],
      recommendedConfirmMs: timing.answerConfirmMs,
      reason: 'fixed-policy-fallback',
    }
    try {
      const evaluated = evaluateConfirmation(expected)
      if (!evaluated || typeof evaluated !== 'object') return fallback
      const requested = Number(evaluated.recommendedConfirmMs)
      if (!Number.isFinite(requested) || requested <= 0) return fallback
      return {
        ...evaluated,
        // Semantic rules may extend the confirmation period, never shorten the natural pause.
        recommendedConfirmMs: Math.min(5000, Math.max(timing.answerConfirmMs, requested)),
      }
    } catch (error) {
      logger.warn?.('[AnswerEndpointing] completeness evaluation failed; fixed timing retained', {
        error: error?.message || String(error),
        answerId: expected?.answerId,
      })
      return { ...fallback, reason: 'rule-evaluation-error' }
    }
  }

  function cancel(reason = 'cancelled') {
    const wasPossible = possible
    clearTimers()
    possible = false
    context = null
    lastCompleteness = null
    if (wasPossible) onPossibleEndCancelled({ reason })
  }

  function dispose() {
    disposed = true
    cancel('disposed')
  }

  function getSnapshot() {
    const currentTime = now()
    return {
      possibleEnd: possible,
      silenceSinceReliableSpeechMs: context?.endedAt == null ? 0 : Math.max(0, currentTime - context.endedAt),
      answerFinishRemainingMs: finishDeadline == null ? null : Math.max(0, finishDeadline - currentTime),
      possibleEndConfirmRemainingMs: confirmDeadline == null ? null : Math.max(0, confirmDeadline - currentTime),
      completenessScore: lastCompleteness?.score ?? null,
      completenessClassification: lastCompleteness?.classification ?? null,
      completenessRecommendedConfirmMs: lastCompleteness?.recommendedConfirmMs ?? null,
      completenessReason: lastCompleteness?.reason ?? null,
      completenessSignals: lastCompleteness?.signals ?? [],
      completenessEnumerationProgress: lastCompleteness?.enumerationProgress ?? null,
    }
  }

  return { speechStarted, speechEnded, cancel, dispose, isPossibleEnd: () => possible, getSnapshot }
}
