import { AlertTriangle, Boxes, History, LayoutGrid, List, Loader2, RotateCcw, Save, Search, X } from 'lucide-react'
import { type ReactNode, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, type Application, type Profile, type RunSummary, type SavedSearch } from './api'
import { AppCard, AppRow } from './components/AppCard'
import { DetailPanel } from './components/DetailPanel'
import { RunReport } from './components/RunReport'
import { STATUS_TEXT, relativeTime } from './runs'
import { search } from './search'
import { difference, impliedBy } from './selection'

type View = 'all' | 'selected' | 'available' | 'changes'

const VIEWS: { id: View; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'selected', label: 'Will install' },
  { id: 'available', label: 'Not selected' },
  { id: 'changes', label: 'Changes' },
]

type Layout = 'grid' | 'list'

const LAYOUT_KEY = 'workstation-manager.layout'

function storedLayout(): Layout {
  try {
    return localStorage.getItem(LAYOUT_KEY) === 'list' ? 'list' : 'grid'
  } catch {
    return 'grid'
  }
}

const initialParam = (name: string) => () => new URLSearchParams(window.location.search).get(name)

export default function App() {
  const [apps, setApps] = useState<Application[]>([])
  const [profiles, setProfiles] = useState<string[]>([])
  const [searches, setSearches] = useState<SavedSearch[]>([])
  const [profileName, setProfileName] = useState<string | null>(initialParam('profile'))
  const [profile, setProfile] = useState<Profile | null>(null)
  const [draft, setDraft] = useState<Set<string>>(new Set())
  const [query, setQuery] = useState('')
  const [view, setView] = useState<View>('all')
  const [layout, setLayout] = useState<Layout>(storedLayout)
  const [activeTags, setActiveTags] = useState<Set<string>>(new Set())
  const [activeKind, setActiveKind] = useState<string | null>(null)
  const [detailId, setDetailId] = useState<string | null>(null)
  const [runs, setRuns] = useState<RunSummary[]>([])
  // A run id or "latest"; when set, the main area shows that run's report
  const [runId, setRunId] = useState<string | null>(initialParam('run'))
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    Promise.all([api.applications(), api.profiles(), api.settings(), api.runs()])
      .then(([apps, profiles, settings, runs]) => {
        setApps(apps.sort((a, b) => a.name.localeCompare(b.name)))
        setProfiles(profiles)
        setSearches(settings.searches)
        setRuns(runs)
        setProfileName((current) => (current && profiles.includes(current) ? current : profiles[0] ?? null))
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  useEffect(() => {
    if (!profileName) return
    const url = new URL(window.location.href)
    url.searchParams.set('profile', profileName)
    window.history.replaceState(null, '', url)
    api
      .profile(profileName)
      .then((p) => {
        setProfile(p)
        setDraft(new Set(p.selected))
      })
      .catch((e: Error) => setError(e.message))
  }, [profileName])

  useEffect(() => {
    const url = new URL(window.location.href)
    if (runId) url.searchParams.set('run', runId)
    else url.searchParams.delete('run')
    window.history.replaceState(null, '', url)
  }, [runId])

  const refreshRuns = useCallback(() => api.runs().then(setRuns), [])
  const openLastRun = () => refreshRuns().then(() => setRunId('latest'))
  const reportId = runId === 'latest' ? runs[0]?.id : runId
  const showApps = () => setRunId(null)

  const byId = useMemo(() => new Map(apps.map((app) => [app.id, app])), [apps])
  const saved = useMemo(() => new Set(profile?.selected ?? []), [profile])
  const fundamentals = useMemo(() => new Set(profile?.fundamentals ?? []), [profile])
  const implied = useMemo(() => impliedBy(byId, new Set([...fundamentals, ...draft])), [byId, fundamentals, draft])
  const installs = useCallback(
    (id: string) => draft.has(id) || fundamentals.has(id) || implied.has(id),
    [draft, fundamentals, implied],
  )
  const added = useMemo(() => difference(draft, saved), [draft, saved])
  const removed = useMemo(() => difference(saved, draft), [draft, saved])
  const dirty = added.length > 0 || removed.length > 0
  const loading = !profile || profile.name !== profileName

  const changeOf = useCallback(
    (id: string) => (draft.has(id) && !saved.has(id) ? 'added' : !draft.has(id) && saved.has(id) ? 'removed' : null),
    [draft, saved],
  )

  const inView = useCallback(
    (app: Application) => {
      if (view === 'selected') return installs(app.id)
      if (view === 'available') return !installs(app.id)
      if (view === 'changes') return changeOf(app.id) !== null
      return true
    },
    [view, installs, changeOf],
  )

  const installed = useCallback((app: Application) => installs(app.id), [installs])
  const matching = useMemo(() => search(apps, query, installed).filter(inView), [apps, query, installed, inView])
  const tagged = useMemo(
    () => matching.filter((app) => [...activeTags].every((tag) => app.tags.includes(tag))),
    [matching, activeTags],
  )
  const visible = useMemo(
    () => (activeKind ? tagged.filter((app) => app.kind === activeKind) : tagged),
    [tagged, activeKind],
  )
  const kindCounts = useMemo(() => {
    const counts = new Map([...new Set(apps.map((app) => app.kind))].sort().map((kind) => [kind, 0]))
    for (const app of tagged) counts.set(app.kind, (counts.get(app.kind) ?? 0) + 1)
    return [...counts]
  }, [apps, tagged])
  const searchCounts = useMemo(
    () => new Map(searches.map(({ query }) => [query, search(apps, query, installed).length])),
    [apps, searches, installed],
  )
  const tagCounts = useMemo(() => {
    const counts = new Map<string, number>()
    for (const app of visible) for (const tag of app.tags) counts.set(tag, (counts.get(tag) ?? 0) + 1)
    for (const tag of activeTags) if (!counts.has(tag)) counts.set(tag, 0)
    return [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  }, [visible, activeTags])

  const viewCounts = useMemo(() => {
    const searched = search(apps, query, installed)
    return {
      all: searched.length,
      selected: searched.filter((app) => installs(app.id)).length,
      available: searched.filter((app) => !installs(app.id)).length,
      changes: added.length + removed.length,
    }
  }, [apps, query, installed, installs, added, removed])
  const installCount = draft.size + fundamentals.size + implied.size

  const toggle = useCallback((id: string) => {
    if (fundamentals.has(id)) return
    setDraft((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [fundamentals])

  const toggleTag = useCallback((tag: string) => {
    setActiveTags((current) => {
      const next = new Set(current)
      if (next.has(tag)) next.delete(tag)
      else next.add(tag)
      return next
    })
  }, [])

  const save = useCallback(async () => {
    if (!profile || !dirty || saving) return
    setSaving(true)
    try {
      const ordered = apps.filter((app) => draft.has(app.id)).map((app) => app.id)
      const updated = await api.saveProfile(profile.name, ordered)
      setProfile(updated)
      setDraft(new Set(updated.selected))
      setToast(`Saved profiles/${updated.name}.yaml`)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setSaving(false)
    }
  }, [apps, draft, dirty, profile, saving])

  const discard = () => setDraft(new Set(saved))

  const switchProfile = (name: string) => {
    if (dirty && !window.confirm(`Discard ${added.length + removed.length} unsaved change(s)?`)) return
    setProfileName(name)
  }

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const typing = e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement
      if ((e.key === '/' && !typing) || (e.key === 'k' && (e.metaKey || e.ctrlKey))) {
        e.preventDefault()
        searchRef.current?.focus()
        searchRef.current?.select()
      } else if (e.key === 's' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        void save()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [save])

  useEffect(() => {
    if (!dirty) return
    const onUnload = (e: BeforeUnloadEvent) => e.preventDefault()
    window.addEventListener('beforeunload', onUnload)
    return () => window.removeEventListener('beforeunload', onUnload)
  }, [dirty])

  useEffect(() => {
    if (!toast) return
    const timer = setTimeout(() => setToast(null), 2500)
    return () => clearTimeout(timer)
  }, [toast])

  useEffect(() => {
    try {
      localStorage.setItem(LAYOUT_KEY, layout)
    } catch {
      // Storage unavailable; layout just won't persist
    }
  }, [layout])

  const closeDetail = useCallback(() => setDetailId(null), [])
  const updateApp = useCallback(
    (updated: Application) => setApps((current) => current.map((app) => (app.id === updated.id ? updated : app))),
    [],
  )

  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col gap-6 overflow-y-auto border-r border-zinc-200 bg-white/60 p-5 backdrop-blur lg:flex dark:border-zinc-800 dark:bg-zinc-900/40">
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <Boxes className="size-4.5" />
          </div>
          <div>
            <p className="text-sm font-semibold leading-tight">Workstation</p>
            <p className="text-xs text-zinc-500">Application selector</p>
          </div>
        </div>

        {runs.length > 0 && (
          <button
            type="button"
            onClick={() => void openLastRun()}
            className={[
              'flex items-center gap-2.5 rounded-lg border px-3 py-2 text-left transition',
              runId
                ? 'border-indigo-300 bg-indigo-50 dark:border-indigo-500/40 dark:bg-indigo-500/15'
                : 'border-zinc-200 hover:border-indigo-300 hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-800',
            ].join(' ')}
          >
            <History className="size-4 shrink-0 text-zinc-500" />
            <span className="min-w-0">
              <span className="block text-sm font-medium">Last run report</span>
              <span className="block truncate text-xs text-zinc-500">
                <span className={STATUS_TEXT[runs[0].status]}>{runs[0].status}</span> · {relativeTime(runs[0].started)}
              </span>
            </span>
          </button>
        )}

        <section>
          <SidebarTitle>Profile</SidebarTitle>
          <div className="flex items-center gap-2">
            <select
              value={profileName ?? ''}
              onChange={(e) => switchProfile(e.target.value)}
              className="min-w-0 flex-1 rounded-lg border border-zinc-300 bg-white px-2 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-900"
            >
              {profiles.map((name) => (
                <option key={name}>{name}</option>
              ))}
            </select>
            {profile && <Count>{installCount}</Count>}
          </div>
        </section>

        <section>
          <SidebarTitle>Kind</SidebarTitle>
          <div className="space-y-0.5">
            {kindCounts.map(([kind, count]) => (
              <SidebarButton
                key={kind}
                active={activeKind === kind}
                onClick={() => {
                  showApps()
                  setActiveKind((current) => (current === kind ? null : kind))
                }}
              >
                <span>{kind}</span>
                <Count>{count}</Count>
              </SidebarButton>
            ))}
          </div>
        </section>

        {searches.length > 0 && (
          <section>
            <SidebarTitle>Searches</SidebarTitle>
            <div className="space-y-0.5">
              {searches.map((saved) => {
                const active = query.trim() === saved.query.trim()
                return (
                  <SidebarButton
                    key={saved.name}
                    active={active}
                    onClick={() => {
                      showApps()
                      setQuery(active ? '' : saved.query)
                    }}
                  >
                    <span title={saved.query} className={saved.builtin ? 'italic' : undefined}>
                      {saved.name}
                    </span>
                    <Count>{searchCounts.get(saved.query)}</Count>
                  </SidebarButton>
                )
              })}
            </div>
          </section>
        )}

        <section>
          <SidebarTitle>Show</SidebarTitle>
          <div className="space-y-0.5">
            {VIEWS.map(({ id, label }) => (
              <SidebarButton
                key={id}
                active={view === id}
                onClick={() => {
                  showApps()
                  setView(id)
                }}
              >
                <span>{label}</span>
                <Count>{viewCounts[id]}</Count>
              </SidebarButton>
            ))}
          </div>
        </section>

        {profile && (profile.missing.length > 0 || profile.inline.length > 0) && (
          <section className="space-y-2 rounded-lg border border-amber-300/70 bg-amber-50 p-3 text-xs text-amber-900 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-200">
            {profile.missing.length > 0 && (
              <p>
                <AlertTriangle className="mr-1 inline size-3.5" />
                Unknown refs kept as-is: <span className="font-mono">{profile.missing.join(', ')}</span>
              </p>
            )}
            {profile.inline.length > 0 && (
              <p>Inline entries kept as-is: {profile.inline.map((e) => e.label).join(', ')}</p>
            )}
          </section>
        )}

        <section>
          <div className="flex items-center justify-between">
            <SidebarTitle>Tags</SidebarTitle>
            {activeTags.size > 0 && (
              <button
                type="button"
                onClick={() => setActiveTags(new Set())}
                className="mb-2 text-xs text-indigo-600 hover:underline dark:text-indigo-400"
              >
                Clear
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-1">
            {tagCounts.map(([tag, count]) => (
              <button
                key={tag}
                type="button"
                onClick={() => {
                  showApps()
                  toggleTag(tag)
                }}
                className={[
                  'rounded-md px-1.5 py-0.5 text-xs transition',
                  activeTags.has(tag)
                    ? 'bg-indigo-600 text-white dark:bg-indigo-500'
                    : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700',
                ].join(' ')}
              >
                {tag} <span className="opacity-60">{count}</span>
              </button>
            ))}
          </div>
        </section>
      </aside>

      <main className="min-w-0 flex-1">
        {runId ? (
          <div className="mx-auto max-w-6xl px-4 pt-6 pb-32 sm:px-6">
            {reportId ? (
              <RunReport
                key={reportId}
                id={reportId}
                runs={runs}
                apps={byId}
                onSelectRun={setRunId}
                onOpenApp={setDetailId}
                onReload={refreshRuns}
                onClose={showApps}
              />
            ) : (
              <p className="py-24 text-center text-sm text-zinc-500">
                No runs yet. Run <code className="font-mono">ws update</code> in a terminal.
              </p>
            )}
          </div>
        ) : (
          <>
          <div className="sticky top-0 z-30 border-b border-zinc-200 bg-zinc-50/80 px-6 py-4 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/80">
            <div className="mx-auto flex max-w-6xl items-center gap-3">
              <select
                value={profileName ?? ''}
                onChange={(e) => switchProfile(e.target.value)}
                className="rounded-lg border border-zinc-300 bg-white px-2 py-2 text-sm lg:hidden dark:border-zinc-700 dark:bg-zinc-900"
              >
                {profiles.map((name) => (
                  <option key={name}>{name}</option>
                ))}
              </select>
              {runs.length > 0 && (
                <button
                  type="button"
                  title="Last run report"
                  onClick={() => void openLastRun()}
                  className="rounded-lg border border-zinc-300 p-2 text-zinc-500 lg:hidden dark:border-zinc-700"
                >
                  <History className="size-4" />
                </button>
              )}
              <label className="relative flex-1">
                <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-zinc-400" />
                <input
                  ref={searchRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Escape') {
                      setQuery('')
                      e.currentTarget.blur()
                    }
                  }}
                  placeholder="Fuzzy search name, id or description · #tag · kind:cli · is:archived"
                  className="w-full rounded-xl border border-zinc-300 bg-white py-2.5 pr-20 pl-10 text-sm shadow-sm outline-none transition placeholder:text-zinc-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/15 dark:border-zinc-700 dark:bg-zinc-900"
                />
                {query ? (
                  <button
                    type="button"
                    onClick={() => setQuery('')}
                    className="absolute top-1/2 right-3 -translate-y-1/2 rounded p-0.5 text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                  >
                    <X className="size-4" />
                  </button>
                ) : (
                  <kbd className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 rounded border border-zinc-200 px-1.5 font-mono text-[11px] text-zinc-400 dark:border-zinc-700">
                    /
                  </kbd>
                )}
              </label>
            </div>
            <div className="mx-auto mt-3 flex max-w-6xl items-center gap-2 text-xs text-zinc-500">
              <span>
                {visible.length} of {apps.length} applications
              </span>
              {activeKind && (
                <button
                  type="button"
                  onClick={() => setActiveKind(null)}
                  className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-1.5 py-0.5 text-white dark:bg-indigo-500"
                >
                  {activeKind} <X className="size-3" />
                </button>
              )}
              {[...activeTags].map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  className="inline-flex items-center gap-1 rounded-md bg-indigo-600 px-1.5 py-0.5 text-white dark:bg-indigo-500"
                >
                  {tag} <X className="size-3" />
                </button>
              ))}
              <div className="ml-auto flex rounded-lg border border-zinc-200 bg-white p-0.5 dark:border-zinc-700 dark:bg-zinc-900">
                <LayoutButton active={layout === 'grid'} title="Cards" onClick={() => setLayout('grid')}>
                  <LayoutGrid className="size-3.5" />
                </LayoutButton>
                <LayoutButton active={layout === 'list'} title="Compact list" onClick={() => setLayout('list')}>
                  <List className="size-3.5" />
                </LayoutButton>
              </div>
            </div>
          </div>

          <div className="mx-auto max-w-6xl px-6 pt-6 pb-32">
            {error && (
              <div className="mb-6 flex items-start gap-2 rounded-lg border border-rose-300 bg-rose-50 p-3 text-sm text-rose-800 dark:border-rose-500/40 dark:bg-rose-500/10 dark:text-rose-200">
                <AlertTriangle className="mt-0.5 size-4 shrink-0" />
                <span className="flex-1">{error}</span>
                <button type="button" onClick={() => setError(null)}>
                  <X className="size-4" />
                </button>
              </div>
            )}

            {loading && !error ? (
              <div className="flex justify-center py-24 text-zinc-400">
                <Loader2 className="size-6 animate-spin" />
              </div>
            ) : visible.length === 0 ? (
              <p className="py-24 text-center text-sm text-zinc-500">No applications match.</p>
            ) : (
              <div
                className={
                  layout === 'list'
                    ? 'divide-y divide-zinc-200 overflow-hidden rounded-xl border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800'
                    : 'grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3'
                }
              >
                {visible.map((app) => {
                  const Item = layout === 'list' ? AppRow : AppCard
                  return (
                    <Item
                      key={app.id}
                      app={app}
                      activeTags={activeTags}
                      state={{
                        selected: draft.has(app.id),
                        locked: fundamentals.has(app.id),
                        implied: implied.get(app.id) ?? [],
                        change: changeOf(app.id),
                      }}
                      onToggle={() => toggle(app.id)}
                      onDetails={() => setDetailId(app.id)}
                      onTag={toggleTag}
                    />
                  )
                })}
              </div>
            )}
          </div>
          </>
        )}
      </main>

      {dirty && !loading && (
        <div className="fixed inset-x-0 bottom-6 z-30 flex justify-center px-4">
          <div className="flex items-center gap-4 rounded-2xl border border-zinc-200 bg-white/90 py-2 pr-2 pl-5 shadow-xl backdrop-blur dark:border-zinc-700 dark:bg-zinc-900/90">
            <p className="text-sm">
              <span className="font-medium text-emerald-600 dark:text-emerald-400">+{added.length}</span>{' '}
              <span className="font-medium text-rose-600 dark:text-rose-400">−{removed.length}</span>{' '}
              <span className="text-zinc-500">
                unsaved in <span className="font-medium text-zinc-700 dark:text-zinc-200">{profile?.name}</span>
              </span>
            </p>
            <button
              type="button"
              onClick={() => setView('changes')}
              className="rounded-lg px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              Review
            </button>
            <button
              type="button"
              onClick={discard}
              className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              <RotateCcw className="size-4" /> Discard
            </button>
            <button
              type="button"
              onClick={() => void save()}
              disabled={saving}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 disabled:opacity-60"
            >
              {saving ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />} Save
              <kbd className="ml-1 rounded bg-white/20 px-1 font-mono text-[10px]">⌘S</kbd>
            </button>
          </div>
        </div>
      )}

      {toast && (
        <div className="fixed right-6 bottom-6 z-50 rounded-lg bg-zinc-900 px-4 py-2 text-sm text-white shadow-lg dark:bg-white dark:text-zinc-900">
          {toast}
        </div>
      )}

      {detailId && (
        <DetailPanel
          id={detailId}
          apps={byId}
          selected={draft.has(detailId)}
          locked={fundamentals.has(detailId)}
          impliedBy={implied.get(detailId) ?? []}
          onToggle={() => toggle(detailId)}
          onOpen={setDetailId}
          onUpdate={updateApp}
          onClose={closeDetail}
        />
      )}
    </div>
  )
}

function SidebarTitle({ children }: { children: ReactNode }) {
  return <h2 className="mb-2 text-[11px] font-semibold tracking-wider text-zinc-400 uppercase">{children}</h2>
}

function SidebarButton({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-sm transition',
        active
          ? 'bg-indigo-50 font-medium text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300'
          : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800',
      ].join(' ')}
    >
      {children}
    </button>
  )
}

function Count({ children }: { children: ReactNode }) {
  return <span className="text-xs tabular-nums text-zinc-400">{children}</span>
}

function LayoutButton({
  active,
  title,
  onClick,
  children,
}: {
  active: boolean
  title: string
  onClick: () => void
  children: ReactNode
}) {
  return (
    <button
      type="button"
      title={title}
      onClick={onClick}
      className={[
        'rounded-md p-1 transition',
        active
          ? 'bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-100'
          : 'text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200',
      ].join(' ')}
    >
      {children}
    </button>
  )
}
