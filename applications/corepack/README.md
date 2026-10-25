---
stereotype: application
id: corepack
name: "Corepack"
kind: Toolchain
description: "Corepack, bridge between Node projects and their package managers"
tags: [programming, javascript, node]
dependencies: []
homepage: https://github.com/nodejs/corepack
legacy: components/programming/node/corepack
---

# Corepack

Corepack, bridge between Node projects and their package managers.

<https://github.com/nodejs/corepack>

## Notes

`zshrc` holds aliases routing yarn/pnpm/npm through corepack; `20-run.sh` links it into the shell.
