export const AnswerCompletenessClassification = Object.freeze({
  COMPLETE: 'COMPLETE',
  UNCERTAIN: 'UNCERTAIN',
  INCOMPLETE: 'INCOMPLETE',
  FALLBACK: 'FALLBACK',
})

export const DEFAULT_COMPLETENESS_CONFIRM_MS = 800

const UNCERTAIN_CONFIRM_MS = 1200
const INCOMPLETE_CONFIRM_MS = 2000
const PENDING_ASR_CONFIRM_MS = 1600

const EXPLICIT_ENDINGS = [
  /(?:以上|大概|基本)(?:就是|是)?(?:这些|这样)[。.!！]?$/u,
  /(?:我的回答|回答)(?:完毕|结束)[。.!！]?$/u,
  /(?:就这些|差不多了)[。.!！]?$/u,
]

const DANGLING_ENDINGS = [
  /(?:首先|其次|再次|然后|接着|最后|另外|还有|以及|并且|但是|不过)$/u,
  /(?:因为|所以|比如|例如|包括|分别是|主要有|具体来说|也就是说)$/u,
  /(?:一方面|另一方面|第一|第二|第三|第四|第\d+)[、，,:：]?$/u,
  /[、，,:：;；（(]$/u,
]

const OPEN_ENDED_QUESTION = /(?:如何|为什么|怎样|区别|优缺点|条件|步骤|流程|分析|解释|说说|谈谈|哪些)/u

export function evaluateAnswerCompleteness(input = {}, options = {}) {
  const fallbackConfirmMs = positive(options.fallbackConfirmMs, DEFAULT_COMPLETENESS_CONFIRM_MS)
  try {
    const minimumSilenceMs = positive(options.minimumSilenceMs, 3000)
    const silenceDurationMs = Number(input.silenceDurationMs)
    if (Number.isFinite(silenceDurationMs) && silenceDurationMs < minimumSilenceMs) {
      return fallback('minimum-natural-pause-not-reached', fallbackConfirmMs)
    }
    const text = normalizeText(input.transcript)
    const lastSegmentText = normalizeText(input.lastCompletedSegmentText) || text
    if (!text) return fallback('no-completed-transcript', fallbackConfirmMs)

    const signals = []
    let score = 0.55
    const length = countContentCharacters(text)
    const pendingSegmentCount = nonNegativeInteger(input.pendingSegmentCount)
    const enumerationProgress = normalizeEnumerationProgress(
      input.enumerationProgress || detectEnumerationProgress(input.questionText, text),
    )
    if (input.questionType) {
      signals.push(signal('question-type-observed', 0, String(input.questionType)))
    }

    if (length < 8) {
      score -= 0.28
      signals.push(signal('answer-very-short', -0.28, `有效文本仅${length}个字符`))
    } else if (length < 20) {
      score -= 0.08
      signals.push(signal('answer-short', -0.08, `有效文本${length}个字符`))
    } else if (length >= 30) {
      score += 0.08
      signals.push(signal('answer-developed', 0.08, `有效文本${length}个字符`))
    }

    if (OPEN_ENDED_QUESTION.test(normalizeText(input.questionText)) && length < 30) {
      score -= 0.12
      signals.push(signal('open-question-needs-detail', -0.12, '开放式问题的回答较短'))
    }

    if (/[。！？.!?]$/u.test(lastSegmentText)) {
      score += 0.12
      signals.push(signal('terminal-punctuation', 0.12, '最后分段具有完整句末标点'))
    }

    if (EXPLICIT_ENDINGS.some((pattern) => pattern.test(lastSegmentText))) {
      score += 0.25
      signals.push(signal('explicit-completion-phrase', 0.25, '候选人使用了明确结束表达'))
    }

    if (DANGLING_ENDINGS.some((pattern) => pattern.test(lastSegmentText))) {
      score -= 0.32
      signals.push(signal('dangling-expression', -0.32, '最后分段以连接词、列举引导词或未闭合标点结尾'))
    }

    if (enumerationProgress.expectedCount > 0) {
      if (enumerationProgress.observedCount < enumerationProgress.expectedCount) {
        score -= 0.3
        signals.push(signal(
          'enumeration-incomplete',
          -0.3,
          `问题预期约${enumerationProgress.expectedCount}项，检测到${enumerationProgress.observedCount}项`,
        ))
      } else {
        score += 0.18
        signals.push(signal(
          'enumeration-complete',
          0.18,
          `检测到${enumerationProgress.observedCount}/${enumerationProgress.expectedCount}项`,
        ))
      }
    }

    if (pendingSegmentCount > 0) {
      score -= 0.12
      signals.push(signal('asr-pending', -0.12, `仍有${pendingSegmentCount}个分段等待识别`))
    }

    score = clamp(score, 0, 1)
    const classification = score >= 0.72
      ? AnswerCompletenessClassification.COMPLETE
      : score <= 0.35
        ? AnswerCompletenessClassification.INCOMPLETE
        : AnswerCompletenessClassification.UNCERTAIN
    let recommendedConfirmMs = classification === AnswerCompletenessClassification.INCOMPLETE
      ? INCOMPLETE_CONFIRM_MS
      : classification === AnswerCompletenessClassification.UNCERTAIN
        ? UNCERTAIN_CONFIRM_MS
        : fallbackConfirmMs
    if (pendingSegmentCount > 0) recommendedConfirmMs = Math.max(recommendedConfirmMs, PENDING_ASR_CONFIRM_MS)

    return {
      score,
      classification,
      signals,
      recommendedConfirmMs: Math.max(fallbackConfirmMs, recommendedConfirmMs),
      reason: explain(classification, signals),
      enumerationProgress,
      answerId: input.answerId || null,
      evaluatedAtPossibleEnd: input.isPossibleEnd === true,
    }
  } catch (error) {
    return fallback('rule-evaluation-error', fallbackConfirmMs, error)
  }
}

export function detectEnumerationProgress(questionText, transcript) {
  const question = normalizeText(questionText)
  const answer = normalizeText(transcript)
  const expectedCount = detectExpectedCount(question)
  if (!expectedCount) return { expectedCount: 0, observedCount: 0, source: 'none' }

  const markers = new Set()
  for (const match of answer.matchAll(/(?:^|[\s，,。；;])(?:第)?([一二三四五六七八九十]|\d{1,2})(?:[、，,.．:：]|是)/gu)) {
    markers.add(match[1])
  }
  const ordinalWords = ['首先', '其次', '再次', '最后']
  for (const word of ordinalWords) {
    if (answer.includes(word)) markers.add(word)
  }
  return { expectedCount, observedCount: markers.size, source: 'explicit-markers' }
}

function detectExpectedCount(question) {
  const arabic = question.match(/(\d{1,2})\s*(?:个|项|种|点|条|步|方面|条件|区别|原因)/u)
  if (arabic) return Number(arabic[1])
  const chinese = question.match(/([一二三四五六七八九十])\s*(?:个|项|种|点|条|步|方面|条件|区别|原因)/u)
  return chinese ? chineseNumber(chinese[1]) : 0
}

function normalizeEnumerationProgress(value) {
  return {
    expectedCount: nonNegativeInteger(value?.expectedCount),
    observedCount: nonNegativeInteger(value?.observedCount),
    source: value?.source || 'provided',
  }
}

function fallback(reason, recommendedConfirmMs, error) {
  return {
    score: 0.5,
    classification: AnswerCompletenessClassification.FALLBACK,
    signals: [signal(reason, 0, error?.message || '使用固定确认等待时间')],
    recommendedConfirmMs,
    reason,
    enumerationProgress: { expectedCount: 0, observedCount: 0, source: 'none' },
    answerId: null,
    evaluatedAtPossibleEnd: false,
  }
}

function signal(code, impact, detail) {
  return { code, impact, detail }
}

function explain(classification, signals) {
  const relevant = signals.filter((item) => item.impact !== 0).map((item) => item.code)
  return `${classification.toLowerCase()}:${relevant.join(',') || 'no-strong-signal'}`
}

function normalizeText(value) {
  return String(value || '').trim().replace(/\s+/g, ' ')
}

function countContentCharacters(value) {
  return value.replace(/[\s，,。.!！?？、:：;；'"“”‘’()（）]/gu, '').length
}

function chineseNumber(value) {
  const values = { 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9, 十: 10 }
  return values[value] || 0
}

function nonNegativeInteger(value) {
  const number = Number(value)
  return Number.isFinite(number) && number > 0 ? Math.floor(number) : 0
}

function positive(value, fallbackValue) {
  const number = Number(value)
  return Number.isFinite(number) && number > 0 ? number : fallbackValue
}

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value))
}
