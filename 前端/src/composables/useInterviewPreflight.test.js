import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { PreflightState, useInterviewPreflight } from './useInterviewPreflight'

describe('useInterviewPreflight', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('waits for backend, connection and media before becoming ready', () => {
    const preflight = useInterviewPreflight()
    preflight.start()
    preflight.markReady('backend')
    preflight.markReady('digitalHuman')
    expect(preflight.state.value).toBe(PreflightState.LOADING)
    expect(preflight.progress.value).toBe(67)

    preflight.markReady('media')
    expect(preflight.state.value).toBe(PreflightState.READY)
    expect(preflight.progress.value).toBe(100)
  })

  it('only starts the interview from ready state', () => {
    const preflight = useInterviewPreflight()
    preflight.start()
    expect(preflight.beginInterview()).toBe(false)
    for (const check of ['backend', 'digitalHuman', 'media']) preflight.markReady(check)
    expect(preflight.beginInterview()).toBe(true)
    expect(preflight.state.value).toBe(PreflightState.STARTED)
    expect(preflight.beginInterview()).toBe(false)
  })

  it('reports timeout without fabricating readiness', () => {
    const preflight = useInterviewPreflight({ timeoutMs: 1000 })
    preflight.start()
    preflight.markReady('backend')
    vi.advanceTimersByTime(1000)
    expect(preflight.state.value).toBe(PreflightState.ERROR)
    expect(preflight.error.value.source).toBe('timeout')
    expect(preflight.checks.value.media).toBe(false)
  })

  it('can retry while preserving already completed checks', () => {
    const preflight = useInterviewPreflight()
    preflight.start()
    preflight.markReady('backend')
    preflight.fail('digitalHuman', new Error('offline'))
    preflight.retry()
    expect(preflight.state.value).toBe(PreflightState.LOADING)
    expect(preflight.checks.value.backend).toBe(true)
    expect(preflight.error.value).toBeNull()
  })

  it('dispose clears the timeout', () => {
    const preflight = useInterviewPreflight({ timeoutMs: 1000 })
    preflight.start()
    preflight.dispose()
    vi.advanceTimersByTime(1000)
    expect(preflight.state.value).toBe(PreflightState.LOADING)
  })
})
