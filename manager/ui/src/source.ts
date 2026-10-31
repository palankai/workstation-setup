import { createContext } from 'react'
import { api, type Profile, type Run } from './api'

/** Where the run report reads from: the server's API, or data embedded in a static report. */
export interface RunSource {
  run: (id: string) => Promise<Run>
  output: (run: string, name: string) => Promise<string>
  /** Left out in a static report: no profile, so nothing to clear from the uninstall list */
  profile?: (name: string) => Promise<Profile>
}

export const RunSourceContext = createContext<RunSource>({
  run: api.run,
  output: api.runOutput,
  profile: api.profile,
})
