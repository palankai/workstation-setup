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
