import type { Application } from './api'

/** Maps each dependency pulled in by the selection to the selected apps needing it. */
export function impliedBy(
  apps: Map<string, Application>,
  selected: Set<string>,
): Map<string, string[]> {
  const result = new Map<string, string[]>()
  const visit = (root: string, id: string, seen: Set<string>) => {
    for (const dependency of apps.get(id)?.dependencies ?? []) {
      if (seen.has(dependency)) continue
      seen.add(dependency)
      if (!selected.has(dependency)) {
        result.set(dependency, [...(result.get(dependency) ?? []), root])
      }
      visit(root, dependency, seen)
    }
  }
  for (const id of selected) visit(id, id, new Set())
  return result
}

/** The app and everything it depends on, transitively. */
export function withDependencies(apps: Map<string, Application>, id: string): Set<string> {
  const result = new Set<string>()
  const visit = (id: string) => {
    if (result.has(id)) return
    result.add(id)
    for (const dependency of apps.get(id)?.dependencies ?? []) visit(dependency)
  }
  visit(id)
  return result
}

export function difference<T>(a: Set<T>, b: Set<T>): T[] {
  return [...a].filter((item) => !b.has(item))
}

/** Descriptions start with the app name for search; drop it where the name is shown anyway. */
export function displayDescription(app: Application): string {
  const prefix = `${app.name}, `
  if (!app.description.startsWith(prefix)) return app.description
  const rest = app.description.slice(prefix.length)
  return rest.charAt(0).toUpperCase() + rest.slice(1)
}
