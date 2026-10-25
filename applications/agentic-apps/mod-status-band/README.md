---
stereotype: application
id: mod-status-band
name: "Status Band"
kind: Claude Mod
description: "Two-row band above the prompt: prompt cache with keep-warm, context, 5h/7d limits, folder and git status"
tags: [agentic, mod]
dependencies: [claude-code, git]
---

# Status Band

A coloured, two-row band above Claude Code's prompt, in the terminal and the desktop app.

```
🔥 3m ago ██████████░░ 21:14 ♨ 05:14   🧠 ███░░░░░░░░░ 27% of 1M   ⏳ 5h █░░░░░░░░░░░ 9% ↻ 42m 21:00   📅 7d ░░░░░░░░░░░░ 1% ↻ Sun 11:00
📂 ~/opt/workstation-setup                                                                      ⎇ master ✚1 …1 ⚙
```

## First row: cache, context, limits

Each item is as wide as its text plus a bar. The bars share one length, which grows with
the width and is dropped when the window is too narrow for it.

- **🔥 Prompt cache.** How long ago the last reply was, a bar draining over the cache's 1-hour
  life (green, amber under 15 minutes left, red under 5; 🌡️ cooling, 🧊 cold), the time of
  that reply, then the keep-warm switch (below).
- **🧠 Context.** How full the context window is, and its size. The bar and the percentage
  take their colour from the colour bands: green below 25%, yellow to 50%, orange to 75%,
  red above, by default.
- **⏳ 5h and 📅 7d limits.** Percentage used and when each resets. Any other window the
  API reports, such as a model-specific one, is shown the same way. They are coloured by
  pace: where the current rate of use would end by the reset.

  | By the reset you'd be at | Colour |
  | --- | --- |
  | under 75% | green |
  | 75–100% | yellow |
  | 100–125% | orange |
  | over 125%, or 90% already used | red |

  When the pace runs out before the reset, `⚠ out <time>` says when. The first tenth of a
  window counts as a tenth, so one burst right after a reset does not read as running out.

## Second row: folder and git

The session's folder on the left; on the right the git branch with ✖ conflicts, ● staged,
✚ modified, … untracked (✔ when clean), ⚑ stashes, ⇡ ahead, ⇣ behind and ⊘ no upstream,
then ⚙ for the settings. Git is read after every reply and every minute.

## Keep-warm

The prompt cache lives for an hour after the last request. Keep-warm sends a tiny request
over the cached conversation about every 55 minutes while the session is idle, so the cache
never expires and the next prompt does not pay to write it again.

- On by default, for 8 hours after the last reply; each new reply starts the hours again.
- ♨ shows the time it keeps the cache warm until; click it to switch keep-warm off for that
  session. ☕ means it is off; click it to switch it on, which warms a cold cache again too.
- Left alone, a cache that has already gone cold stays cold.
- ⚠ next to ♨ means the last ping failed; it is retried after 5 minutes.
- Each ping reads the whole cached conversation: it costs cache-read tokens and counts a
  little towards the usage limits.

## Settings

⚙ in the band, or `/status-band`, opens a pane. The settings apply to every session and
are kept in Claude Code's plugin store.

- Keep-warm on or off by default in new sessions.
- How long to keep warm after the last reply: 2, 4, 8 or 12 hours.
- The colour bands of the context: each edge moves in 5% steps, kept in order; Reset
  restores 25%, 50%, 75%.

## Where the figures come from

- **Context and limits:** Claude Code's own session usage, which the API reports with each
  reply (`$.session.usage()` and the `session.measure` event).
- **Cache time:** the API does not report it. The band counts from the last reply of the
  main conversation; a keep-warm ping counts as a reply.
- **After a restart:** the time and context size of the last reply come from the session's
  transcript (`~/.claude/projects/*/<session id>.jsonl`), and the limits last seen from the
  plugin store, so the band shows the same figures before the first new reply. Each
  session's keep-warm choice is kept in the store too, but a ping can only go out once the
  session has had a new reply.
- **Local times:** read from `date +%z` when the session starts, so a clock change during a
  session is an hour off until the next one.

The band steps aside while Claude Code shows something of its own above the prompt, such as
a question to answer.

## Working on it

The payload in `plugin/` is linked as `~/.claude/skills/status-band`; edit it in place and
start a new session or run `/reload-plugins`. Bump `version` in `plugin.json` when the
behaviour changes.

- `hooks/register.tsx` is the whole mod; `types/index.d.ts` declares the values it keeps in
  `$.state`.
- `hooks/register.test.tsx` drives it against a stand-in engine on the terminal and desktop
  surfaces.
- `tsconfig.json` extends the API types Claude Code writes to `.claude-plugin/types/` (ignored
  by git) once it has loaded the mod.

```bash
claude plugin validate applications/agentic-apps/mod-status-band/plugin
```

```bash
claude plugin test applications/agentic-apps/mod-status-band/plugin
```
