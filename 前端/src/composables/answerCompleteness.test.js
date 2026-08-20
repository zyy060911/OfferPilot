import { describe, expect, it } from 'vitest'
import {
  AnswerCompletenessClassification as Classification,
  detectEnumerationProgress,
  evaluateAnswerCompleteness,
} from './answerCompleteness'

describe('answerCompleteness', () => {
  it('falls back to the existing 800ms policy when no completed ASR text exists', () => {
    expect(evaluateAnswerCompleteness({ transcript: '', pendingSegmentCount: 1 })).toMatchObject({
      classification: Classification.FALLBACK,
      recommendedConfirmMs: 800,
      reason: 'no-completed-transcript',
    })
  })

  it('keeps the default confirmation for a clearly completed answer', () => {
    const result = evaluateAnswerCompleteness({
      questionText: '请解释一下事件循环。',
      transcript: '事件循环会依次处理宏任务，并在每个宏任务结束后清空微任务队列。我的回答完毕。',
      lastCompletedSegmentText: '我的回答完毕。',
      pendingSegmentCount: 0,
      isPossibleEnd: true,
      answerId: 'answer-1',
    })
    expect(result.classification).toBe(Classification.COMPLETE)
    expect(result.recommendedConfirmMs).toBe(800)
    expect(result.signals.map((item) => item.code)).toContain('explicit-completion-phrase')
  })

  it('extends confirmation for a dangling connector without ending earlier than the fallback', () => {
    const result = evaluateAnswerCompleteness({
      questionText: 'interface和type有什么区别？',
      transcript: 'interface可以声明合并，type可以表达联合类型，另外',
      lastCompletedSegmentText: '另外',
    })
    expect(result.classification).toBe(Classification.INCOMPLETE)
    expect(result.recommendedConfirmMs).toBe(2000)
    expect(result.signals.map((item) => item.code)).toContain('dangling-expression')
  })

  it('detects explainable incomplete enumeration progress', () => {
    const progress = detectEnumerationProgress(
      '死锁的四个必要条件是什么？',
      '第一，互斥条件。第二，请求并保持。',
    )
    expect(progress).toMatchObject({ expectedCount: 4, observedCount: 2 })
    const result = evaluateAnswerCompleteness({
      questionText: '死锁的四个必要条件是什么？',
      transcript: '第一，互斥条件。第二，请求并保持。',
      enumerationProgress: progress,
    })
    expect(result.classification).toBe(Classification.INCOMPLETE)
    expect(result.signals.map((item) => item.code)).toContain('enumeration-incomplete')
  })

  it('recognizes completed explicit enumeration', () => {
    const result = evaluateAnswerCompleteness({
      questionText: '死锁的四个必要条件是什么？',
      transcript: '第一，互斥。第二，请求并保持。第三，不可剥夺。第四，循环等待。',
      lastCompletedSegmentText: '第四，循环等待。',
    })
    expect(result.classification).toBe(Classification.COMPLETE)
    expect(result.enumerationProgress).toMatchObject({ expectedCount: 4, observedCount: 4 })
    expect(result.recommendedConfirmMs).toBe(800)
  })

  it('allows pending ASR only to extend the confirmation period', () => {
    const result = evaluateAnswerCompleteness({
      questionText: '请解释闭包。',
      transcript: '闭包让内部函数可以访问外部函数作用域中的变量。',
      pendingSegmentCount: 1,
    })
    expect(result.recommendedConfirmMs).toBeGreaterThanOrEqual(1600)
  })

  it('never recommends less than the configured natural confirmation pause', () => {
    const result = evaluateAnswerCompleteness({
      transcript: '这是一个表达完整并且具有明确句号的回答。',
      lastCompletedSegmentText: '这是一个表达完整并且具有明确句号的回答。',
    }, { fallbackConfirmMs: 1000 })
    expect(result.recommendedConfirmMs).toBeGreaterThanOrEqual(1000)
  })

  it('refuses semantic classification before the minimum natural silence', () => {
    const result = evaluateAnswerCompleteness({
      transcript: '这是一段看起来完整的回答。',
      silenceDurationMs: 2999,
      isPossibleEnd: true,
    }, { minimumSilenceMs: 3000 })
    expect(result).toMatchObject({
      classification: Classification.FALLBACK,
      reason: 'minimum-natural-pause-not-reached',
      recommendedConfirmMs: 800,
    })
  })
})
