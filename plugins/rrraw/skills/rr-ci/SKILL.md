---
name: rr-ci
description: Forge-agnostic CI and ship path — detect GitHub vs GitLab, PR/MR titles and descriptions, pipelines, then load nested gitlab/github/publish/deployment skills. Use when opening or updating a PR/MR, debugging CI, publishing artifacts, or deploying.
---

# rr-ci

**Human overview:** [README.md](README.md)

**Scripts:** JSON envelope CLI — [scripts/README.md](scripts/README.md); frozen surface [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md).

## Purpose

Own the **ship path** (commit/push when creating or updating a PR/MR) and **generic CI** (title/description, pipeline debug, review helpers). Detect the remote forge and **Read** the nested skill. Keep GitHub-only and GitLab-only facts out of this file.

## When to use

- Open or update a pull/merge request (including commit/push as part of that flow)
- Author PR/MR **title** and **description**
- Pipeline / Actions failure, CI reports, review submit, pending reviews
- Publish artifacts to a static or registry destination
- Deploy via Helm, Kubernetes, Argo CD, or similar

## When not to use

- Local git only (rebase, worktree, conflicts, branch cleanup) with **no** PR/MR → **rr-git**
- Implement, refactor, test writing, or multi-lane code review → **rr-builder**
- Company-specific catalogs (pinned component versions, internal clusters, Jira-required titles) — not this plugin

## Procedure

TodoWrite `merge: false` with ids `root`, `forge`, `title`, `load`, `execute` when shipping a PR/MR or running 3+ CLI commands. Single CLI call: skip TodoWrite.

1. **root** — Resolve `REPO_ROOT` via plugin-relative `skills/rr-git/refs/repo-root.md`. Destructive git: `skills/rr-git/refs/safety.md`. Done: cwd/`git -C` is the repo root.
2. **forge** — Run `rr-ci detect-remote` ([scripts/README.md](scripts/README.md)). Branch on `result.forge`: `github` | `gitlab` | `unknown`. If `unknown`, AskQuestion: GitHub | GitLab | Other. Done: forge selected.
3. **title** — Before create/update of a PR/MR, load [refs/pr-mr-templates.md](refs/pr-mr-templates.md). Done: title + description drafted per that ref.
4. **load** — Read the nested skill (and only that forge’s refs):

| `result.forge` / task | Load |
|------------------------|------|
| `github` | [github/SKILL.md](github/SKILL.md) |
| `gitlab` | [gitlab/SKILL.md](gitlab/SKILL.md) |
| Publish artifacts (Pages, registry, releases, object storage) | [publish/SKILL.md](publish/SKILL.md) after forge skill |
| Deploy to cluster (Helm, K8s, Argo CD) | [deployment/SKILL.md](deployment/SKILL.md) after forge skill |
| Pipeline fix anti-patterns | [refs/pipeline-fix-rules.md](refs/pipeline-fix-rules.md) |
| Review thread disposition | [refs/review-comment-triage.md](refs/review-comment-triage.md) |

5. **execute** — Follow the nested skill; invoke CLI commands from [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md). Stop on first hard failure (`ok: false`, auth missing, no PR/MR).

## Invariants

- **Titles/descriptions:** only [refs/pr-mr-templates.md](refs/pr-mr-templates.md) — do not restate that policy here.
- **Ship git:** Commit/push allowed from this skill when creating a PR/MR. Still confirm before history rewrite or discarding work (`skills/rr-git/refs/safety.md`).
- **No Renovate onboarding CLI** in this plugin. Do not add per-repo Renovate CI unless the user asked.
- Nested `gitlab` / `github` / `publish` / `deployment` skills are **not** plugin-listed; load them by path only.

## Orchestration

AskQuestion only when forge is `unknown`. Nested skills are `disable-model-invocation`; do not wait for the user to @-mention them.
