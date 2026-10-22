export interface Application {
  id: string
  name: string
  kind: string
  description: string
  tags: string[]
  dependencies: string[]
  homepage: string | null
  fundamental: boolean
  deprecated: boolean
  archived: boolean
  trial: boolean
  order: number
  folder: string
}

export type StepKind = 'brewfile' | 'run' | 'once'

export interface Step {
  file: string
  kind: StepKind
}

export interface ApplicationDetail extends Application {
  readme: string
  steps: Step[]
  files: string[]
}

export interface InlineEntry {
  label: string
  data: Record<string, unknown>
}

export interface Profile {
  name: string
  fundamentals: string[]
  selected: string[]
  implied: string[]
  missing: string[]
  inline: InlineEntry[]
  install_order: string[]
}

export interface SavedSearch {
  name: string
  query: string
  builtin: boolean
}

export interface Settings {
  searches: SavedSearch[]
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `${response.status} ${response.statusText}`)
  }
  return response.json()
}

export const api = {
  applications: () => request<Application[]>('/api/applications'),
  application: (id: string) =>
    request<ApplicationDetail>(`/api/applications/${encodeURIComponent(id)}`),
  fileUrl: (id: string, path: string) =>
    `/api/applications/${encodeURIComponent(id)}/files/${path}`,
  settings: () => request<Settings>('/api/settings'),
  profiles: () => request<string[]>('/api/profiles'),
  profile: (name: string) =>
    request<Profile>(`/api/profiles/${encodeURIComponent(name)}`),
  saveProfile: (name: string, selected: string[]) =>
    request<Profile>(`/api/profiles/${encodeURIComponent(name)}`, {
      method: 'PUT',
      body: JSON.stringify({ selected }),
    }),
}
