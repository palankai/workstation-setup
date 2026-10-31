---
stereotype: application
id: claude-code
name: "Claude Code"
kind: CLI Tool
description: "Claude Code, Anthropic's agentic coding CLI, with hooks, status line and settings linked"
tags: [ai, agent]
dependencies: [jq-json-processor]
homepage: https://claude.com/claude-code
legacy: components/ai/claude-code
---

# Claude Code

Claude Code, Anthropic's agentic coding CLI, with hooks, status line and settings linked.

<https://claude.com/claude-code>

## Notes

Status line script (`config/statusline-command.sh`) needs `jq`.
Settings are linked from `sensitive/targets/$WORKSTATION/dotfiles/.claude/settings.json`.
Skills in `skills/<name>/` are linked into `~/.claude/skills/<name>` on every machine; the
`agentic-apps` skill there points agents at `applications/agentic-apps/README.md`.

`30-generate.py` writes the agent instructions (`ws generate`): `~/.claude/CLAUDE.md` from `instructions/user.md`
and `~/Workstation/AGENTS.md` from `instructions/workstation.md`, each followed by the profile's own part from
`sensitive/targets/$WORKSTATION/instructions/` when there is one. Edit those, not the generated files. The sources
aren't called CLAUDE.md or AGENTS.md so agents working in this folder don't take them as instructions for it.
