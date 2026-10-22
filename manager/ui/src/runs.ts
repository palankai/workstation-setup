import type { RunStep, RunSummary, StepStatus } from './api'

export const STATUS_TEXT: Record<StepStatus | RunSummary['status'], string> = {
  ok: 'text-emerald-600 dark:text-emerald-400',
  failed: 'text-rose-600 dark:text-rose-400',
  skipped: 'text-zinc-400',
  running: 'text-sky-600 dark:text-sky-400',
  interrupted: 'text-amber-600 dark:text-amber-400',
}

export const formatTime = (iso: string) => new Date(iso).toLocaleString()

export const secondsBetween = (start: string, end: string | null) =>
  end ? Math.max(0, (Date.parse(end) - Date.parse(start)) / 1000) : 0

export function formatDuration(seconds: number) {
  if (seconds < 60) return `${Math.round(seconds)}s`
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`
}

const RELATIVE = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' })

export function relativeTime(iso: string) {
  const minutes = Math.round((Date.parse(iso) - Date.now()) / 60000)
  if (Math.abs(minutes) < 60) return RELATIVE.format(minutes, 'minute')
  if (Math.abs(minutes) < 60 * 24) return RELATIVE.format(Math.round(minutes / 60), 'hour')
  return RELATIVE.format(Math.round(minutes / 60 / 24), 'day')
}

/** One line of the report: an application's steps, or a run-wide step such as `brew update`. */
export interface StepGroup {
  key: string
  app: string | null
  label: string
  steps: RunStep[]
  status: StepStatus
  seconds: number
}

export function groupSteps(steps: RunStep[]): StepGroup[] {
  const groups = new Map<string, RunStep[]>()
  for (const step of steps) {
    const key = step.app ?? `run:${step.step}`
    groups.set(key, [...(groups.get(key) ?? []), step])
  }
  return [...groups].map(([key, steps]) => ({
    key,
    app: steps[0].app,
    label: steps[0].app ?? steps[0].step,
    steps,
    status: steps.some((s) => s.status === 'failed')
      ? 'failed'
      : steps.every((s) => s.status === 'skipped')
        ? 'skipped'
        : 'ok',
    seconds: steps.reduce((total, s) => total + secondsBetween(s.started, s.finished), 0),
  }))
}
