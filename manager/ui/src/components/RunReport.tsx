import { ArrowLeft, ChevronRight, ChevronsDownUp, ChevronsUpDown, Loader2, PanelRightOpen, RefreshCw } from 'lucide-react'
import { type ReactNode, useEffect, useMemo, useState } from 'react'
import { api, type Application, type Run, type RunSummary, type StepStatus } from '../api'
import { STATUS_TEXT, formatDuration, formatTime, groupSteps, secondsBetween, type StepGroup } from '../runs'
import { StatusIcon, StepOutput } from './Runs'

type Filter = 'all' | StepStatus

const FILTERS: { id: Filter; label: string; active: string }[] = [
  { id: 'failed', label: 'Failed', active: 'bg-rose-600 text-white dark:bg-rose-500' },
  { id: 'skipped', label: 'Skipped', active: 'bg-zinc-600 text-white dark:bg-zinc-500' },
  { id: 'all', label: 'All', active: 'bg-zinc-800 text-white dark:bg-zinc-200 dark:text-zinc-900' },
  { id: 'ok', label: 'OK', active: 'bg-emerald-600 text-white dark:bg-emerald-500' },
]

const BAR: Record<StepStatus, string> = {
  ok: 'border-l-emerald-500',
  failed: 'border-l-rose-500',
  skipped: 'border-l-zinc-300 dark:border-l-zinc-600',
}

interface Props {
  id: string
  runs: RunSummary[]
  apps: Map<string, Application>
  onSelectRun: (id: string) => void
  onOpenApp: (id: string) => void
  onReload: () => void
  onClose: () => void
}

export function RunReport({ id, runs, apps, onSelectRun, onOpenApp, onReload, onClose }: Props) {
  const [loaded, setLoaded] = useState<{ run?: Run; error?: string }>()
  const [reload, setReload] = useState(0)
  const [filter, setFilter] = useState<Filter>('all')
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  useEffect(() => {
    let cancelled = false
    api
      .run(id)
      .then((run) => !cancelled && setLoaded({ run }))
      .catch((e: Error) => !cancelled && setLoaded({ error: e.message }))
    return () => {
      cancelled = true
    }
  }, [id, reload])

  const run = loaded?.run
  const groups = useMemo(() => (run ? groupSteps(run.steps) : []), [run])
  const counts = useMemo(() => {
    const counts: Record<Filter, number> = { all: groups.length, ok: 0, failed: 0, skipped: 0 }
    for (const group of groups) counts[group.status]++
    return counts
  }, [groups])
  const visible = filter === 'all' ? groups : groups.filter((group) => group.status === filter)

  const toggle = (key: string) =>
    setExpanded((current) => {
      const next = new Set(current)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={onClose}
          className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
        >
          <ArrowLeft className="size-4" /> Applications
        </button>
        <h1 className="mr-auto text-lg font-semibold">Run report</h1>
        <select
          value={id}
          onChange={(e) => onSelectRun(e.target.value)}
          className="max-w-full rounded-lg border border-zinc-300 bg-white px-2 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-900"
        >
          {runs.map((summary) => (
            <option key={summary.id} value={summary.id}>
              {formatTime(summary.started)} · {summary.status} · {summary.command.join(' ')}
            </option>
          ))}
        </select>
        <button
          type="button"
          title="Reload"
          onClick={() => {
            onReload()
            setReload((n) => n + 1)
          }}
          className="rounded-lg p-2 text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
        >
          <RefreshCw className="size-4" />
        </button>
      </div>

      {loaded?.error && <p className="text-sm text-rose-600">{loaded.error}</p>}
      {!loaded && <Loader2 className="mx-auto size-6 animate-spin text-zinc-400" />}

      {run && (
        <>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
            <Stat label="Status">
              <span className={STATUS_TEXT[run.status]}>{run.status}</span>
            </Stat>
            <Stat label="Started">{formatTime(run.started)}</Stat>
            <Stat label="Duration">{formatDuration(secondsBetween(run.started, run.finished))}</Stat>
            <Stat label="Profile">{run.profile}</Stat>
            <Stat label="Steps">{run.steps.length}</Stat>
            <Stat label="Failed / skipped">
              <span className={counts.failed ? STATUS_TEXT.failed : undefined}>{counts.failed}</span> /{' '}
              {counts.skipped}
            </Stat>
          </div>
          <p className="truncate font-mono text-xs text-zinc-500">ws {run.command.join(' ')}</p>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex flex-wrap gap-1">
              {FILTERS.map(({ id, label, active }) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => setFilter(id)}
                  className={[
                    'rounded-lg px-3 py-1 text-sm transition',
                    filter === id
                      ? active
                      : 'border border-zinc-200 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-800',
                  ].join(' ')}
                >
                  {label} <span className="opacity-70">{counts[id]}</span>
                </button>
              ))}
            </div>
            <div className="ml-auto flex gap-1">
              <ToolbarButton onClick={() => setExpanded(new Set(visible.map((g) => g.key)))}>
                <ChevronsUpDown className="size-4" /> Expand all
              </ToolbarButton>
              <ToolbarButton onClick={() => setExpanded(new Set())}>
                <ChevronsDownUp className="size-4" /> Collapse all
              </ToolbarButton>
            </div>
          </div>

          {visible.length === 0 ? (
            <p className="py-12 text-center text-sm text-zinc-500">Nothing here.</p>
          ) : (
            <ol className="space-y-1.5">
              {visible.map((group) => (
                <GroupRow
                  key={group.key}
                  run={run.id}
                  group={group}
                  name={group.app ? (apps.get(group.app)?.name ?? group.app) : group.label}
                  open={expanded.has(group.key)}
                  onToggle={() => toggle(group.key)}
                  onOpenApp={group.app && apps.has(group.app) ? () => onOpenApp(group.app!) : undefined}
                />
              ))}
            </ol>
          )}
        </>
      )}
    </div>
  )
}

function GroupRow({
  run,
  group,
  name,
  open,
  onToggle,
  onOpenApp,
}: {
  run: string
  group: StepGroup
  name: string
  open: boolean
  onToggle: () => void
  onOpenApp?: () => void
}) {
  const failed = group.steps.filter((s) => s.status === 'failed')
  const summary =
    group.status === 'skipped'
      ? (group.steps[0].reason ?? 'skipped')
      : failed.length
        ? `failed: ${failed.map((s) => `${s.step} (exit ${s.exit_code})`).join(', ')}`
        : `${group.steps.length} step${group.steps.length === 1 ? '' : 's'}`

  return (
    <li
      className={`overflow-hidden rounded-lg border border-l-4 border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900 ${BAR[group.status]}`}
    >
      <div onClick={onToggle} className="flex cursor-pointer items-center gap-2 px-3 py-1.5 text-sm">
        <ChevronRight className={`size-4 shrink-0 text-zinc-400 transition ${open ? 'rotate-90' : ''}`} />
        <StatusIcon status={group.status} />
        <span className={`truncate font-medium ${group.app ? '' : 'font-mono text-xs'}`}>{name}</span>
        {onOpenApp && (
          <button
            type="button"
            title="Open application"
            onClick={(e) => {
              e.stopPropagation()
              onOpenApp()
            }}
            className="shrink-0 rounded p-0.5 text-zinc-400 hover:bg-zinc-100 hover:text-indigo-600 dark:hover:bg-zinc-800 dark:hover:text-indigo-300"
          >
            <PanelRightOpen className="size-4" />
          </button>
        )}
        <span
          className={`min-w-0 flex-1 truncate text-xs ${failed.length ? STATUS_TEXT.failed : 'text-zinc-500'}`}
        >
          {summary}
        </span>
        <span className="shrink-0 text-xs tabular-nums text-zinc-400">{formatDuration(group.seconds)}</span>
      </div>
      {open &&
        group.steps.map((step, index) => (
          <div key={index} className="border-t border-zinc-200 dark:border-zinc-800">
            {group.app && step.kind !== 'app' && (
              <div className="flex items-center gap-2 px-3 py-1 text-xs text-zinc-500">
                <StatusIcon status={step.status} />
                <span className="font-mono">{step.step}</span>
                <span>{step.kind}</span>
                {step.status === 'failed' && <span className={STATUS_TEXT.failed}>exit {step.exit_code}</span>}
                <span className="ml-auto tabular-nums">{formatDuration(secondsBetween(step.started, step.finished))}</span>
              </div>
            )}
            <StepOutput run={run} step={step} />
          </div>
        ))}
    </li>
  )
}

function Stat({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900">
      <p className="text-[11px] font-semibold tracking-wider text-zinc-400 uppercase">{label}</p>
      <p className="truncate text-sm font-medium">{children}</p>
    </div>
  )
}

function ToolbarButton({ onClick, children }: { onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
    >
      {children}
    </button>
  )
}
