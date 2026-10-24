import type { Application } from './api'

const words = (text: string) => text.toLowerCase().split(/[^a-z0-9+#.]+/).filter(Boolean)

const isBoundary = (text: string, index: number) => index === 0 || /[^a-z0-9]/.test(text[index - 1])

/**
 * fzf-style subsequence match: every character of the pattern in order.
 * Returns 0..1, rewarding consecutive runs and word-boundary hits; 0 if no match.
 */
export function subsequenceScore(text: string, pattern: string): number {
  let best = 0
  for (let start = text.indexOf(pattern[0]); start !== -1; start = text.indexOf(pattern[0], start + 1)) {
    let score = 0
    let previous = start - 1
    let matched = true
    for (let i = 0; i < pattern.length; i++) {
      const position = text.indexOf(pattern[i], previous + 1)
      if (position === -1) {
        matched = false
        break
      }
      score += 1
      if (isBoundary(text, position)) score += 3
      if (i > 0 && position === previous + 1) score += 2
      if (i > 0) score -= Math.min(position - previous - 1, 3) * 0.5
      previous = position
    }
    if (matched) best = Math.max(best, score)
  }
  return Math.max(0, best / (pattern.length * 6))
}

/** Damerau-Levenshtein distance, giving up once it exceeds max. */
function editDistance(a: string, b: string, max: number): number {
  if (Math.abs(a.length - b.length) > max) return max + 1
  const rows = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array<number>(b.length).fill(0)])
  for (let j = 1; j <= b.length; j++) rows[0][j] = j
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1
      rows[i][j] = Math.min(rows[i - 1][j] + 1, rows[i][j - 1] + 1, rows[i - 1][j - 1] + cost)
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        rows[i][j] = Math.min(rows[i][j], rows[i - 2][j - 2] + 1)
      }
    }
  }
  return rows[a.length][b.length]
}

function isTypoOf(token: string, candidates: string[]): boolean {
  if (token.length < 4) return false
  const max = token.length >= 8 ? 2 : 1
  return candidates.some((word) => editDistance(token, word.slice(0, token.length + max), max) <= max)
}

function scoreToken(app: Application, token: string): number {
  const id = app.id.toLowerCase()
  const name = app.name.toLowerCase()
  const nameWords = [...words(app.id), ...words(app.name)]
  if (id === token || name === token) return 100
  if (id.startsWith(token) || name.startsWith(token)) return 60
  if (nameWords.some((word) => word.startsWith(token))) return 40
  if (app.tags.includes(token)) return 20
  if (app.tags.some((tag) => tag.startsWith(token))) return 12
  if (words(app.description).some((word) => word.startsWith(token))) return 6
  if (token.length >= 3) {
    const fuzzy = Math.max(subsequenceScore(id, token), subsequenceScore(name, token))
    if (fuzzy >= 0.3) return 4 + fuzzy * 30
  }
  if (isTypoOf(token, [...nameWords, ...app.tags])) return 8
  if (isTypoOf(token, words(app.description))) return 3
  return 0
}

export interface ParsedQuery {
  terms: string[]
  tags: string[]
  kinds: string[]
  flags: string[]
}

/** "CLI Tool" → "cli-tool", so `kind:cli` can match it. */
export const kindSlug = (kind: string) => kind.toLowerCase().replace(/\s+/g, '-')

const FLAGS: Record<string, (app: Application, marked: Set<string>) => boolean> = {
  uninstall: (app, marked) => marked.has(app.id),
  fundamental: (app) => app.fundamental,
  deprecated: (app) => app.deprecated,
  archived: (app) => app.archived,
  trial: (app) => app.trial,
}

/**
 * `#rust` or `tag:rust` filter by tag, `kind:cli` by kind (both prefix), `is:fundamental` by flag
 * (also deprecated, archived, trial, and uninstall for the profile's); everything else is a search term.
 */
export function parseQuery(query: string): ParsedQuery {
  const parsed: ParsedQuery = { terms: [], tags: [], kinds: [], flags: [] }
  for (const token of query.toLowerCase().split(/\s+/).filter(Boolean)) {
    const filter = token.match(/^(#|tag:|kind:|is:)(.*)$/)
    if (!filter) parsed.terms.push(token)
    else if (!filter[2]) continue
    else if (filter[1] === 'kind:') parsed.kinds.push(filter[2])
    else if (filter[1] === 'is:') parsed.flags.push(filter[2])
    else parsed.tags.push(filter[2])
  }
  return parsed
}

function matchesFilters(app: Application, { tags, kinds, flags }: ParsedQuery, marked: Set<string>): boolean {
  return (
    tags.every((wanted) => app.tags.some((tag) => tag.startsWith(wanted))) &&
    kinds.every((wanted) => kindSlug(app.kind).startsWith(wanted)) &&
    flags.every((flag) => FLAGS[flag]?.(app, marked) ?? false)
  )
}

/**
 * Every term and filter must match; better matches on id/name rank first.
 * Archived apps only show up for `is:archived`, or when `keep` says so (e.g. they'd be installed).
 */
export function search(
  apps: Application[],
  query: string,
  keep: (app: Application) => boolean = () => false,
  marked: Set<string> = new Set(),
): Application[] {
  const parsed = parseQuery(query)
  const { terms } = parsed
  const showArchived = parsed.flags.includes('archived')
  const tagged = apps.filter(
    (app) => (!app.archived || showArchived || keep(app)) && matchesFilters(app, parsed, marked),
  )
  if (!terms.length) return tagged
  return tagged
    .map((app) => {
      const scores = terms.map((term) => scoreToken(app, term))
      return { app, score: scores.includes(0) ? 0 : scores.reduce((a, b) => a + b) }
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || a.app.name.localeCompare(b.app.name))
    .map(({ app }) => app)
}
