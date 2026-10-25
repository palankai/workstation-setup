export type StatusBandGit = {
  branch: string
  staged: number
  modified: number
  untracked: number
  conflicts: number
  stashes: number
  ahead: number
  behind: number
  hasUpstream: boolean
}

export type StatusBandLimit = { kind: string; percentUsed: number; resetsAt?: string }

export type StatusBandUsage = {
  contextTokens?: number
  contextWindow: number
  contextPercent?: number
  limits: StatusBandLimit[]
}

export type StatusBandPing = { at: number; isOk: boolean; reason?: string }

/**
 * Settings for every session, kept in the plugin store. `bands` are the three
 * percentages where green turns yellow, yellow orange, and orange red.
 */
export type StatusBandSettings = { isWarmByDefault: boolean; warmHours: number; bands: [number, number, number] }

/**
 * This session's keep-warm choice: `auto` follows the settings, `on` was
 * switched on by hand at `from`, `off` was switched off by hand.
 */
export type StatusBandWarm = { mode: 'auto' } | { mode: 'on'; from: number } | { mode: 'off' }

declare module 'claude-code' {
  interface PluginState {
    'status-band': {
      now: number
      folder: string
      path: string
      git: StatusBandGit | null
      usage: StatusBandUsage | null
      cacheAt: number | null
      lastReplyAt: number | null
      warm: StatusBandWarm
      settings: StatusBandSettings
      lastPing: StatusBandPing | null
      utcOffsetMinutes: number
      /** Whether the band above the prompt shows; toggled from the footer. */
      isBandShown: boolean
    }
  }
}
