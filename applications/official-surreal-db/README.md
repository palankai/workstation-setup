---
stereotype: application
id: official-surreal-db
name: "SurrealDB (official)"
kind: Service
description: "SurrealDB, document-graph database, from SurrealDB's own Homebrew tap"
tags: [database, server]
dependencies: []
homepage: https://surrealdb.com/
---

# SurrealDB (official)

SurrealDB, a scalable, distributed, document-graph database, installed from the official
`surrealdb/tap` as the `surreal-db` formula.

<https://surrealdb.com/>

## Notes

- The executable is `surreal-db` (`surreal-db start`), not `surreal`: in the tap, `surreal` is now
  the SurrealDB CLI, which installs and manages the database itself: that's `official-surreal-cli`.
- `brew services start surreal-db` runs a local development database on port 8000, as `root`/`root`,
  with its data in `$(brew --prefix)/var/surreal.db`. Uninstalling leaves that data in place.
