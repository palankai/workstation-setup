---
stereotype: application
id: workstation-manager
name: "Workstation Manager"
kind: Setup
description: "Workstation Manager, the ws command plus the web UI's dependencies"
tags: [shell]
dependencies: []
fundamental: true
order: 70
---

# Workstation Manager

Workstation Manager, the `ws` command plus the web UI's dependencies.

Links `bin/ws` into `~/.local/bin` and installs the `server` extra; the built UI is committed in `manager/ui/dist`.
On a fresh machine, run `~/opt/workstation-setup/bin/ws update` once; afterwards `ws update`.
