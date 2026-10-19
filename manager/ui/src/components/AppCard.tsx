import { Check, Info, Link2, Lock } from 'lucide-react'
import type { Application } from '../api'
import { displayDescription } from '../selection'

export type CardState = {
  selected: boolean
  locked: boolean
  implied: string[]
  change: 'added' | 'removed' | null
}

type Variant = 'locked' | 'selected' | 'implied' | 'idle'

const CARD: Record<Variant, string> = {
  locked: 'border-zinc-300 bg-zinc-100/80 dark:border-zinc-700 dark:bg-zinc-800/50',
  selected: 'border-indigo-500/70 bg-indigo-50/70 shadow-sm dark:border-indigo-400/60 dark:bg-indigo-500/10',
  implied: 'border-dashed border-amber-400/80 bg-amber-50/50 dark:border-amber-400/50 dark:bg-amber-500/5',
  idle: 'border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900',
}

const CHECKBOX: Record<Variant, string> = {
  locked: 'border-zinc-400 bg-zinc-400 text-white dark:border-zinc-500 dark:bg-zinc-600',
  selected: 'border-indigo-600 bg-indigo-600 text-white dark:border-indigo-400 dark:bg-indigo-500',
  implied: 'border-zinc-300 bg-white group-hover:border-indigo-400 dark:border-zinc-600 dark:bg-zinc-800',
  idle: 'border-zinc-300 bg-white group-hover:border-indigo-400 dark:border-zinc-600 dark:bg-zinc-800',
}

interface Props {
  app: Application
  state: CardState
  activeTags: Set<string>
  onToggle: () => void
  onDetails: () => void
  onTag: (tag: string) => void
}

export function AppCard({ app, state, activeTags, onToggle, onDetails, onTag }: Props) {
  const { selected, locked, implied, change } = state
  const isImplied = !selected && !locked && implied.length > 0
  const variant: Variant = locked ? 'locked' : selected ? 'selected' : isImplied ? 'implied' : 'idle'

  return (
    <article
      onClick={locked ? onDetails : onToggle}
      title={locked ? 'Fundamental: always installed' : undefined}
      className={[
        'group relative flex cursor-pointer flex-col gap-2 rounded-xl border p-4 transition',
        'hover:-translate-y-px hover:shadow-md',
        CARD[variant],
      ].join(' ')}
    >
      <div className="flex items-start gap-3">
        <span
          className={[
            'mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-md border transition',
            CHECKBOX[variant],
          ].join(' ')}
        >
          {locked ? (
            <Lock className="size-3" strokeWidth={3} />
          ) : (
            selected && <Check className="size-3.5" strokeWidth={3} />
          )}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate font-semibold">{app.name}</h3>
            {locked && (
              <span className="rounded-full bg-zinc-200 px-1.5 py-px text-[10px] font-semibold tracking-wide text-zinc-600 uppercase dark:bg-zinc-700 dark:text-zinc-300">
                always
              </span>
            )}
            {change && (
              <span
                className={[
                  'rounded-full px-1.5 py-px text-[10px] font-semibold uppercase tracking-wide',
                  change === 'added'
                    ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300'
                    : 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
                ].join(' ')}
              >
                {change}
              </span>
            )}
          </div>
          <p className="truncate font-mono text-xs text-zinc-500 dark:text-zinc-400">{app.id}</p>
        </div>
        <button
          type="button"
          title="Details"
          onClick={(e) => {
            e.stopPropagation()
            onDetails()
          }}
          className="rounded-md p-1 text-zinc-400 opacity-0 transition hover:bg-zinc-100 hover:text-zinc-700 group-hover:opacity-100 focus:opacity-100 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
        >
          <Info className="size-4" />
        </button>
      </div>

      <p className="line-clamp-2 text-sm text-zinc-600 dark:text-zinc-300">{displayDescription(app)}</p>

      {isImplied && (
        <p className="flex items-center gap-1 text-xs text-amber-700 dark:text-amber-300">
          <Link2 className="size-3.5" />
          Required by {implied.join(', ')}
        </p>
      )}

      <div className="mt-auto flex flex-wrap gap-1 pt-1">
        {app.tags.map((tag) => (
          <button
            key={tag}
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              onTag(tag)
            }}
            className={[
              'rounded-md px-1.5 py-0.5 text-[11px] font-medium transition',
              activeTags.has(tag)
                ? 'bg-indigo-600 text-white dark:bg-indigo-500'
                : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700',
            ].join(' ')}
          >
            {tag}
          </button>
        ))}
      </div>
    </article>
  )
}
