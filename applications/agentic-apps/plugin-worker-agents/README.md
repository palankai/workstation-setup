---
stereotype: application
id: plugin-worker-agents
name: "Worker Agents"
kind: Claude Plugin
description: "Slim subagent types for coordinated work: few tools, so each agent starts with a small context"
tags: [agentic, plugin]
dependencies: [claude-code]
---

# Worker Agents

Subagent types for a coordinator session that hands out work (implement an issue, review a
PR, fix review findings). The standard `general-purpose` type carries every tool, and the
long tool descriptions alone make it start at about 62k tokens. Every step re-reads that
context, so a slim type saves on every step of every agent.

- `worker`: shell, file tools and the Context7 library docs. Use it for workers and
  reviewers. Claude Code shows it as `worker-agents:worker`.

The Context7 tool names contain the claude.ai connector id; if the connector changes, update
the `tools` line in `plugin/agents/worker.md`.
