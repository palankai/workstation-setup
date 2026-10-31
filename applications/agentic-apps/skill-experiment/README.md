---
stereotype: application
id: skill-experiment
name: "Experiment"
kind: Agent Skill
description: "Start or continue an experiment in the Workstation's Experiments folder"
tags: [agentic, skill]
dependencies: [claude-code, git]
---

# Experiment

Start or continue an experiment in `$WORK_HOME/Experiments`, whichever folder the session is in.
Invoked by hand only (`/experiment <idea>`); agents don't pick it up on their own.
`WORK_HOME` is exported from `dotfiles/zshenv`.
