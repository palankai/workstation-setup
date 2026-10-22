import { Archive, Check, ExternalLink, Link2, Lock, OctagonAlert, Plus, Trash2, X } from 'lucide-react'
import { type ReactNode, useEffect, useState } from 'react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api, type Application, type ApplicationDetail } from '../api'
import { displayDescription } from '../selection'
import { Files } from './Files'
import { AppHistory } from './Runs'

interface Props {
  id: string
  apps: Map<string, Application>
  selected: boolean
  locked: boolean
  impliedBy: string[]
  marked: boolean
  // What else being installed needs this app, so it can't be uninstalled
  neededBy: string[]
  onToggle: () => void
  onUninstall: (uninstall: boolean) => void
  onOpen: (id: string) => void
  onUpdate: (app: Application) => void
  onClose: () => void
}

function isRelative(url: string) {
  return !/^([a-z][a-z0-9+.-]*:|\/|#)/i.test(url)
}

/** Drop the title, description and homepage blocks already shown in the header. */
function readmeBody(readme: string, app: Application) {
  const shown = new Set([`# ${app.name}`, app.description, `${app.description}.`, `<${app.homepage}>`])
  return readme
    .split(/\n{2,}/)
    .filter((block) => !shown.has(block.trim()))
    .join('\n\n')
}

export function DetailPanel({
  id,
  apps,
  selected,
  locked,
  impliedBy,
  marked,
  neededBy,
  onToggle,
  onUninstall,
  onOpen,
  onUpdate,
  onClose,
}: Props) {
  const [loaded, setLoaded] = useState<{ id: string; detail?: ApplicationDetail; error?: string }>()
  const detail = loaded?.id === id ? loaded.detail : undefined
  const error = loaded?.id === id ? loaded.error : undefined
  const requiredBy = [...apps.values()].filter((app) => app.dependencies.includes(id))

  useEffect(() => {
    let cancelled = false
    api
      .application(id)
      .then((detail) => !cancelled && setLoaded({ id, detail }))
      .catch((e: Error) => !cancelled && setLoaded({ id, error: e.message }))
    return () => {
      cancelled = true
    }
  }, [id])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const [flagError, setFlagError] = useState<string>()
  const setFlag = (flag: 'deprecated' | 'archived', value: boolean) =>
    api
      .updateFlags(id, { [flag]: value })
      .then((updated) => {
        setFlagError(undefined)
        onUpdate(updated)
      })
      .catch((e: Error) => setFlagError(e.message))

  const app = apps.get(id)
  if (!app) return null

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-zinc-950/30 backdrop-blur-[2px]" onClick={onClose} />
      <aside className="relative flex h-full w-full max-w-3xl flex-col overflow-hidden border-l border-zinc-200 bg-white shadow-2xl dark:border-zinc-800 dark:bg-zinc-900">
        <header className="flex items-start gap-4 border-b border-zinc-200 p-6 dark:border-zinc-800">
          <div className="min-w-0 flex-1">
            <h2 className="text-xl font-semibold">{app.name}</h2>
            <p className="font-mono text-sm text-zinc-500 dark:text-zinc-400">{app.id}</p>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">{displayDescription(app)}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1.5 text-zinc-400 hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-200"
          >
            <X className="size-5" />
          </button>
        </header>

        <div className="flex-1 space-y-6 overflow-y-auto p-6">
          <div className="flex flex-wrap items-center gap-2">
            {locked ? (
              <span className="inline-flex items-center gap-1.5 rounded-lg bg-zinc-100 px-3 py-1.5 text-sm font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                <Lock className="size-4" /> Always installed
              </span>
            ) : (
              <button
                type="button"
                onClick={onToggle}
                className={[
                  'inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition',
                  selected
                    ? 'bg-indigo-600 text-white hover:bg-indigo-500'
                    : 'border border-zinc-300 hover:border-indigo-400 hover:text-indigo-600 dark:border-zinc-700 dark:hover:text-indigo-300',
                ].join(' ')}
              >
                {selected ? <Check className="size-4" /> : <Plus className="size-4" />}
                {selected ? 'Selected' : 'Select'}
              </button>
            )}
            {!locked && (
              <FlagButton
                active={marked}
                disabled={!marked && neededBy.length > 0}
                icon={<Trash2 className="size-4" />}
                label={marked ? 'Uninstalling' : 'Uninstall'}
                title={
                  marked
                    ? 'Every update uninstalls it until cleared; click to keep it (stays unselected)'
                    : neededBy.length > 0
                      ? `Needed by ${neededBy.join(', ')}`
                      : 'Deselect and uninstall on every update until cleared'
                }
                activeClass="border-rose-300 bg-rose-50 text-rose-700 dark:border-rose-500/40 dark:bg-rose-500/15 dark:text-rose-300"
                onClick={() => onUninstall(!marked)}
              />
            )}
            {app.homepage && (
              <a
                href={app.homepage}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                <ExternalLink className="size-4" /> Homepage
              </a>
            )}
            <FlagButton
              active={app.deprecated}
              icon={<OctagonAlert className="size-4" />}
              label={app.deprecated ? 'Deprecated' : 'Deprecate'}
              title={app.deprecated ? 'Undeprecate' : 'Mark as deprecated'}
              activeClass="border-orange-300 bg-orange-50 text-orange-700 dark:border-orange-500/40 dark:bg-orange-500/15 dark:text-orange-300"
              onClick={() => void setFlag('deprecated', !app.deprecated)}
            />
            <FlagButton
              active={app.archived}
              icon={<Archive className="size-4" />}
              label={app.archived ? 'Archived' : 'Archive'}
              title={app.archived ? 'Unarchive' : 'Archive: hide from searches unless is:archived'}
              activeClass="border-zinc-400 bg-zinc-100 text-zinc-700 dark:border-zinc-500 dark:bg-zinc-800 dark:text-zinc-200"
              onClick={() => void setFlag('archived', !app.archived)}
            />
            <span className="ml-auto text-right font-mono text-xs text-zinc-400">
              applications/{app.folder}
              <span className="block" title="Install order among apps whose dependencies are met; lower goes first">
                order {app.order}
              </span>
            </span>
          </div>

          {flagError && <p className="text-sm text-rose-600">{flagError}</p>}

          {!selected && !locked && impliedBy.length > 0 && (
            <p className="flex items-center gap-1.5 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800 dark:bg-amber-500/10 dark:text-amber-200">
              <Link2 className="size-4" /> Installed anyway as a dependency of {impliedBy.join(', ')}
            </p>
          )}

          <Relations title="Depends on" ids={app.dependencies} apps={apps} onOpen={onOpen} />
          <Relations title="Required by" ids={requiredBy.map((a) => a.id)} apps={apps} onOpen={onOpen} />

          {error && <p className="text-sm text-rose-600">{error}</p>}
          {detail && (
            <>
              <article className="prose prose-sm prose-zinc max-w-none dark:prose-invert prose-code:before:content-none prose-code:after:content-none prose-pre:bg-zinc-100 prose-pre:text-zinc-800 dark:prose-pre:bg-zinc-800 dark:prose-pre:text-zinc-100">
                <Markdown
                  remarkPlugins={[remarkGfm]}
                  urlTransform={(url) => (isRelative(url) ? api.fileUrl(id, url) : url)}
                  components={{
                    a: (props) => <a {...props} target="_blank" rel="noreferrer" />,
                  }}
                >
                  {readmeBody(detail.readme, app)}
                </Markdown>
              </article>

              <Files detail={detail} />
            </>
          )}

          <AppHistory id={id} />
        </div>
      </aside>
    </div>
  )
}

function FlagButton({
  active,
  disabled = false,
  icon,
  label,
  title,
  activeClass,
  onClick,
}: {
  active: boolean
  disabled?: boolean
  icon: ReactNode
  label: string
  title: string
  activeClass: string
  onClick: () => void
}) {
  return (
    <button
      type="button"
      title={title}
      aria-pressed={active}
      disabled={disabled}
      onClick={onClick}
      className={[
        'inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition disabled:cursor-not-allowed disabled:opacity-50',
        active
          ? activeClass
          : 'border-zinc-200 text-zinc-500 hover:border-zinc-400 hover:text-zinc-700 dark:border-zinc-700 dark:hover:text-zinc-200',
      ].join(' ')}
    >
      {icon}
      {label}
    </button>
  )
}

function Relations({
  title,
  ids,
  apps,
  onOpen,
}: {
  title: string
  ids: string[]
  apps: Map<string, Application>
  onOpen: (id: string) => void
}) {
  if (!ids.length) return null
  return (
    <section>
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">{title}</h3>
      <div className="flex flex-wrap gap-1.5">
        {ids.map((id) => (
          <button
            key={id}
            type="button"
            onClick={() => onOpen(id)}
            className="rounded-md border border-zinc-200 px-2 py-1 text-sm hover:border-indigo-400 hover:text-indigo-600 dark:border-zinc-700 dark:hover:text-indigo-300"
          >
            {apps.get(id)?.name ?? id}
          </button>
        ))}
      </div>
    </section>
  )
}
