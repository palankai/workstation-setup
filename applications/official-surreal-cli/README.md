---
stereotype: application
id: official-surreal-cli
name: "SurrealDB CLI (official)"
kind: CLI Tool
description: "SurrealDB's command-line tool: SurrealDB Cloud and database versions, from SurrealDB's own Homebrew tap"
tags: [database, cloud]
dependencies: []
homepage: https://surrealdb.com/docs/reference/cli/launcher
---

# SurrealDB CLI (official)

`surreal`, SurrealDB's command-line tool, installed from the official `surrealdb/tap`. It doesn't include
the database: it installs and runs components, each in `~/.surrealdb`.

<https://surrealdb.com/docs/reference/cli/launcher>

## Notes

- `surreal cloud …` manages SurrealDB Cloud.
- `surreal install db` (or `db@VERSION`, `--beta`, `--nightly`) installs database versions side by side;
  `surreal use`, `surreal +VERSION db …` pick one. `surreal upgrade` upgrades the components, Homebrew
  upgrades `surreal` itself.
- With `official-surreal-db` also installed, `surreal db …` runs its `surreal-db` until the CLI has a
  database of its own, which then wins.
- Uninstalling leaves `~/.surrealdb` and its components in place.
