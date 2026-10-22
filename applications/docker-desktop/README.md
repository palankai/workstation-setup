---
stereotype: application
id: docker-desktop
name: "Docker Desktop"
kind: Desktop App
description: "Docker Desktop with ECR credential helper, config linked"
tags: [tools, containers, docker]
dependencies: []
homepage: https://www.docker.com/products/docker-desktop
legacy: components/tools/docker
---

# Docker Desktop

Docker Desktop with ECR credential helper, config linked.

<https://www.docker.com/products/docker-desktop>

## Notes

Config is linked from `sensitive/dotfiles/docker-config.json`. Cask was renamed to `docker-desktop`.
