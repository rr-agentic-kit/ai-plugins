---
name: publish
disable-model-invocation: true
description: Publish build artifacts to static hosts and registries (GitHub/GitLab Pages, container registries, package registries, object storage, GitHub Releases). Loaded by rr-ci — not a top-level plugin skill.
---

# rr-ci / publish

Loaded from parent **rr-ci** `SKILL.md` when the task is **publishing artifacts**, not deploying a live cluster workload.

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
- Opening the PR/MR that *contains* the publish job → parent **rr-ci** + forge skill
- Storing secrets in repo files

## Procedure

1. **Identify artifact** — what file(s)/image, versioning (git tag vs SHA), public vs private. Done: artifact + version scheme named.
2. **Pick destination** — [refs/destinations.md](refs/destinations.md). Prefer the forge already detected (`github` → GHCR/Pages/Releases; `gitlab` → GitLab registry/Pages/packages) unless the user named another target.
3. **Wire CI** — [refs/ci-publish.md](refs/ci-publish.md). Auth via OIDC or CI job tokens; never long-lived tokens in YAML.
4. **Stop** — Do not push from the agent laptop to production registries unless the user explicitly asked for a local publish.

## Invariants

- Tags are immutable after publish; fix-forward with a new version.
- Release notes below `---` in the PR/MR (parent `refs/pr-mr-templates.md`) when CI parses them.
- Do not log tokens. Prefer `permissions:` least privilege on GitHub Actions; `CI_JOB_TOKEN` scope on GitLab.
