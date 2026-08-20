import { describe, expect, it, vi } from 'vitest'
import {
  DIGITAL_HUMAN_PROTOCOL_VERSION,
  createSpeechWatchdog,
  createSpeechId,
  isSpeechLifecycleMessage,
  isDigitalHumanActionMessage,
  isCurrentDigitalHumanActionMessage,
  isTrustedEmbedMessage,
} from './digitalHumanMessaging'

describe('digital human message protocol', () => {
  it('creates a unique speechId from the parent-side request', () => {
    let id = 0
    const cryptoApi = { randomUUID: () => `id-${++id}` }
    expect(createSpeechId(cryptoApi)).toBe('id-1')
    expect(createSpeechId(cryptoApi)).toBe('id-2')
  })

  it('requires both the iframe source and an allowed origin', () => {
    const frameWindow = {}
    expect(isTrustedEmbedMessage(
      { source: frameWindow, origin: 'https://avatar.example' },
      frameWindow,
      ['https://avatar.example'],
    )).toBe(true)
    expect(isTrustedEmbedMessage(
      { source: {}, origin: 'https://avatar.example' },
      frameWindow,
      ['https://avatar.example'],
    )).toBe(false)
    expect(isTrustedEmbedMessage(
      { source: frameWindow, origin: 'https://evil.example' },
      frameWindow,
      ['https://avatar.example'],
    )).toBe(false)
  })

  it('rejects unknown or unversioned lifecycle messages', () => {
    expect(isSpeechLifecycleMessage({
      version: DIGITAL_HUMAN_PROTOCOL_VERSION,
      type: 'offerpilot.embed.speech.started',
      speechId: 'speech-1',
    })).toBe(true)
    expect(isSpeechLifecycleMessage({
      type: 'offerpilot.embed.speech.started',
      speechId: 'speech-1',
    })).toBe(false)
    expect(isSpeechLifecycleMessage({
      version: DIGITAL_HUMAN_PROTOCOL_VERSION,
      type: 'offerpilot.embed.speech.unknown',
      speechId: 'speech-1',
    })).toBe(false)
  })

  it('accepts only versioned and correlated action results', () => {
    expect(isDigitalHumanActionMessage({
      version: DIGITAL_HUMAN_PROTOCOL_VERSION,
      type: 'offerpilot.embed.action.fallback',
      requestId: 'action-1',
      requestedAction: 'THINKING',
    })).toBe(true)
    expect(isDigitalHumanActionMessage({
      type: 'offerpilot.embed.action.applied',
      requestId: 'action-1',
      requestedAction: 'LISTENING',
    })).toBe(false)
    expect(isDigitalHumanActionMessage({
      version: DIGITAL_HUMAN_PROTOCOL_VERSION,
      type: 'offerpilot.embed.action.unknown',
      requestId: 'action-1',
      requestedAction: 'LISTENING',
    })).toBe(false)
    expect(isCurrentDigitalHumanActionMessage({
      version: DIGITAL_HUMAN_PROTOCOL_VERSION,
      type: 'offerpilot.embed.action.applied',
      requestId: 'old-action',
      requestedAction: 'LISTENING',
    }, 'new-action')).toBe(false)
  })

  it('does not schedule lifecycle completion before speech-started', () => {
    const setTimer = vi.fn()
    createSpeechWatchdog({ timeoutMs: 100, onTimeout: vi.fn(), setTimer, clearTimer: vi.fn() })
    expect(setTimer).not.toHaveBeenCalled()
  })

  it('reports a missing ended event as an error without fabricating ended', () => {
    let scheduled
    const onTimeout = vi.fn()
    const watchdog = createSpeechWatchdog({
      timeoutMs: 100,
      onTimeout,
      setTimer: (callback) => {
        scheduled = callback
        return 7
      },
      clearTimer: vi.fn(),
    })
    watchdog.start('speech-1')
    scheduled()
    expect(onTimeout).toHaveBeenCalledWith('speech-1')
  })

  it('stops the watchdog and releases its timer on page cleanup', () => {
    const clearTimer = vi.fn()
    const watchdog = createSpeechWatchdog({
      timeoutMs: 100,
      onTimeout: vi.fn(),
      setTimer: () => 9,
      clearTimer,
    })
    watchdog.start('speech-1')
    watchdog.dispose()
    expect(clearTimer).toHaveBeenCalledWith(9)
  })
})
