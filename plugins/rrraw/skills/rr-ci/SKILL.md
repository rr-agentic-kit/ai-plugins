---
name: rr-ci
description: Forge router for PR/MR, forge issues, CI debug, publish, deploy. Use for PR/MR ship, issue draft/create, pipelines, publish, or deploy.
---

# rr-ci

**Human overview:** [README.md](README.md)

**Scripts:** JSON envelope CLI — [scripts/README.md](scripts/README.md); frozen surface [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md).

## Shared refs

| Step / task | Load |
|-------------|------|
| Forge ops (PR/MR, issue, Actions/CI) | [github/SKILL.md](github/SKILL.md) or [gitlab/SKILL.md](gitlab/SKILL.md) after `detect-remote` |
| Publish artifacts | [publish/SKILL.md](publish/SKILL.md) after forge skill |
| Cluster deploy | [deployment/SKILL.md](deployment/SKILL.md) after forge skill |
| PR/MR title/body | [refs/pr-mr-templates.md](refs/pr-mr-templates.md) |
| Pipeline fix anti-patterns | [refs/pipeline-fix-rules.md](refs/pipeline-fix-rules.md) |
| Review thread disposition | [refs/review-comment-triage.md](refs/review-comment-triage.md) |

Procedure step **load** follows this table; do not invent nested paths.

## Purpose

Own the **ship path** (commit/push when creating or updating a PR/MR), **forge tracker issues** (draft → approve → create), and **generic CI** (title/description, pipeline debug, review helpers). Detect the remote forge and **Read** the nested skill. Keep GitHub-only and GitLab-only facts out of this file.

## When to use

- Open or update a pull/merge request (including commit/push as part of that flow)
- Draft and create a GitHub or GitLab **issue** (including on a forge `owner/repo` other than cwd origin)
- Author PR/MR **title** and **description**
- Pipeline / Actions failure, CI reports, review submit, pending reviews
- Publish artifacts to a static or registry destination
- Deploy via Helm, Kubernetes, Argo CD, or similar

## When not to use

- Local git only (rebase, worktree, conflicts, branch cleanup) with **no** PR/MR → **rr-git**
- Implement, refactor, test writing, or multi-lane code review → **rr-builder**
- Employer/internal catalogs (pinned component versions, cluster inventories, required tracker keys in titles) — not this plugin
- Inventing forge CLI flags or `rr-ci` subcommands not listed in nested skills / [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md)

## Procedure

TodoWrite `merge: false` with ids `root`, `forge`, `title`, `load`, `execute` when shipping a PR/MR or running 3+ CLI commands. Single CLI call: skip TodoWrite. **Issue-only** tasks: TodoWrite ids `root`, `forge`, `load`, `execute` (skip `title` / pr-mr-templates).

0. **task-shape** — Classify the user ask before PR ship steps:
   - **issue** → skip step 3 (`title` / [refs/pr-mr-templates.md](refs/pr-mr-templates.md)); after forge bind, load forge skill and run its **Issue create** row.
   - **PR/MR ship** → full steps 1–5 including `title`.
   - **CI / review / publish / deploy** → steps 1–2, then matching load row (no invent).
   Done: shape recorded. Stop: shape unclear after one AskQuestion (Issue | PR/MR | CI/other).

1. **root** — Resolve `REPO_ROOT` via plugin-relative `skills/rr-git/refs/repo-root.md`. Destructive git: `skills/rr-git/refs/safety.md`. Done: cwd/`git -C` is the repo root (local work tree for git ops). Issue create on another forge project does **not** require that path to be a clone of the target.

2. **forge** — Run `rr-ci detect-remote` ([scripts/README.md](scripts/README.md)). Branch on `result.forge`: `github` | `gitlab` | `unknown`. If `unknown`, AskQuestion: GitHub | GitLab (no Other). **Forge target probe:** if the user named `owner/repo` (or equivalent URL) and it differs from `result.owner`/`result.repo`, set **forge target** to that `owner/repo` and pass it to the nested skill (`gh --repo` / `glab --repo`); do not silently use cwd origin. If ambiguous which repo → one AskQuestion (cwd origin | named `owner/repo`). Done: forge + forge target selected. Stop: user declines or forge is neither GitHub nor GitLab — say “GitHub/GitLab only.”

3. **title** — **PR/MR only.** Before create/update of a PR/MR, load [refs/pr-mr-templates.md](refs/pr-mr-templates.md). Done: title + description drafted per that ref. Skip entirely for **issue** shape.

4. **load** — Read the nested skill (and only that forge’s refs) per **Shared refs** above. For `github` / `gitlab`, also run the forge skill’s task row matching the classified shape (issue vs PR/MR vs CI).

**Fallback (no matching row):** CLI-only via [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md). If policy or forge-specific steps are still required → AskQuestion or stop. Do not invent nested skill behavior.

5. **execute** — Follow the nested skill; invoke CLI commands from [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md) or the forge skill’s allowlisted `gh`/`glab` rows. Stop on first hard failure (`ok: false`, auth missing, no PR/MR when PR/MR was required, user declines issue create).

## Invariants

- **Titles/descriptions (PR/MR):** only [refs/pr-mr-templates.md](refs/pr-mr-templates.md) — do not restate that policy here.
- **Issues:** draft → human approve → create; never skip draft when the user asked to draft first (default: always draft once before create).
- **Ship git:** Commit/push allowed from this skill when creating or updating a PR/MR. Still confirm before history rewrite or discarding work (`skills/rr-git/refs/safety.md`).
- **Disk sidecars:** Any file this skill or its CLI writes (job traces, dumps) lands under **`.ai/ci/`** at the target repo root — never cwd clutter. Review run artifacts stay under `.ai/review/` (**rr-review**).
- **No Renovate onboarding CLI** in this plugin. Do not add per-repo Renovate CI unless the user asked.
- Nested `gitlab` / `github` / `publish` / `deployment` skills are **not** plugin-listed; load them by path only.

## Orchestration

AskQuestion when: forge is `unknown`; task-shape is unclear; forge target is ambiguous; or nested issue path needs draft approval. Delivery channels: prefer AskQuestion for enumerable options; same options as short prose if the tool/harness is unavailable — do not stall. Nested skills are `disable-model-invocation`; do not wait for the user to @-mention them. Task agents: N/A.
