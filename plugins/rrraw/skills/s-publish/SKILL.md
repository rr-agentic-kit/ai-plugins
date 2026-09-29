---
name: s-publish
disable-model-invocation: true
description: /s-publish — publish artifacts to Pages, registries, releases, and object storage.
---

# s-ci / publish

Loaded from parent **s-ci** `SKILL.md` when the task is **publishing artifacts**, not deploying a live cluster workload.

## Purpose

Choose a **static or registry** destination and the CI job pattern that uploads immutable artifacts. Do not invent company registries or credentials.

## When to use

- GitHub Pages / GitLab Pages
- Container image push (GHCR, GitLab registry, other OCI)
- Language package registries (npm, PyPI, Maven) from CI
- GitHub Releases / GitLab generic packages / release assets
- Object storage (S3-compatible) for static sites or tarballs

## When not to use

- Rolling out to Kubernetes / Helm / Argo CD → sibling **deployment** skill
- Opening the PR/MR that *contains* the publish job → parent **s-ci** + forge skill
- Storing secrets in repo files

## Procedure

1. **Identify** — Name artifact file(s)/image, versioning (git tag vs SHA), public vs private. Done: artifact + version scheme named.
2. **Load destination** — [refs/destinations.md](refs/destinations.md). Prefer the forge already detected (`github` → GHCR/Pages/Releases; `gitlab` → GitLab registry/Pages/packages) unless the user named another target. Done: destination row selected.

**Fallback:** destination not in `destinations.md` → stop; ask for target or repo precedent. Do not invent registry hosts.

3. **Wire CI** — Follow [refs/ci-publish.md](refs/ci-publish.md) (auth, immutability, artifact paths). Done: CI job pattern drafted or updated per that ref.
4. **Stop** — Do not push from the agent laptop to production registries unless the user explicitly asked for a local publish.

## Invariants

- Auth, tag immutability, and token logging: [refs/ci-publish.md](refs/ci-publish.md) + [refs/destinations.md](refs/destinations.md) — do not restate here.
- Release notes below `---` in the PR/MR (parent `refs/pr-mr-templates.md`) when CI parses them.
