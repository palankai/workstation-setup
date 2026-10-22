import { Check, ChevronRight, Loader2, Minus, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api, type HistoryStep, type Run, type RunStep, type RunSummary, type StepStatus } from '../api'

const STATUS: Record<StepStatus | RunSummary['status'], string> = {
  ok: 'text-emerald-600 dark:text-emerald-400',
  failed: 'text-rose-600 dark:text-rose-400',
  skipped: 'text-zinc-400',
  running: 'text-sky-600 dark:text-sky-400',
  interrupted: 'text-amber-600 dark:text-amber-400',
}

const formatTime = (iso: string) => new Date(iso).toLocaleString()

function StatusIcon({ status }: { status: StepStatus }) {
  const Icon = status === 'ok' ? Check : status === 'failed' ? X : Minus
  return <Icon className={`size-4 shrink-0 ${STATUS[status]}`} strokeWidth={2.5} />
}

function stepLabel(step: RunStep, withApp: boolean) {
  if (step.app === null) return step.step
  if (step.kind === 'app') return step.app
  return withApp ? `${step.app} · ${step.step}` : step.step
}

/** One executed step; failed steps open with their output shown. */
function StepEntry({ step, run, withApp, note }: { step: RunStep; run: string; withApp: boolean; note?: string }) {
  const [open, setOpen] = useState(step.status === 'failed')
  const [output, setOutput] = useState<string>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    if (!open || !step.output || output !== undefined) return
    api
      .runOutput(run, step.output)
      .then(setOutput)
      .catch((e: Error) => setError(e.message))
  }, [open, run, step.output, output])

  return (
    <li className="rounded-lg border border-zinc-200 dark:border-zinc-800">
      <button
        type="button"
        disabled={!step.output}
        onClick={() => setOpen((current) => !current)}
        className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm disabled:cursor-default"
      >
        <ChevronRight
          className={['size-4 shrink-0 text-zinc-400 transition', open ? 'rotate-90' : '', step.output ? '' : 'invisible'].join(' ')}
        />
        <StatusIcon status={step.status} />
        <span className="min-w-0 flex-1 truncate font-mono text-xs">{stepLabel(step, withApp)}</span>
        {step.reason && <span className="truncate text-xs text-zinc-500">{step.reason}</span>}
        {step.status === 'failed' && step.exit_code !== null && (
          <span className="text-xs text-rose-600 dark:text-rose-400">exit {step.exit_code}</span>
        )}
        {note && <span className="shrink-0 text-xs text-zinc-400">{note}</span>}
      </button>
      {open && step.output && (
        <div className="border-t border-zinc-200 dark:border-zinc-800">
          {error ? (
            <p className="p-3 text-sm text-rose-600">{error}</p>
          ) : output === undefined ? (
            <Loader2 className="m-3 size-4 animate-spin text-zinc-400" />
          ) : (
            <pre className="max-h-96 overflow-auto bg-zinc-50 p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap dark:bg-zinc-950">
              {output.trim() || '(no output)'}
            </pre>
          )}
        </div>
      )}
    </li>
  )
}

/** Executed steps of one application across runs, latest first. */
export function AppHistory({ id }: { id: string }) {
  const [history, setHistory] = useState<{ id: string; steps: HistoryStep[] }>()

  useEffect(() => {
    let cancelled = false
    api
      .history(id)
      .then((steps) => !cancelled && setHistory({ id, steps }))
      .catch(() => !cancelled && setHistory({ id, steps: [] }))
    return () => {
      cancelled = true
    }
  }, [id])

  if (history?.id !== id || history.steps.length === 0) return null
  return (
    <section>
      <h3 className="mb-2 text-xs font-semibold tracking-wide text-zinc-500 uppercase">Run history</h3>
      <ol className="space-y-1.5">
        {history.steps.slice(0, 30).map((step, index) => (
          <StepEntry
            key={`${step.run}-${index}`}
            step={step}
            run={step.run}
            withApp={false}
            note={formatTime(step.started)}
          />
        ))}
      </ol>
    </section>
  )
}

export function RunsPanel({ onClose }: { onClose: () => void }) {
  const [runs, setRuns] = useState<RunSummary[]>()
  const [selected, setSelected] = useState<string>()
  const [run, setRun] = useState<Run>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    api
      .runs()
      .then((runs) => {
        setRuns(runs)
        setSelected((current) => current ?? runs[0]?.id)
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  useEffect(() => {
    if (!selected) return
    api
      .run(selected)
      .then(setRun)
      .catch((e: Error) => setError(e.message))
  }, [selected])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const counts = (steps: RunStep[], status: StepStatus) => steps.filter((s) => s.status === status).length

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-zinc-950/30 backdrop-blur-[2px]" onClick={onClose} />
      <aside className="relative flex h-full w-full max-w-4xl flex-col overflow-hidden border-l border-zinc-200 bg-white shadow-2xl dark:border-zinc-800 dark:bg-zinc-900">
        <header className="flex items-center gap-4 border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <h2 className="flex-1 text-xl font-semibold">Runs</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
          >
            <X className="size-5" />
          </button>
        </header>
        {error && <p className="px-6 py-3 text-sm text-rose-600">{error}</p>}
        {runs?.length === 0 && (
          <p className="px-6 py-12 text-center text-sm text-zinc-500">
            No runs yet. Run <code className="font-mono">ws update</code> in a terminal.
          </p>
        )}
        <div className="flex min-h-0 flex-1 flex-col sm:flex-row">
          {runs && runs.length > 0 && (
            <ol className="max-h-48 shrink-0 overflow-y-auto border-b border-zinc-200 sm:max-h-none sm:w-64 sm:border-r sm:border-b-0 dark:border-zinc-800">
              {runs.map((summary) => (
                <li key={summary.id}>
                  <button
                    type="button"
                    onClick={() => setSelected(summary.id)}
                    className={[
                      'w-full px-4 py-2 text-left text-sm',
                      summary.id === selected
                        ? 'bg-indigo-50 dark:bg-indigo-500/15'
                        : 'hover:bg-zinc-50 dark:hover:bg-zinc-800/60',
                    ].join(' ')}
                  >
                    <span className="block">{formatTime(summary.started)}</span>
                    <span className="block truncate text-xs text-zinc-500">
                      <span className={STATUS[summary.status]}>{summary.status}</span> · {summary.profile} ·{' '}
                      <span className="font-mono">{summary.command.join(' ')}</span>
                    </span>
                  </button>
                </li>
              ))}
            </ol>
          )}
          {run && run.id === selected && (
            <div className="min-w-0 flex-1 space-y-4 overflow-y-auto p-6">
              <p className="text-sm text-zinc-600 dark:text-zinc-300">
                <span className={`font-medium ${STATUS[run.status]}`}>{run.status}</span> ·{' '}
                {counts(run.steps, 'ok')} ok · {counts(run.steps, 'failed')} failed · {counts(run.steps, 'skipped')}{' '}
                skipped
                <span className="block font-mono text-xs text-zinc-500">{run.command.join(' ')}</span>
              </p>
              <ol className="space-y-1.5">
                {run.steps.map((step, index) => (
                  <StepEntry key={index} step={step} run={run.id} withApp />
                ))}
              </ol>
            </div>
          )}
        </div>
      </aside>
    </div>
  )
}
