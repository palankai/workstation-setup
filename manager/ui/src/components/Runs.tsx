import { Check, ChevronRight, Loader2, Minus, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api, type HistoryStep, type RunStep, type StepStatus } from '../api'
import { STATUS_TEXT, formatDuration, formatTime, secondsBetween } from '../runs'

export function StatusIcon({ status }: { status: StepStatus }) {
  const Icon = status === 'ok' ? Check : status === 'failed' ? X : Minus
  return <Icon className={`size-4 shrink-0 ${STATUS_TEXT[status]}`} strokeWidth={2.5} />
}

/** A step's captured terminal output, loaded when shown. */
export function StepOutput({ run, step }: { run: string; step: RunStep }) {
  const [output, setOutput] = useState<string>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    if (!step.output) return
    api
      .runOutput(run, step.output)
      .then(setOutput)
      .catch((e: Error) => setError(e.message))
  }, [run, step.output])

  if (!step.output) return step.reason ? <p className="px-3 py-2 text-sm text-zinc-500">{step.reason}</p> : null
  if (error) return <p className="p-3 text-sm text-rose-600">{error}</p>
  if (output === undefined) return <Loader2 className="m-3 size-4 animate-spin text-zinc-400" />
  return (
    <pre className="max-h-[32rem] overflow-auto bg-zinc-50 p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap dark:bg-zinc-950">
      {output.trim() || '(no output)'}
    </pre>
  )
}

/** One step of the app panel's history; failed steps open with their output shown. */
function HistoryEntry({ step }: { step: HistoryStep }) {
  const [open, setOpen] = useState(step.status === 'failed')
  return (
    <li className="rounded-lg border border-zinc-200 dark:border-zinc-800">
      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm"
      >
        <ChevronRight className={`size-4 shrink-0 text-zinc-400 transition ${open ? 'rotate-90' : ''}`} />
        <StatusIcon status={step.status} />
        <span className="min-w-0 flex-1 truncate font-mono text-xs">{step.step === '*' ? (step.kind === 'uninstall' ? 'uninstall' : 'skipped') : step.step}</span>
        {step.status === 'failed' && (
          <span className="text-xs text-rose-600 dark:text-rose-400">{step.reason ?? `exit ${step.exit_code}`}</span>
        )}
        <span className="shrink-0 text-xs text-zinc-400">
          {formatTime(step.started)} · {formatDuration(secondsBetween(step.started, step.finished))}
        </span>
      </button>
      {open && (
        <div className="border-t border-zinc-200 dark:border-zinc-800">
          <StepOutput run={step.run} step={step} />
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
        {history.steps.map((step, index) => (
          <HistoryEntry key={`${step.run}-${index}`} step={step} />
        ))}
      </ol>
    </section>
  )
}
