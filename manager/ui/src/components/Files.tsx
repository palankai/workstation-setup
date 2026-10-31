import { ChevronRight, FileText } from 'lucide-react'
import { useState } from 'react'
import type { ApplicationDetail, StepKind } from '../api'
import { CodeView } from './CodeView'

const STEP_LABELS: Record<StepKind, { label: string; className: string }> = {
  brewfile: {
    label: 'brew bundle',
    className: 'bg-amber-100 text-amber-800 dark:bg-amber-500/15 dark:text-amber-300',
  },
  once: {
    label: 'first install only',
    className: 'bg-sky-100 text-sky-800 dark:bg-sky-500/15 dark:text-sky-300',
  },
  run: {
    label: 'every upgrade',
    className: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-300',
  },
  uninstall: {
    label: 'on uninstall',
    className: 'bg-rose-100 text-rose-800 dark:bg-rose-500/15 dark:text-rose-300',
  },
  generate: {
    label: 'generates files',
    className: 'bg-violet-100 text-violet-800 dark:bg-violet-500/15 dark:text-violet-300',
  },
}

export function Files({ detail }: { detail: ApplicationDetail }) {
  const steps = new Set(detail.steps.map((step) => step.file))
  const others = detail.files.filter((file) => !steps.has(file) && file !== 'README.md')

  return (
    <>
      <section>
        <SectionTitle>Install steps</SectionTitle>
        {detail.steps.length === 0 ? (
          <p className="text-sm text-zinc-500">No install steps.</p>
        ) : (
          <ol className="space-y-2">
            {detail.steps.map((step, index) => (
              <FileBlock key={step.file} id={detail.id} file={step.file} index={index + 1} kind={step.kind} open />
            ))}
          </ol>
        )}
      </section>

      {others.length > 0 && (
        <section>
          <SectionTitle>Supporting files</SectionTitle>
          <ul className="space-y-2">
            {others.map((file) => (
              <FileBlock key={file} id={detail.id} file={file} />
            ))}
          </ul>
        </section>
      )}
    </>
  )
}

function FileBlock({
  id,
  file,
  index,
  kind,
  open: initiallyOpen = false,
}: {
  id: string
  file: string
  index?: number
  kind?: StepKind
  open?: boolean
}) {
  const [open, setOpen] = useState(initiallyOpen)
  return (
    <li className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-zinc-50 dark:hover:bg-zinc-800/60"
      >
        <ChevronRight className={`size-4 shrink-0 text-zinc-400 transition ${open ? 'rotate-90' : ''}`} />
        {index !== undefined ? (
          <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-zinc-100 text-[11px] font-semibold text-zinc-600 tabular-nums dark:bg-zinc-800 dark:text-zinc-300">
            {index}
          </span>
        ) : (
          <FileText className="size-4 shrink-0 text-zinc-400" />
        )}
        <span className="min-w-0 flex-1 truncate font-mono text-xs">{file}</span>
        {kind && (
          <span className={`rounded-full px-2 py-px text-[10px] font-semibold ${STEP_LABELS[kind].className}`}>
            {STEP_LABELS[kind].label}
          </span>
        )}
      </button>
      {open && (
        <div className="border-t border-zinc-200 dark:border-zinc-800">
          <CodeView id={id} file={file} />
        </div>
      )}
    </li>
  )
}

function SectionTitle({ children }: { children: string }) {
  return <h3 className="mb-2 text-xs font-semibold tracking-wide text-zinc-500 uppercase">{children}</h3>
}
