import { atom, read, update } from 'claude-code'
import type { Color, EngineInterface, Register, SessionMeasureInput, SessionUsage } from 'claude-code'

import type { StatusBandGit, StatusBandLimit, StatusBandSettings, StatusBandUsage, StatusBandWarm } from '../types'

const MINUTE = 60_000
const HOUR = 60 * MINUTE
const CACHE_TTL = HOUR
const PING_AFTER = 55 * MINUTE
const RETRY_AFTER = 5 * MINUTE
const HOUR_CHOICES = [2, 4, 8, 12]
const DEFAULT_SETTINGS: StatusBandSettings = { isWarmByDefault: true, warmHours: 8, bands: [25, 50, 75] }
const BAND_STEP = 5
const PANE = 'status-band-settings'
const PANE_TITLE = 'Status band'

const now = atom({ plugin: 'status-band', key: 'now' } as const, 0)
const folder = atom({ plugin: 'status-band', key: 'folder' } as const, '')
const path = atom({ plugin: 'status-band', key: 'path' } as const, '')
const git = atom({ plugin: 'status-band', key: 'git' } as const, null)
const usage = atom({ plugin: 'status-band', key: 'usage' } as const, null)
const cacheAt = atom({ plugin: 'status-band', key: 'cacheAt' } as const, null)
const lastReplyAt = atom({ plugin: 'status-band', key: 'lastReplyAt' } as const, null)
const warm = atom({ plugin: 'status-band', key: 'warm' } as const, { mode: 'auto' })
const settings = atom({ plugin: 'status-band', key: 'settings' } as const, DEFAULT_SETTINGS)
const lastPing = atom({ plugin: 'status-band', key: 'lastPing' } as const, null)
const utcOffset = atom({ plugin: 'status-band', key: 'utcOffsetMinutes' } as const, 0)

// What survives a restart lives in $.store: the settings and the limits for the
// whole account, the cache time and keep-warm choice per session.
const SETTINGS_KEY = 'settings'
const LIMITS_KEY = 'limits'
const cacheKey = (id: string) => `cacheAt:${id}`
const warmKey = (id: string) => `warm:${id}`

// ── formatting ──────────────────────────────────────────────────────────────

const tokens = (n: number) =>
  n >= 1_000_000 ? `${+(n / 1_000_000).toFixed(1)}M` : n >= 1000 ? `${Math.round(n / 1000)}k` : `${n}`

const duration = (ms: number) => {
  const m = Math.max(0, Math.round(ms / MINUTE))
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  if (h < 24) return m % 60 ? `${h}h${m % 60}m` : `${h}h`
  return h % 24 ? `${Math.floor(h / 24)}d${h % 24}h` : `${Math.floor(h / 24)}d`
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// The module has no time zone of its own, so local time comes from the offset `date` reported.
const localTime = (ms: number, offsetMinutes: number, withDay: boolean) => {
  const d = new Date(ms + offsetMinutes * MINUTE)
  const hm = `${String(d.getUTCHours()).padStart(2, '0')}:${String(d.getUTCMinutes()).padStart(2, '0')}`
  return withDay ? `${DAYS[d.getUTCDay()]} ${hm}` : hm
}

// Green, yellow, orange, red: the colour of a percentage by the bands it passed.
const HEAT: Color[] = ['success', 'warning', 'claude', 'error']
// Whether two moments fall on different local days.
const isOtherDay = (a: number, b: number, offsetMinutes: number) =>
  Math.floor((a + offsetMinutes * MINUTE) / (24 * HOUR)) !== Math.floor((b + offsetMinutes * MINUTE) / (24 * HOUR))

const level = (percent: number, bands: readonly number[]): Color =>
  HEAT[bands.filter(b => percent >= b).length] ?? 'error'

const LIMIT_NAMES: Record<string, { icon: string; label: string; isLong: boolean }> = {
  five_hour: { icon: '⏳', label: '5h', isLong: false },
  seven_day: { icon: '📅', label: '7d', isLong: true },
}

const windowOf = (kind: string) => (kind.startsWith('five_hour') ? 5 * HOUR : 7 * 24 * HOUR)

/**
 * How a limit is going at the current pace: the share of the window it would
 * have used by the reset, its colour, and when it runs out if that is sooner.
 *
 * The first tenth of a window counts as a tenth, so one early burst does not
 * read as running out. Green under 75% by the reset, yellow to 100%, orange
 * to 125%, red past that or once 90% is used.
 */
const pace = (percent: number, left: number, windowMs: number, t: number) => {
  const elapsedMs = windowMs - left
  const projected = percent / Math.min(1, Math.max(0.1, elapsedMs / windowMs))
  const color: Color =
    percent >= 90 || projected >= 125
      ? 'error'
      : projected >= 100
        ? 'claude'
        : projected >= 75
          ? 'warning'
          : 'success'
  const outIn = percent > 0 && elapsedMs > 0 ? ((100 - percent) / percent) * elapsedMs : Infinity
  return { color, outAt: projected > 100 && outIn < left ? t + outIn : null }
}

const limitName = (kind: string) =>
  LIMIT_NAMES[kind] ?? {
    icon: '📊',
    label: kind.replace('five_hour', '5h').replace('seven_day', '7d').replace(/_/g, ' '),
    isLong: !kind.startsWith('five_hour'),
  }

// When keep-warm stops: the settings' hours after the last reply, or after it
// was switched on by hand; null while it is off.
const warmDeadline = (w: StatusBandWarm, s: StatusBandSettings, replyAt: number | null) => {
  if (w.mode === 'off' || (w.mode === 'auto' && !s.isWarmByDefault)) return null
  const base = Math.max(replyAt ?? 0, w.mode === 'on' ? w.from : 0)
  return base > 0 ? base + s.warmHours * HOUR : null
}

// ── laying out the band ─────────────────────────────────────────────────────

/** A run of text: the text, its colour, whether bold. */
type Run = [text: string, color?: Color, bold?: boolean]

/** One item of the first row: what goes before its bar, the bar, what follows. */
type Segment = { head: Run[]; bar?: Bar; tail: Run[] }

/** A bar: `solid` in one colour (cache, limits), `heat` coloured by the band each cell sits in (context). */
type Bar = { percent: number; style: 'solid'; color: Color } | { percent: number; style: 'heat' }

// The cells of a bar as runs of one colour each.
const barRuns = (bar: Bar, n: number, bands: readonly number[]): Run[] => {
  const filled = Math.round((Math.min(100, Math.max(0, bar.percent)) / 100) * n)
  const runs: Run[] = []
  for (let i = 0; i < n; i += 1) {
    const isFilled = i < filled
    const glyph = isFilled ? '█' : '░'
    const color: Color = !isFilled ? 'subtle' : bar.style === 'solid' ? bar.color : level(((i + 1) / n) * 100, bands)
    const last = runs[runs.length - 1]
    if (last && last[1] === color) last[0] += glyph
    else runs.push([glyph, color])
  }
  return runs
}

const MIN_BAR = 5
const MAX_BAR = 24
const GAP = 3
const BLOCK_WIDTH = 1.4

// Terminal cells a text takes: emoji and other wide glyphs take two.
const cells = (runs: Run[]) => {
  let n = 0
  for (const [text] of runs) {
    for (const ch of text) {
      const cp = ch.codePointAt(0) ?? 0
      if (cp === 0xfe0f || cp === 0x200d) continue
      n += cp >= 0x1f000 || cp === 0x23f3 || cp === 0x2615 || cp === 0x231b ? 2 : 1
    }
  }
  return n
}

// ── reading the world ───────────────────────────────────────────────────────

const parseGit = (out: string): StatusBandGit => {
  const g: StatusBandGit = {
    branch: '',
    staged: 0,
    modified: 0,
    untracked: 0,
    conflicts: 0,
    stashes: 0,
    ahead: 0,
    behind: 0,
    hasUpstream: false,
  }
  let oid = ''
  for (const line of out.split('\n')) {
    if (line.startsWith('# branch.oid ')) oid = line.slice(13, 20)
    else if (line.startsWith('# branch.head ')) g.branch = line.slice(14)
    else if (line.startsWith('# branch.upstream ')) g.hasUpstream = true
    else if (line.startsWith('# branch.ab ')) {
      const [a, b] = line.slice(12).split(' ')
      g.ahead = Math.abs(parseInt(a ?? '', 10)) || 0
      g.behind = Math.abs(parseInt(b ?? '', 10)) || 0
    } else if (line.startsWith('# stash ')) g.stashes = parseInt(line.slice(8), 10) || 0
    else if (line.startsWith('? ')) g.untracked += 1
    else if (line.startsWith('u ')) g.conflicts += 1
    else if (line.startsWith('1 ') || line.startsWith('2 ')) {
      if (line[2] !== '.') g.staged += 1
      if (line[3] !== '.') g.modified += 1
    }
  }
  if (g.branch === '(detached)') g.branch = `➦ ${oid}`
  return g
}

// Module variables start over on a reload; session.start fills them again.
let home = ''
let isWorking = false
let isPinging = false

async function refreshGit($: EngineInterface) {
  const cwd = await $.session.cwd()
  const name = cwd.split('/').filter(Boolean).pop() ?? cwd
  const full = home && (cwd === home || cwd.startsWith(`${home}/`)) ? `~${cwd.slice(home.length)}` : cwd
  await update($, folder, () => name)
  await update($, path, () => full)
  try {
    const r = await $.process.run(['git', 'status', '--porcelain=v2', '--branch', '--show-stash'], {
      cwd,
      timeoutMs: 5000,
    })
    await update($, git, () => (r.exitCode === 0 ? parseGit(r.stdout) : null))
  } catch {
    await update($, git, () => null)
  }
}

type LastReply = { at: number; contextTokens?: number }

// The transcript records every reply with its time and token usage, so after a
// restart the last main-thread reply says when the cache was last written.
async function readLastReply($: EngineInterface, sessionId: string): Promise<LastReply | null> {
  if (!/^[\w-]+$/.test(sessionId)) return null
  try {
    const r = await $.process.run(
      [
        'sh',
        '-c',
        `cat "\${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/projects/*/${sessionId}.jsonl 2>/dev/null` +
          ` | grep '"type":"assistant"' | grep -v '"isSidechain":true' | tail -n 1`,
      ],
      { timeoutMs: 5000 },
    )
    const line = r.stdout.trim()
    if (!line) return null
    const row = JSON.parse(line) as {
      timestamp?: string
      message?: { usage?: Record<string, number | undefined> }
    }
    const at = row.timestamp ? Date.parse(row.timestamp) : NaN
    if (Number.isNaN(at)) return null
    const u = row.message?.usage
    const contextTokens = u
      ? (u.input_tokens ?? 0) + (u.cache_read_input_tokens ?? 0) + (u.cache_creation_input_tokens ?? 0)
      : undefined
    return { at, contextTokens }
  } catch {
    return null
  }
}

const toUsage = (u: SessionUsage | SessionMeasureInput): StatusBandUsage => ({
  contextTokens: u.context.tokens,
  contextWindow: u.context.window,
  contextPercent: u.context.percent,
  limits: u.rateLimits.map(({ kind, percentUsed, resetsAt }) => ({ kind, percentUsed, resetsAt })),
})

// Live limits win; before the first reply of a session the last ones seen (on
// any session) stand in, so a restart still shows them.
async function setUsage($: EngineInterface, u: StatusBandUsage) {
  if (u.limits.length > 0) {
    await $.store.set(LIMITS_KEY, u.limits)
    await update($, usage, () => u)
    return
  }
  const saved = ((await $.store.get(LIMITS_KEY)) as StatusBandLimit[] | undefined) ?? []
  await update($, usage, prev => ({
    ...u,
    contextTokens: u.contextTokens ?? prev?.contextTokens,
    contextPercent: u.contextPercent ?? prev?.contextPercent,
    limits: saved,
  }))
}

async function setCacheAt($: EngineInterface, at: number) {
  await update($, cacheAt, prev => (prev === null || at > prev ? at : prev))
  await $.store.set(cacheKey(await $.session.id()), at)
}

async function setWarm($: EngineInterface, w: StatusBandWarm) {
  await update($, warm, () => w)
  await $.store.set(warmKey(await $.session.id()), w)
  const t = await $.clock.now()
  await update($, now, () => t)
  await keepWarm($)
}

async function setSettings($: EngineInterface, change: Partial<StatusBandSettings>) {
  const s = { ...(await read($, settings)), ...change }
  await update($, settings, () => s)
  await $.store.set(SETTINGS_KEY, s)
}

// Moves one band edge by a step, keeping the edges in order and a step apart.
async function moveBand($: EngineInterface, i: number, delta: number) {
  const b = [...(await read($, settings)).bands] as [number, number, number]
  const low = (b[i - 1] ?? 0) + BAND_STEP
  const high = (b[i + 1] ?? 100) - BAND_STEP
  b[i] = Math.min(high, Math.max(low, (b[i] ?? 0) + delta))
  await setSettings($, { bands: b })
}

async function openSettings($: EngineInterface) {
  await $.ui.open({ id: PANE, title: PANE_TITLE })
}

// ── keep-warm ───────────────────────────────────────────────────────────────

async function keepWarm($: EngineInterface) {
  const t = await $.clock.now()
  const w = await read($, warm)
  const deadline = warmDeadline(w, await read($, settings), await read($, lastReplyAt))
  const at = await read($, cacheAt)
  if (deadline === null || t >= deadline || at === null) return
  // Left alone, a cache that has gone cold stays cold; switched on by hand, it is warmed again.
  if (t - at >= CACHE_TTL && w.mode !== 'on') return
  if (isWorking || isPinging || t - at < PING_AFTER) return
  const ping = await read($, lastPing)
  if (ping && !ping.isOk && t - ping.at < RETRY_AFTER) return

  isPinging = true
  try {
    const r = await $.model.fork({ prompt: 'Keep-alive ping. Reply with the single word: ok' })
    const done = await $.clock.now()
    if (r.isAnswered) await setCacheAt($, done)
    await update($, lastPing, () => ({ at: done, isOk: r.isAnswered, reason: r.isAnswered ? undefined : r.reason }))
    // Right after a restart there is nothing to fork until the next reply: not worth a toast.
    if (!r.isAnswered && r.reason !== 'nothing-to-fork' && (ping === null || ping.isOk)) {
      $.ui.toast(`☕ Keep-warm ping failed: ${r.reason}`)
    }
  } finally {
    isPinging = false
  }
}

async function tick($: EngineInterface) {
  const t = await $.clock.now()
  await update($, now, () => t)
  await refreshGit($)
  await keepWarm($)
}

// ── the module ──────────────────────────────────────────────────────────────

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await $.command.register({ name: 'status-band', description: 'Open the status band settings' })
    try {
      const r = await $.process.run(['sh', '-c', 'printf "%s\\n%s" "$HOME" "$(date +%z)"'], { timeoutMs: 2000 })
      const [h, z] = r.stdout.split('\n')
      home = h ?? ''
      const m = (z ?? '').trim().match(/^([+-])(\d\d)(\d\d)$/)
      if (m) await update($, utcOffset, () => (m[1] === '-' ? -1 : 1) * (Number(m[2]) * 60 + Number(m[3])))
    } catch {
      // keep UTC and the absolute path
    }

    const id = await $.session.id()
    const s = (await $.store.get(SETTINGS_KEY)) as Partial<StatusBandSettings> | undefined
    await update($, settings, () => ({ ...DEFAULT_SETTINGS, ...s }))
    const w = (await $.store.get(warmKey(id))) as StatusBandWarm | undefined
    await update($, warm, () => w ?? { mode: 'auto' })

    const live = toUsage(await $.session.usage())
    const reply = await readLastReply($, id)
    const stored = (await $.store.get(cacheKey(id))) as number | undefined
    const at = Math.max(reply?.at ?? 0, stored ?? 0)
    if (at > 0) await update($, cacheAt, () => at)
    if (reply) await update($, lastReplyAt, () => reply.at)
    if (live.contextTokens === undefined && reply?.contextTokens !== undefined) {
      live.contextTokens = reply.contextTokens
      live.contextPercent = Math.round((reply.contextTokens / live.contextWindow) * 100)
    }
    await setUsage($, live)

    await tick($)
    $.clock.every(MINUTE, () => void tick($))
    return result
  })

  on('command.run', { command: 'status-band' }, async $ => {
    await openSettings($)
    return { text: 'Status band settings opened.' }
  })

  on('session.measure', async ($, e, next) => {
    await setUsage($, toUsage(e))
    return next(e)
  })

  on('turn.start', ($, e, next) => {
    if (!e.agentId) isWorking = true
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (!e.agentId) {
      isWorking = false
      const t = await $.clock.now()
      if (e.usage) {
        await setCacheAt($, t)
        await update($, lastReplyAt, () => t)
      }
      await update($, now, () => t)
      await refreshGit($)
    }
    return next(e)
  })

  // ── the settings pane ──

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const s = await read($, settings)
    const pick = (isOn: boolean) => (isOn ? { variant: 'primary' as const } : {})

    return (
      <Box flexDirection="column" gap={1}>
        <Text bold>☕ Keep the prompt cache warm</Text>
        <Box flexDirection="column">
          <Text>In every new session</Text>
          <Box flexDirection="row" gap={1}>
            <Button key="default-on" label="On" {...pick(s.isWarmByDefault)} onPress={() => setSettings($, { isWarmByDefault: true })} />
            <Button key="default-off" label="Off" {...pick(!s.isWarmByDefault)} onPress={() => setSettings($, { isWarmByDefault: false })} />
          </Box>
        </Box>
        <Box flexDirection="column">
          <Text>For how long after the last reply</Text>
          <Box flexDirection="row" gap={1}>
            {HOUR_CHOICES.map(hours => (
              <Button key={`hours-${hours}`} label={`${hours}h`} {...pick(s.warmHours === hours)} onPress={() => setSettings($, { warmHours: hours })} />
            ))}
          </Box>
        </Box>
        <Box flexDirection="column">
          <Text>Colour bands for the context</Text>
          <Box flexDirection="row" gap={1} alignItems="center">
            <Text color={HEAT[0]}>green</Text>
            {s.bands.flatMap((edge, i) => [
              <Button key={`band-${i}-down`} label="−" onPress={() => moveBand($, i, -BAND_STEP)} />,
              <Text bold>{edge}%</Text>,
              <Button key={`band-${i}-up`} label="+" onPress={() => moveBand($, i, BAND_STEP)} />,
              <Text color={HEAT[i + 1]}>{['yellow', 'orange', 'red'][i]}</Text>,
            ])}
            <Button key="bands-reset" label="Reset" onPress={() => setSettings($, { bands: DEFAULT_SETTINGS.bands })} />
          </Box>
          <Text>
            {barRuns({ percent: 100, style: 'heat' }, 20, s.bands).map(([text, color]) => (
              <Text color={color}>{text}</Text>
            ))}
          </Text>
        </Box>
        <Text dimColor>
          While the session is idle, a tiny request goes out about every 55 minutes so the 1-hour cache never
          expires. Each one reads the whole cached conversation: it costs cache-read tokens and counts a little
          towards your usage limits. In the band, ♨ switches it off for that session and ☕ switches it on.
        </Text>
      </Box>
    )
  })

  // ── the band ──
  //
  // Row 1: cache, context, 5h, 7d, each as wide as its text plus a bar, the bars
  // all one length that uses up the row. Row 2: the folder left, git right.

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)

    const { Box, Text, Button } = $.ui.resolve(e)
    const t = (await read($, now)) || (await $.clock.now())
    const offset = await read($, utcOffset)
    const full = await read($, path)
    const g = await read($, git)
    const u = await read($, usage)
    const at = await read($, cacheAt)
    const ping = await read($, lastPing)
    const cfg = await read($, settings)
    const lv = (p: number) => level(p, cfg.bands)
    const deadline = warmDeadline(await read($, warm), cfg, await read($, lastReplyAt))
    const isWarm = deadline !== null && deadline > t

    const draw = (runs: Run[]) => runs.map(([text, color, bold]) => <Text color={color} bold={bold}>{text}</Text>)

    // The cache segment: the bar drains over the hour the cache lives.
    const cache: Segment = (() => {
      if (at === null) return { head: [['💬 no reply yet', 'subtle']], tail: [] }
      const left = at + CACHE_TTL - t
      const isCold = left <= 0
      const icon = isCold ? '🧊' : left < 15 * MINUTE ? '🌡️' : '🔥'
      const c: Color = isCold ? 'subtle' : left < 5 * MINUTE ? 'error' : left < 15 * MINUTE ? 'warning' : 'success'
      return {
        head: [[`${icon} `], [`${duration(t - at)} ago`, c]],
        bar: { percent: isCold ? 0 : (left / CACHE_TTL) * 100, style: 'solid', color: c },
        tail: [[` ${localTime(at, offset, t - at > 20 * HOUR)}`, 'subtle']],
      }
    })()
    const warmLabel = isWarm ? ` ♨ ${localTime(deadline, offset, deadline - t > 20 * HOUR)}` : ' ☕'
    const failed = isWarm && ping && !ping.isOk ? ' ⚠' : ''

    const segments: Segment[] = [cache]
    if (u) {
      const p = u.contextPercent
      segments.push({
        head: [['🧠']],
        bar: p === undefined ? undefined : { percent: p, style: 'heat' },
        tail: [[` ${p ?? '–'}%`, p === undefined ? 'subtle' : lv(p)], [` of ${tokens(u.contextWindow)}`, 'subtle']],
      })
      for (const l of u.limits) {
        const n = limitName(l.kind)
        const reset = l.resetsAt ? Date.parse(l.resetsAt) : NaN
        const left = Number.isNaN(reset) ? null : reset - t
        // a window whose reset has passed starts again at 0
        const percent = left !== null && left <= 0 ? 0 : Math.round(l.percentUsed)
        const p = left !== null && left > 0 ? pace(percent, left, windowOf(l.kind), t) : null
        const color = p?.color ?? 'success'
        segments.push({
          head: [[`${n.icon} `], [n.label, undefined, true]],
          bar: { percent, style: 'solid', color },
          tail: [
            [` ${percent}%`, color],
            ...(p?.outAt ? ([[` ⚠ out ${localTime(p.outAt, offset, isOtherDay(p.outAt, t, offset))}`, color]] as Run[]) : []),
            ...(left !== null && left > 0
              ? ([
                  [
                    ` ↻ ${n.isLong ? localTime(reset, offset, true) : `${duration(left)} ${localTime(reset, offset, false)}`}`,
                    'subtle',
                  ],
                ] as Run[])
              : []),
          ],
        })
      }
    }

    // Every bar has the same length: what the row has left once each item's text
    // is placed, shared out. Each item's width is its text plus that bar, so wordy
    // items get more room and the gaps between items even out.
    const columns = e.props.bodyColumns
    const fixed = (s: Segment, i: number) =>
      cells(s.head) + cells(s.tail) + (i === 0 ? cells([[warmLabel + failed]]) : 0) + GAP
    const texts = segments.map(fixed)
    const total = texts.reduce((sum, n) => sum + n, 0)
    // A graphical surface draws the block glyphs wider than a cell.
    const cellsPerGlyph = (s: Segment | undefined) =>
      !s?.bar ? 0 : e.surface !== 'terminal' ? BLOCK_WIDTH : 1
    const perGlyph = segments.reduce((sum, s) => sum + cellsPerGlyph(s), 0)
    const isEven = total <= columns
    const fit = isEven && perGlyph > 0 ? Math.min(MAX_BAR, Math.floor((columns - total - segments.length) / perGlyph)) : 0
    const barCells = fit >= MIN_BAR ? fit : 0
    const widthOf = (i: number) => {
      const bar = barCells ? Math.ceil(barCells * cellsPerGlyph(segments[i])) + 1 : 0
      return `${Math.floor((((texts[i] ?? 0) + bar) / columns) * 100)}%`
    }

    const row1 = segments.map((s, i) => {
      return (
        <Box flexDirection="row" width={isEven ? widthOf(i) : undefined} marginRight={isEven ? 0 : 2} flexShrink={1}>
          <Text wrap="truncate-end">
            {draw(s.head)}
            {barCells > 0 && s.bar ? (
              <Text>
                {' '}
                {draw(barRuns(s.bar, barCells, cfg.bands))}
              </Text>
            ) : (
              ''
            )}
            {draw(s.tail)}
          </Text>
          {i === 0 ? (
            <Button key="warm-toggle" plain onPress={async () =>
              setWarm($, isWarm ? { mode: 'off' } : { mode: 'on', from: await $.clock.now() })
            }>
              <Text color={isWarm ? 'claude' : 'subtle'}>{warmLabel}</Text>
              {failed ? <Text color="warning">{failed}</Text> : ''}
            </Button>
          ) : (
            ''
          )}
        </Box>
      )
    })

    // Row 2: folder left; git and the settings gear right.
    const gitRuns: Run[] = g
      ? [
          [`⎇ ${g.branch}`, 'merged'],
          ...(g.conflicts ? ([[` ✖${g.conflicts}`, 'error']] as Run[]) : []),
          ...(g.staged ? ([[` ●${g.staged}`, 'success']] as Run[]) : []),
          ...(g.modified ? ([[` ✚${g.modified}`, 'warning']] as Run[]) : []),
          ...(g.untracked ? ([[` …${g.untracked}`, 'subtle']] as Run[]) : []),
          ...(g.staged + g.modified + g.untracked + g.conflicts === 0 ? ([[' ✔', 'success']] as Run[]) : []),
          ...(g.stashes ? ([[` ⚑${g.stashes}`, 'permission']] as Run[]) : []),
          ...(g.ahead ? ([[` ⇡${g.ahead}`, 'suggestion']] as Run[]) : []),
          ...(g.behind ? ([[` ⇣${g.behind}`, 'warning']] as Run[]) : []),
          ...(!g.hasUpstream ? ([[' ⊘ no upstream', 'subtle']] as Run[]) : []),
        ]
      : []

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" flexWrap="wrap">
          {row1}
        </Box>
        <Box flexDirection="row" justifyContent="space-between">
          <Text color="suggestion" bold>
            📂 {full}
          </Text>
          <Box flexDirection="row">
            {draw(gitRuns)}
            <Button key="settings" plain onPress={() => openSettings($)}>
              <Text color="subtle"> ⚙</Text>
            </Button>
          </Box>
        </Box>
      </Box>
    )
  })
}
