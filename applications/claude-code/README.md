---
name: "Claude Code"
description: "Anthropic's agentic coding CLI, with hooks, status line and settings linked"
tags: [ai, cli, agent]
dependencies: [jq]
homepage: https://claude.com/claude-code
legacy: components/ai/claude-code
---

# Claude Code

Anthropic's agentic coding CLI, with hooks, status line and settings linked.

<https://claude.com/claude-code>

## Notes

Status line script (`config/statusline-command.sh`) needs `jq`.
Settings are linked from `sensitive/targets/$WORKSTATION/dotfiles/.claude/settings.json`.
