import { Check, Link2, Lock, Trash2 } from 'lucide-react'
import type { Application } from '../api'
import { displayDescription } from '../selection'

export type CardState = {
  selected: boolean
  locked: boolean
  implied: string[]
  // Marked for uninstall in the profile
  uninstall: boolean
  // Unsaved: selection added or removed, or uninstall marked or kept (taken off the list)
  change: 'added' | 'removed' | 'marked' | 'kept' | null
}

type Variant = 'locked' | 'selected' | 'implied' | 'uninstall' | 'idle'

const CARD: Record<Variant, string> = {
  locked: 'border-zinc-300 bg-zinc-100/80 dark:border-zinc-700 dark:bg-zinc-800/50',
  selected: 'border-indigo-500/70 bg-indigo-50/70 shadow-sm dark:border-indigo-400/60 dark:bg-indigo-500/10',
  implied: 'border-dashed border-amber-400/80 bg-amber-50/50 dark:border-amber-400/50 dark:bg-amber-500/5',
  uninstall: 'border-dashed border-rose-300 bg-rose-50/40 dark:border-rose-500/40 dark:bg-rose-500/5',
  idle: 'border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900',
}

const ROW: Record<Variant, string> = {
  locked: 'bg-zinc-100/80 dark:bg-zinc-800/50',
  selected: 'bg-indigo-50/70 dark:bg-indigo-500/10',
  implied: 'bg-amber-50/50 dark:bg-amber-500/5',
  uninstall: 'bg-rose-50/40 dark:bg-rose-500/5',
  idle: 'bg-white hover:bg-zinc-50 dark:bg-zinc-900 dark:hover:bg-zinc-800/60',
}

const CHECKBOX: Record<Variant, string> = {
  locked: 'border-zinc-400 bg-zinc-400 text-white dark:border-zinc-500 dark:bg-zinc-600',
  selected: 'border-indigo-600 bg-indigo-600 text-white dark:border-indigo-400 dark:bg-indigo-500',
  implied: 'border-zinc-300 bg-white hover:border-indigo-400 dark:border-zinc-600 dark:bg-zinc-800',
  uninstall: 'border-rose-300 bg-white text-rose-500 hover:border-indigo-400 dark:border-rose-500/50 dark:bg-zinc-800',
  idle: 'border-zinc-300 bg-white hover:border-indigo-400 dark:border-zinc-600 dark:bg-zinc-800',
}

interface Props {
  app: Application
  state: CardState
  activeTags: Set<string>
  onToggle: () => void
  onDetails: () => void
  onTag: (tag: string) => void
}

function variantOf({ selected, locked, implied, uninstall }: CardState): Variant {
  if (locked) return 'locked'
  if (selected) return 'selected'
  if (implied.length > 0) return 'implied'
  return uninstall ? 'uninstall' : 'idle'
}

export function AppCard({ app, state, activeTags, onToggle, onDetails, onTag }: Props) {
  const variant = variantOf(state)

  return (
    <article
      onClick={onDetails}
      className={[
        'relative flex cursor-pointer flex-col gap-2 rounded-xl border p-4 transition',
        'hover:-translate-y-px hover:shadow-md',
        CARD[variant],
      ].join(' ')}
    >
      <div className="flex items-start gap-3">
        <Checkbox variant={variant} onToggle={onToggle} className="mt-0.5" />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate font-semibold">{app.name}</h3>
            <Badges app={app} state={state} />
          </div>
          <p className="truncate text-xs text-zinc-500 dark:text-zinc-400">
            <span className="font-mono">{app.id}</span> · {app.kind}
          </p>
        </div>
      </div>

      <p className="line-clamp-2 text-sm text-zinc-600 dark:text-zinc-300">{displayDescription(app)}</p>

      {variant === 'implied' && (
        <p className="flex items-center gap-1 text-xs text-amber-700 dark:text-amber-300">
          <Link2 className="size-3.5" />
          Required by {state.implied.join(', ')}
        </p>
      )}

      <div className="mt-auto flex flex-wrap gap-1 pt-1">
        <Tags tags={app.tags} activeTags={activeTags} onTag={onTag} />
      </div>
    </article>
  )
}

export function AppRow({ app, state, activeTags, onToggle, onDetails, onTag }: Props) {
  const variant = variantOf(state)

  return (
    <article
      onClick={onDetails}
      className={['flex cursor-pointer items-center gap-3 px-3 py-1.5 text-sm transition', ROW[variant]].join(
        ' ',
      )}
    >
      <Checkbox variant={variant} onToggle={onToggle} />
      <div className="flex w-56 shrink-0 items-center gap-2 overflow-hidden">
        <h3 className="truncate font-medium">{app.name}</h3>
        <Badges app={app} state={state} />
      </div>
      <p className="hidden w-48 shrink-0 truncate font-mono text-xs text-zinc-500 xl:block dark:text-zinc-400">
        {app.id}
      </p>
      <p className="hidden w-24 shrink-0 truncate text-xs text-zinc-500 lg:block dark:text-zinc-400">{app.kind}</p>
      <p className="min-w-0 flex-1 truncate text-zinc-600 dark:text-zinc-300">
        {variant === 'implied' ? (
          <span className="text-amber-700 dark:text-amber-300" title={`Required by ${state.implied.join(', ')}`}>
            <Link2 className="mr-1 inline size-3.5" />
            {state.implied.join(', ')} ·{' '}
          </span>
        ) : null}
        {displayDescription(app)}
      </p>
      <div className="hidden max-w-[35%] shrink-0 gap-1 overflow-hidden md:flex">
        <Tags tags={app.tags} activeTags={activeTags} onTag={onTag} />
      </div>
    </article>
  )
}

function Checkbox({ variant, onToggle, className = '' }: { variant: Variant; onToggle: () => void; className?: string }) {
  const locked = variant === 'locked'
  return (
    <button
      type="button"
      disabled={locked}
      title={
        locked ? 'Fundamental: always installed' : variant === 'uninstall' ? 'Marked for uninstall; tick to select again' : undefined
      }
      onClick={(e) => {
        e.stopPropagation()
        onToggle()
      }}
      className={[
        'flex size-5 shrink-0 items-center justify-center rounded-md border transition disabled:cursor-not-allowed',
        CHECKBOX[variant],
        className,
      ].join(' ')}
    >
      {locked ? (
        <Lock className="size-3" strokeWidth={3} />
      ) : variant === 'uninstall' ? (
        <Trash2 className="size-3" strokeWidth={2.5} />
      ) : (
        variant === 'selected' && <Check className="size-3.5" strokeWidth={3} />
      )}
    </button>
  )
}

const BADGE = 'shrink-0 rounded-full px-1.5 py-px text-[10px] font-semibold tracking-wide uppercase'

const CHANGE: Record<NonNullable<CardState['change']>, string> = {
  added: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300',
  removed: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
  marked: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
  kept: 'bg-zinc-200 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300',
}

function Badges({ app, state }: { app: Application; state: CardState }) {
  return (
    <>
      {state.locked && (
        <span className={`${BADGE} bg-zinc-200 text-zinc-600 dark:bg-zinc-700 dark:text-zinc-300`}>always</span>
      )}
      {state.uninstall && (
        <span className={`${BADGE} bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300`}>uninstall</span>
      )}
      {app.archived && (
        <span className={`${BADGE} bg-zinc-200 text-zinc-500 dark:bg-zinc-700 dark:text-zinc-400`}>archived</span>
      )}
      {app.deprecated && (
        <span className={`${BADGE} bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300`}>
          deprecated
        </span>
      )}
      {app.trial && (
        <span className={`${BADGE} bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300`}>trial</span>
      )}
      {state.change && <span className={`${BADGE} ${CHANGE[state.change]}`}>{state.change}</span>}
    </>
  )
}

function Tags({ tags, activeTags, onTag }: { tags: string[]; activeTags: Set<string>; onTag: (tag: string) => void }) {
  return tags.map((tag) => (
    <button
      key={tag}
      type="button"
      onClick={(e) => {
        e.stopPropagation()
        onTag(tag)
      }}
      className={[
        'shrink-0 rounded-md px-1.5 py-0.5 text-[11px] font-medium transition',
        activeTags.has(tag)
          ? 'bg-indigo-600 text-white dark:bg-indigo-500'
          : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700',
      ].join(' ')}
    >
      {tag}
    </button>
  ))
}
