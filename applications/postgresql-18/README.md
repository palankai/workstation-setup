---
stereotype: application
id: postgresql-18
name: "PostgreSQL 18"
kind: Service
description: "PostgreSQL 18, object-relational database system (v18, linked)"
tags: [database, sql, server]
dependencies: []
options:
  server: "Start the server (brew services)"
homepage: https://www.postgresql.org/
legacy: components/database/postgresql@18
---

# PostgreSQL 18

PostgreSQL 18, object-relational database system (v18, linked).

<https://www.postgresql.org/>

## Notes

- Conflicts with `postgresql-17`: both run `brew link`.
- With the `server` option, every update starts it as a `brew services` service (once started, it's
  left running). Switching the option off doesn't stop it; uninstalling does.
