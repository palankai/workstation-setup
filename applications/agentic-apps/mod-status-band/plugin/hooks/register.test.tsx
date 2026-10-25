import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

// 2026-10-25 12:00 UTC; the machine is on +01:00.
const NOW = Date.UTC(2026, 9, 25, 12, 0)

const GIT = [
  '# branch.oid 7e53171aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
  '# branch.head master',
  '# branch.upstream origin/master',
  '# branch.ab +2 -1',
  '# stash 1',
  '1 M. N... 100644 100644 100644 a b staged.txt',
  '1 .M N... 100644 100644 100644 a b edited.txt',
  '? new.txt',
  '',
].join('\n')

const BAND = {
  plugin: 'status-band',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  props: {
    hasSurvey: false,
    isWorking: false,
    maxRows: 10,
    bodyColumns: 140,
    scroll: { offset: 0, bodyRows: 9 },
    view: {},
  },
} as const

const LIMITS = [
  { kind: 'five_hour', percentUsed: 38, resetsAt: new Date(NOW + 130 * 60_000).toISOString() },
  { kind: 'seven_day', percentUsed: 82.5, resetsAt: new Date(NOW + 4 * 86_400_000).toISOString() },
]

type World = {
  clock: () => number
  rateLimits: typeof LIMITS
  contextTokens?: number
  transcriptLine: string
  store: Map<string, unknown>
}

// Stands in for the engine: the clock, the session, the processes and the store.
const engine = (on: On, w: World) => {
  const counts = { forks: 0 }
  // the band tests want it shown; hidden is the default
  if (!w.store.has('bandShown')) w.store.set('bandShown', true)
  on('clock.now', () => ({ value: w.clock() }))
  on('clock.every', () => ({ value: undefined }))
  on('session.id', () => ({ value: 'abc-123' }))
  on('session.cwd', () => ({ value: '/Users/me/opt/workstation-setup' }))
  on('session.usage', () => ({
    value: {
      startedAt: NOW,
      context: {
        window: 1_000_000,
        tokens: w.contextTokens,
        percent: w.contextTokens === undefined ? undefined : Math.round(w.contextTokens / 10_000),
      },
      rateLimits: w.rateLimits,
    },
  }))
  on('process.run', (_, e) => ({
    value: {
      exitCode: 0,
      stdout:
        e.argv[0] !== 'sh' ? GIT : String(e.argv[2]).includes('date +%z') ? '/Users/me\n+0100\n' : w.transcriptLine,
      stderr: '',
      isStdoutTruncated: false,
      isStderrTruncated: false,
    },
  }))
  on('store.get', (_, e) => ({ value: w.store.get(e.key) }))
  on('store.set', (_, e) => (w.store.set(e.key, e.value), { value: undefined }))
  on('store.delete', (_, e) => (w.store.delete(e.key), { value: undefined }))
  on('model.fork', () => {
    counts.forks += 1
    return { value: { isAnswered: true, text: 'ok', usage: {} } } as never
  })
  on('ui.toast', () => ({ value: undefined }))
  on('command.register', () => ({ value: { command: 'status-band' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  return counts
}

const TURN = {
  answer: 'done',
  durationMs: 1000,
  isAborted: false,
  turnId: 't1',
  reason: 'answer',
  usage: { model: 'claude-opus-5-5', input_tokens: 1, output_tokens: 1 } as never,
} as const

test('two rows: cache, context and limits with bars; then folder and git', async ($, on) => {
  const w: World = { clock: () => NOW, rateLimits: LIMITS, contextTokens: 170_000, transcriptLine: '', store: new Map() }
  engine(on, w)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    const text = (await ui.find({ type: 'Box' }))?.text ?? ''

    expect(text).toMatch(/📂 ~\/opt\/workstation-setup/)
    expect(text).toMatch(/⎇ master ●1 ✚1 …1 ⚑1 ⇡2 ⇣1 ⚙/)
    expect(text).toMatch(/🧠 █+░+ 17% of 1M/)
    expect(text).toMatch(/⏳ 5h █+░+ 38% ↻ 2h10m 15:10/)
    expect(text).toMatch(/📅 7d █+░* 83% ⚠ out Mon 03:44 ↻ Thu 13:00/)
    expect(text).toMatch(/💬 no reply yet 💤/)
    expect(text).not.toMatch(/hover|click/)
    const bars = text.match(/█+░*|░+/g) ?? []
    expect(bars).toHaveLength(3) // no reply yet: no cache bar
    expect(new Set(bars.map(bar => bar.length)).size).toBe(1)
    await ui.unmount()
  }
  expect(w.store.get('limits')).toEqual(LIMITS)
})

test('after a restart: last reply from the transcript, limits from the store', async ($, on) => {
  const at = NOW - 20 * 60_000
  const w: World = {
    clock: () => NOW,
    rateLimits: [],
    transcriptLine: JSON.stringify({
      type: 'assistant',
      timestamp: new Date(at).toISOString(),
      message: { usage: { input_tokens: 10, cache_read_input_tokens: 169_990, cache_creation_input_tokens: 0 } },
    }),
    store: new Map<string, unknown>([['limits', LIMITS]]),
  }
  engine(on, w)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const text = (await ui.find({ type: 'Box' }))?.text ?? ''
  expect(text).toMatch(/17% of 1M/)
  expect(text).toMatch(/⏳ 5h (█+░+ )?38%/)
  // left to the default, keep-warm stops at the 5h reset
  expect(text).toMatch(/🔥 20m ago (█+░+ )?12:40 ☕ 15:10/)
  await ui.unmount()
})

test('keep warm runs until the 5h reset by default; the switch cycles full hours, off, default', async ($, on) => {
  let clock = NOW
  const w: World = { clock: () => clock, rateLimits: LIMITS, transcriptLine: '', store: new Map() }
  const counts = engine(on, w)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.turn.complete(TURN)

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop', props: { ...BAND.props, bodyColumns: 200 } })
  const text = async () => (await ui.find({ type: 'Box' }))?.text ?? ''
  // the 5h window resets at 15:10, before the 8 hours are up
  expect(await text()).toMatch(/🔥 0m ago █+ 13:00 ☕ 15:10/)

  await ui.press({ key: 'warm-toggle' })
  expect(await text()).toMatch(/13:00 ♨ 21:00/)
  expect(w.store.get('warm:abc-123')).toEqual({ mode: 'on', from: NOW })

  await ui.press({ key: 'warm-toggle' })
  expect(await text()).toMatch(/13:00 🚫/)
  expect(w.store.get('warm:abc-123')).toEqual({ mode: 'off' })

  // back to the default an hour on: the cache is due, the 5h window still open
  clock = NOW + 56 * 60_000
  await ui.press({ key: 'warm-toggle' })
  expect(counts.forks).toBe(1)
  expect(await text()).toMatch(/🔥 0m ago █+ 13:56 ☕ 15:10/)
  expect(w.store.get('cacheAt:abc-123')).toBe(clock)

  await ui.unmount()
})

// A session restarted 56 minutes after its last reply, the cache due a ping.
const restartedWithReset = (resetIn: number): World => ({
  clock: () => NOW,
  rateLimits: [],
  transcriptLine: JSON.stringify({ type: 'assistant', timestamp: new Date(NOW - 56 * 60_000).toISOString(), message: {} }),
  store: new Map<string, unknown>([
    ['limits', [{ kind: 'five_hour', percentUsed: 50, resetsAt: new Date(NOW + resetIn * 60_000).toISOString() }]],
  ]),
})

test('left to the default, a ping goes out while the 5h window is open', async ($, on) => {
  const counts = engine(on, restartedWithReset(30))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(counts.forks).toBe(1)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await ui.find({ type: 'Box' }))?.text).toMatch(/🔥 0m ago .*☕ 13:30/)
  await ui.unmount()
})

test('left to the default, no ping goes out once the 5h window has reset', async ($, on) => {
  const counts = engine(on, restartedWithReset(-1))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(counts.forks).toBe(0)
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await ui.find({ type: 'Box' }))?.text).toMatch(/56m ago .*💤/)
  await ui.unmount()
})

test('the settings pane changes the default and the hours for every session', async ($, on) => {
  const late = [{ kind: 'five_hour', percentUsed: 10, resetsAt: new Date(NOW + 290 * 60_000).toISOString() }]
  const w: World = { clock: () => NOW, rateLimits: late, transcriptLine: '', store: new Map() }
  engine(on, w)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.turn.complete(TURN)

  for (const surface of ['terminal', 'desktop'] as const) {
    const pane = await $.ui.mount({
      plugin: 'status-band',
      component: 'Pane',
      requestId: 'status-band-settings',
      surface,
      props: { title: 'Status band', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 20 }, view: {} },
    })
    await pane.press({ key: 'hours-2' })
    expect(w.store.get('settings')).toEqual({ isWarmByDefault: true, warmHours: 2, bands: [25, 50, 75] })
    await pane.unmount()
  }

  const band = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect((await band.find({ type: 'Box' }))?.text).toMatch(/☕ 15:00/)

  const pane = await $.ui.mount({
    plugin: 'status-band',
    component: 'Pane',
    requestId: 'status-band-settings',
    surface: 'desktop',
    props: { title: 'Status band', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 20 }, view: {} },
  })
  await pane.press({ key: 'default-off' })
  expect((await band.find({ type: 'Box' }))?.text).toMatch(/13:00 🚫/)
  await pane.unmount()
  await band.unmount()
})

test('bars grow with the width and give way when it is narrow', async ($, on) => {
  const w: World = { clock: () => NOW, rateLimits: LIMITS, contextTokens: 170_000, transcriptLine: '', store: new Map() }
  engine(on, w)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const bar = async (bodyColumns: number) => {
    const ui = await $.ui.mount({ ...BAND, surface: 'terminal', props: { ...BAND.props, bodyColumns } })
    const text = (await ui.find({ type: 'Box' }))?.text ?? ''
    await ui.unmount()
    return (text.match(/⏳ 5h ([█░]*)/)?.[1] ?? '').length
  }
  const wide = await bar(240)
  const middle = await bar(140)
  expect(wide).toBeGreaterThan(middle)
  expect(middle).toBeGreaterThan(0)
  expect(await bar(60)).toBe(0)
})

test('limits are coloured by pace; the colour bands are for the context alone', async ($, on) => {
  const w: World = { clock: () => NOW, rateLimits: LIMITS, contextTokens: 170_000, transcriptLine: '', store: new Map() }
  engine(on, w)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const band = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const colorOf = async (text: RegExp) => (await band.find({ type: 'Text', text }))?.props.color
  // 5h: 38% used with 57% of the window gone, about 67% by the reset
  expect(await colorOf(/^ 38%$/)).toBe('success')
  // 7d: 83% used with 3 of 7 days gone, out long before the reset
  expect(await colorOf(/^ 83%$/)).toBe('error')
  expect(await colorOf(/^ 17%$/)).toBe('success')

  const pane = await $.ui.mount({
    plugin: 'status-band',
    component: 'Pane',
    requestId: 'status-band-settings',
    surface: 'desktop',
    props: { title: 'Status band', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 20 }, view: {} },
  })
  await pane.press({ key: 'band-0-down' })
  await pane.press({ key: 'band-0-down' })
  expect((w.store.get('settings') as { bands: number[] }).bands).toEqual([15, 50, 75])
  expect(await colorOf(/^ 17%$/)).toBe('warning')
  expect(await colorOf(/^ 38%$/)).toBe('success')
  for (let i = 0; i < 5; i += 1) await pane.press({ key: 'band-0-down' })
  expect((w.store.get('settings') as { bands: number[] }).bands).toEqual([5, 50, 75])
  for (let i = 0; i < 12; i += 1) await pane.press({ key: 'band-0-up' })
  expect((w.store.get('settings') as { bands: number[] }).bands).toEqual([45, 50, 75])
  await pane.press({ key: 'bands-reset' })
  expect((w.store.get('settings') as { bands: number[] }).bands).toEqual([25, 50, 75])
  await pane.unmount()
  await band.unmount()
})

test('the footer keeps the cache, the switch, the context and the limits in sight beside the mode labels', async ($, on) => {
  const w: World = { clock: () => NOW, rateLimits: LIMITS, contextTokens: 170_000, transcriptLine: '', store: new Map() }
  engine(on, w)
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.turn.complete(TURN)

  for (const surface of ['terminal', 'desktop'] as const) {
    const footer = await $.ui.mount({ plugin: 'status-band', component: 'SessionMode', surface, props: { modes: ['focus'] } } as never)
    const text = async () => (await footer.find({ type: 'Box' }))?.text ?? ''
    expect(await text()).toBe('focus · ▾ 🔥 0m ☕ 🧠17% ⏳38% 📅83%')
    await footer.press({ key: 'footer-warm' })
    expect(await text()).toMatch(/🔥 0m ♨ 🧠/)
    await footer.press({ key: 'footer-warm' })
    expect(await text()).toMatch(/🔥 0m 🚫 🧠/)
    expect(w.store.get('warm:abc-123')).toEqual({ mode: 'off' })
    await footer.press({ key: 'footer-warm' })
    expect(w.store.get('warm:abc-123')).toEqual({ mode: 'auto' })
    await footer.unmount()
  }
})

test('the band is hidden by default; the footer\'s ▴/▾ button shows and hides it', async ($, on) => {
  const w: World = { clock: () => NOW, rateLimits: LIMITS, contextTokens: 170_000, transcriptLine: '', store: new Map([['bandShown', false]]) }
  engine(on, w)
  w.store.delete('bandShown')
  // the engine's own drawing, which the hidden band hands over to: nothing
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine</Text>
  })
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.turn.complete(TURN)

  const band = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const bandText = async () => (await band.find({ type: 'Box' }))?.text ?? ''
  expect(await bandText()).not.toMatch(/📂/)

  for (const surface of ['terminal', 'desktop'] as const) {
    const footer = await $.ui.mount({ plugin: 'status-band', component: 'SessionMode', surface, props: { modes: [] } } as never)
    await footer.press({ key: 'footer-band' })
    expect(await bandText()).toMatch(/📂 ~\/opt\/workstation-setup/)
    expect(w.store.get('bandShown')).toBe(true)
    expect((await footer.find({ type: 'Box' }))?.text).toMatch(/^▾ /)
    await footer.press({ key: 'footer-band' })
    expect((await footer.find({ type: 'Box' }))?.text).toMatch(/^▴ /)
    expect(await bandText()).not.toMatch(/📂/)
    // the switch leaves the band alone
    await footer.press({ key: 'footer-warm' })
    expect(await bandText()).not.toMatch(/📂/)
    await footer.press({ key: 'footer-warm' })
    await footer.press({ key: 'footer-warm' })
    await footer.unmount()
  }
  await band.unmount()
})
