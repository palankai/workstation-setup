---
name: agentic-apps
description: Create, update, install or remove the person's own agent skills, Claude Code mods and plugins, kept as installable "agentic apps" in their workstation-setup repository. Use whenever they ask to make a new skill or mod, change or fix one of their skills, bring an existing skill under management, install one on this machine, or remove one, even if they don't say "agentic app".
---

# Agentic apps

The person keeps every skill, mod and plugin as its own application in their
workstation-setup repository, so each machine's profile can pick which ones it gets.
Anything made outside that structure won't be installed on their other machines.

## Find the guide

1. The repository is at `$WORKSTATION_INSTALLATION_PATH`. If that isn't set, read it from
   `~/.workstation-setup-config` (`export WORKSTATION_INSTALLATION_PATH=...`), or use
   `~/opt/workstation-setup`.
2. Read `applications/agentic-apps/README.md` there, all of it, before creating or changing
   anything. It has the naming, folder layout, the application's `README.md`, the install and
   uninstall steps, and the commands to install, check and remove one.

## Then

- Work in `applications/agentic-apps/` in that repository, never directly in
  `~/.claude/skills`: those entries are links back into the repository.
- For a new one, agree the name and kind (skill, mod or plugin) with the person first.
- Install it on this machine with the commands in the guide, and check the link it made.
- Ask before committing; commit the app folder together with any profile change.
