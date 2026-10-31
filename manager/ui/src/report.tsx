import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import type { Run } from './api'
import { RunReport } from './components/RunReport'
import './index.css'
import { RunSourceContext, type RunSource } from './source'

/** Embedded by `ws` when it writes a run's static report (see report.html). */
interface ReportData {
  run: Run
  /** Cleaned output by output file name */
  outputs: Record<string, string>
  /** Application names by id */
  apps: Record<string, string>
}

const data: ReportData = JSON.parse(document.getElementById('run-data')!.textContent!)
const source: RunSource = {
  run: async () => data.run,
  output: async (_, name) => data.outputs[name] ?? '',
}
const apps = new Map(Object.entries(data.apps).map(([id, name]) => [id, { name }]))
document.title = `Run report · ${data.run.id}`

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RunSourceContext value={source}>
      <div className="mx-auto max-w-6xl px-4 pt-6 pb-32 sm:px-6">
        <RunReport id={data.run.id} apps={apps} />
      </div>
    </RunSourceContext>
  </StrictMode>,
)
