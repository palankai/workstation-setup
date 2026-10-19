import { Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import { highlight } from '../highlight'

const MAX_SIZE = 256 * 1024
const IMAGE = /\.(png|jpe?g|gif|svg|webp)$/i

interface Props {
  id: string
  file: string
}

type Loaded = { key: string; html?: string; empty?: boolean; error?: string }

export function CodeView({ id, file }: Props) {
  const key = `${id}/${file}`
  const [loaded, setLoaded] = useState<Loaded>()
  const current = loaded?.key === key ? loaded : undefined

  useEffect(() => {
    if (IMAGE.test(file)) return
    let cancelled = false
    const done = (result: Omit<Loaded, 'key'>) => !cancelled && setLoaded({ key, ...result })
    fetch(api.fileUrl(id, file))
      .then(async (response) => {
        if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
        const code = await response.text()
        if (code.length > MAX_SIZE) return done({ error: 'File is too large to preview' })
        if (!code.trim()) return done({ empty: true })
        done({ html: await highlight(file, code.replace(/\n$/, '')) })
      })
      .catch((e: Error) => done({ error: e.message }))
    return () => {
      cancelled = true
    }
  }, [id, file, key])

  if (IMAGE.test(file)) {
    return <img src={api.fileUrl(id, file)} alt={file} className="max-h-96 rounded-lg" />
  }
  if (current?.error) return <p className="px-4 py-3 text-sm text-rose-600 dark:text-rose-400">{current.error}</p>
  if (current?.empty) return <p className="px-4 py-3 text-sm text-zinc-400 italic">Empty file</p>
  if (!current?.html) {
    return (
      <div className="flex justify-center py-4 text-zinc-400">
        <Loader2 className="size-4 animate-spin" />
      </div>
    )
  }
  return (
    <div
      className="overflow-x-auto bg-zinc-50 px-4 py-3 font-mono text-[12.5px] leading-relaxed dark:bg-zinc-950/60 [&_pre]:bg-transparent!"
      dangerouslySetInnerHTML={{ __html: current.html }}
    />
  )
}
