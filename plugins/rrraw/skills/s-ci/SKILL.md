---
name: s-ci
description: /s-ci — forge router for PR/MR ship, issues, CI debug, publish, deploy; --fix --sonar and --pull-dependabot.
disable-model-invocation: true
---

# s-ci

**Human overview:** [README.md](README.md)

**Scripts:** JSON envelope CLI — [scripts/README.md](scripts/README.md); frozen surface [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md).

## Shared refs

| Step / task | Load |
|-------------|------|
| Forge ops (PR/MR, issue, Actions/CI) | `skills/s-gh/SKILL.md` or `skills/s-glab/SKILL.md` after `detect-remote` |
| Publish artifacts | `skills/s-publish/SKILL.md` after forge skill |
| Cluster deploy | `skills/s-deploy/SKILL.md` after forge skill |
| PR/MR title/body | [refs/pr-mr-templates.md](refs/pr-mr-templates.md) |
| Pipeline fix anti-patterns | [refs/pipeline-fix-rules.md](refs/pipeline-fix-rules.md) |
| Sonar remediations (`--fix --sonar`) | [refs/sonar-fix.md](refs/sonar-fix.md) + [refs/pipeline-fix-rules.md](refs/pipeline-fix-rules.md) |
| Dependabot remote merges (`--pull-dependabot`) | [refs/pull-dependabot.md](refs/pull-dependabot.md) |
| Review thread disposition | [refs/review-comment-triage.md](refs/review-comment-triage.md) |
| Shape detail (draft / sonar / issue / ship / pull-dependabot) | [refs/task-shapes.md](refs/task-shapes.md) when step 0 needs more than classify |

Procedure step **load** follows this table; do not invent nested paths.

## Purpose

Own the **ship path** (commit/push when creating or updating a PR/MR), **forge tracker issues** (draft → approve → create), **generic CI** (title/description, pipeline debug, review helpers), **Sonar-scoped remediations** via `--fix --sonar`, and **Dependabot remote batch-merge** via `--pull-dependabot`. Detect the remote forge and **Read** the nested skill. Keep GitHub-only and GitLab-only facts out of this file.

## When to use

- Open or update a pull/merge request (including commit/push as part of that flow)
- Named ship routes: `--create-pr` / `--create-mr` / `--update-pr` / `--update-mr` (and `--create-pr-mr` / `--update-pr-mr`) — **all upsert** (create if none for the branch; update if one exists)
- Optional `--add-pr` / `--add-mr` / `--add-pr-mr` — same upsert aliases as create/update
- Optional `--draft` with any ship route — write title+body under `.ai/ci/`, AskQuestion for next steps (human disk gate; **not** a toggle for forge draft — forge create always uses `--draft`)
- Draft and create a GitHub or GitLab **issue** (including on a forge `owner/repo` other than cwd origin)
- Author PR/MR **title** and **description**
- Pipeline / Actions failure, CI reports, review submit, pending reviews
- **`--fix --sonar`** — auto-remediate open SonarQube issues for a PR or branch (scripted list; agent applies edits)
- **`--pull-dependabot`** — batch-merge `origin/dependabot/**` into the current branch with verify (GitHub only)
- Publish artifacts to a static or registry destination
- Deploy via Helm, Kubernetes, Argo CD, or similar

## When not to use

- Local git only (rebase, worktree, conflicts, branch cleanup) with **no** PR/MR → **s-git**
- General implement, refactor, test writing, or multi-lane code review → **rr-builder** (exceptions: **Sonar-only** remediations under `--fix --sonar`; **unresolved review threads on the current PR** — triage per [refs/review-comment-triage.md](refs/review-comment-triage.md), edit this branch when implement, then forge reply via nested **s-gh** `open-review-threads.sh --reply` with the thread `id`)
- Employer/internal catalogs (pinned component versions, cluster inventories, required tracker keys in titles) — not this plugin
- Inventing forge CLI flags or `s-ci` subcommands not listed in nested skills / [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md)

## Procedure

TodoWrite `merge: false` with ids `root`, `forge`, `title`, `load`, `execute` when shipping a PR/MR or running 3+ CLI commands. Single CLI call: skip TodoWrite. Shape-specific TodoWrite ids: see [refs/task-shapes.md](refs/task-shapes.md).

0. **task-shape** — Classify: **ship** (named routes or prose PR/MR upsert) | **`--draft`** (with ship) | **`--fix --sonar`** | **`--pull-dependabot`** | **issue** | **CI / review / publish / deploy**. Load [refs/task-shapes.md](refs/task-shapes.md) only when the shape needs draft-gate, sonar, pull-dependabot, issue, or ship-route detail beyond this line. Done: shape recorded. Stop: shape unclear after one AskQuestion (Issue | PR/MR ship | Sonar fix | Pull Dependabot | CI/other).

1. **root** — Resolve `REPO_ROOT` via plugin-relative `skills/s-git/refs/repo-root.md`. Load `skills/s-git/refs/safety.md` **only when** this ship may rewrite history, force-push, reset/clean, or discard work — not on clean upsert of an already-pushed branch. Done: cwd/`git -C` is the repo root (local work tree for git ops). Issue create on another forge project does **not** require that path to be a clone of the target.

2. **forge** — Run `rr-ci detect-remote` ([scripts/README.md](scripts/README.md)). Branch on `result.forge`: `github` | `gitlab` | `unknown`. If `unknown`, AskQuestion: GitHub | GitLab (no Other). **Forge target probe:** if the user named `owner/repo` (or equivalent URL) and it differs from `result.owner`/`result.repo`, set **forge target** to that `owner/repo` and pass it to the nested skill (`gh --repo` / `glab --repo`); do not silently use cwd origin. If ambiguous which repo → one AskQuestion (cwd origin | named `owner/repo`). Done: forge + forge target selected. Stop: user declines or forge is neither GitHub nor GitLab — say “GitHub/GitLab only.” **Skip** for `--fix --sonar` (CLI resolves PR via origin; forge bind only if user needs an override AskQuestion). For **`--pull-dependabot`:** require `github` (stop if not).

3. **title** — **PR/MR only.** Load [refs/pr-mr-templates.md](refs/pr-mr-templates.md). Author title + description per that ref. For `--draft` gate vs in-context draft, follow [refs/task-shapes.md](refs/task-shapes.md) `--draft` section. Skip for **issue**, **`--fix --sonar`**, and **`--pull-dependabot`**.

4. **load** — In **one** tool turn after forge bind: Read the nested forge skill **and** that forge’s `refs/cli.md`, and run `mr-add-preflight` when the task is PR/MR ship. Do not invent-search for skill flags as `s-ci` JSON-CLI subcommands — ship routes are task-shape only (not SCRIPTS-SPEC). For `github` / `gitlab`, run the forge skill’s matching task row. For **`--fix --sonar`:** Read [refs/sonar-fix.md](refs/sonar-fix.md) + [refs/pipeline-fix-rules.md](refs/pipeline-fix-rules.md) (and forge skill only if PR number must be resolved). For **`--pull-dependabot`:** Read [refs/pull-dependabot.md](refs/pull-dependabot.md) only (no forge nested skill).

**Fallback (no matching row):** CLI-only via [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md). If policy or forge-specific steps are still required → AskQuestion or stop. Do not invent nested skill behavior.

5. **execute** — Follow the nested skill or Sonar / pull-dependabot ref; invoke CLI commands from [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md) or the forge skill’s allowlisted `gh`/`glab` rows. Happy-path upsert: keep tool turns tight (batch Reads/Shells; skip unused probes). **`--fix --sonar`:** run `sonar-list-issues --lean` once, then apply fixes per [refs/sonar-fix.md](refs/sonar-fix.md). **`--pull-dependabot`:** run per [refs/pull-dependabot.md](refs/pull-dependabot.md) (one `pull-dependabot` shell; escalate only). Stop on first hard failure (`ok: false`, auth missing, preflight escalate, user declines issue create / keeps draft only).

## Invariants

- **Titles/descriptions (PR/MR):** only [refs/pr-mr-templates.md](refs/pr-mr-templates.md) — do not restate that policy here.
- **Issues:** draft → human approve → create; never skip draft when the user asked to draft first (default: always draft once before create).
- **Ship git:** Commit/push allowed from this skill when upserting a PR/MR. Still confirm before history rewrite or discarding work (`skills/s-git/refs/safety.md`).
- **Ship routes:** `--create-*` / `--update-*` / `--add-*` are aliases for the same upsert ship — skill invoke/task-shape flags, **not** `s-ci` JSON-CLI subcommands unless added to [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md). Never open a second PR/MR for the same branch.
- **Forge draft on create:** nested forge create always passes forge `--draft` plus `--base` / `--target-branch` from `mr-add-preflight` `result.base_branch`. On `exists`, update title/body/base only — do **not** convert ready↔draft.
- **`--draft` + ship:** human gate via `.ai/ci/pr-mr-title.txt` + `.ai/ci/pr-mr-body.md`; user disk edits win; distinct from forge `--draft` (always on create).
- **`--fix --sonar`:** list + remediations per [refs/sonar-fix.md](refs/sonar-fix.md); Sonar-scoped only — not general implement.
- **`--pull-dependabot`:** CLI loop + escalate per [refs/pull-dependabot.md](refs/pull-dependabot.md); GitHub-only; no invent merge chains; no invent `dependabot.yml` directory rewrites.
- **Disk sidecars:** Any file this skill or its CLI writes (job traces, dumps, PR/MR drafts) lands under **`.ai/ci/`** at the target repo root — never cwd clutter. Review run artifacts stay under `.ai/review/` (**s-review**).
- **No Renovate onboarding CLI** in this plugin. Do not add per-repo Renovate CI unless the user asked.
- Forge/publish/deploy specialists (`s-gh`, `s-glab`, `s-publish`, `s-deploy`) are plugin-listed for direct `@s-*` invoke; this router still **Read**s them by top-level path when routing.

## Orchestration

AskQuestion when: forge is `unknown`; task-shape is unclear; forge target is ambiguous; `--draft` ship next-steps; Sonar `no_open_pr` and user must pick `--branch` or abort; pull-dependabot escalate (close stale PRs \| leave); or nested issue path needs draft approval. Delivery channels: prefer AskQuestion for enumerable options; same options as short prose if the tool/harness is unavailable — do not stall. Nested skills are `disable-model-invocation`; do not wait for the user to @-mention them. Task agents: N/A.
