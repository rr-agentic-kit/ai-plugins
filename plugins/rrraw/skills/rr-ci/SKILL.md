---
name: rr-ci
description: Forge router for PR/MR ship (upsert via --create|update-[pr|mr]), issues, CI debug, publish, deploy.
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
- Named ship routes: `--create-pr` / `--create-mr` / `--update-pr` / `--update-mr` (and `--create-pr-mr` / `--update-pr-mr`) — **all upsert** (create if none for the branch; update if one exists)
- Optional `--draft` with any ship route — write title+body under `.ai/ci/`, AskQuestion for next steps (not forge draft status by itself)
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
   - **Ship routes (first-class):** `--create-pr` \| `--create-mr` \| `--update-pr` \| `--update-mr` \| `--create-pr-mr` \| `--update-pr-mr` → same **PR/MR upsert** ship (PR vs MR from forge after `detect-remote`; `-pr-mr` = forge-agnostic). Do **not** treat create vs update as different shapes.
   - **`--draft` (optional, with ship routes):** human title/body draft gate — write files under `.ai/ci/`, AskQuestion next steps; **not** forge `gh`/`glab` `--draft` (add that only if prose asks for forge-draft status). See step **title**.
   - **issue** → skip step 3 (`title` / [refs/pr-mr-templates.md](refs/pr-mr-templates.md)); after forge bind, load forge skill and run its **Issue create** row.
   - **PR/MR ship** (prose “open/create/update PR/MR” or routes above) → full steps 1–5 including `title`; nested forge skill branches on preflight `exists` vs `ready_create`.
   - **CI / review / publish / deploy** → steps 1–2, then matching load row (no invent).
   Done: shape recorded (include whether `--draft` gate applies). Stop: shape unclear after one AskQuestion (Issue | PR/MR ship | CI/other).

1. **root** — Resolve `REPO_ROOT` via plugin-relative `skills/rr-git/refs/repo-root.md`. Load `skills/rr-git/refs/safety.md` **only when** this ship may rewrite history, force-push, reset/clean, or discard work — not on clean upsert of an already-pushed branch. Done: cwd/`git -C` is the repo root (local work tree for git ops). Issue create on another forge project does **not** require that path to be a clone of the target.

2. **forge** — Run `rr-ci detect-remote` ([scripts/README.md](scripts/README.md)). Branch on `result.forge`: `github` | `gitlab` | `unknown`. If `unknown`, AskQuestion: GitHub | GitLab (no Other). **Forge target probe:** if the user named `owner/repo` (or equivalent URL) and it differs from `result.owner`/`result.repo`, set **forge target** to that `owner/repo` and pass it to the nested skill (`gh --repo` / `glab --repo`); do not silently use cwd origin. If ambiguous which repo → one AskQuestion (cwd origin | named `owner/repo`). Done: forge + forge target selected. Stop: user declines or forge is neither GitHub nor GitLab — say “GitHub/GitLab only.”

3. **title** — **PR/MR only.** Load [refs/pr-mr-templates.md](refs/pr-mr-templates.md). Author title + description per that ref.
   - **With `--draft` (or prose “draft title/description first”):** write `.ai/ci/pr-mr-title.txt` and `.ai/ci/pr-mr-body.md`; report paths; AskQuestion: **Ship** | **Keep draft only** | **I'll edit**. **Keep draft only** → stop (files remain). **I'll edit** → wait for the user; when they continue, **re-read disk files** (user edits win — do not regenerate) and AskQuestion again. **Ship** → proceed to load/execute using current disk title/body. Done: gate resolved or stopped.
   - **Without `--draft`:** draft in context (still may write body file for CLI `--body-file`); no AskQuestion gate. Done: title + description ready.
   Skip entirely for **issue** shape.

4. **load** — In **one** tool turn after forge bind: Read the nested forge skill **and** that forge’s `refs/cli.md`, and run `mr-add-preflight` when the task is PR/MR ship. Do not invent-search for skill flags as `rr-ci` JSON-CLI subcommands — ship routes are task-shape only (not SCRIPTS-SPEC). For `github` / `gitlab`, run the forge skill’s task row matching PR/MR ship vs issue vs CI.

**Fallback (no matching row):** CLI-only via [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md). If policy or forge-specific steps are still required → AskQuestion or stop. Do not invent nested skill behavior.

5. **execute** — Follow the nested skill; invoke CLI commands from [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md) or the forge skill’s allowlisted `gh`/`glab` rows. Happy-path upsert: keep tool turns tight (batch Reads/Shells; skip unused probes). Stop on first hard failure (`ok: false`, auth missing, preflight escalate, user declines issue create / keeps draft only).

## Invariants

- **Titles/descriptions (PR/MR):** only [refs/pr-mr-templates.md](refs/pr-mr-templates.md) — do not restate that policy here.
- **Issues:** draft → human approve → create; never skip draft when the user asked to draft first (default: always draft once before create).
- **Ship git:** Commit/push allowed from this skill when upserting a PR/MR. Still confirm before history rewrite or discarding work (`skills/rr-git/refs/safety.md`).
- **Ship routes:** `--create-*` / `--update-*` are aliases for the same upsert ship — skill invoke/task-shape flags, **not** `rr-ci` JSON-CLI subcommands unless added to [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md). Never open a second PR/MR for the same branch.
- **`--draft` + ship:** human gate via `.ai/ci/pr-mr-title.txt` + `.ai/ci/pr-mr-body.md`; user disk edits win; distinct from forge draft status unless user asks for that on ship.
- **Disk sidecars:** Any file this skill or its CLI writes (job traces, dumps, PR/MR drafts) lands under **`.ai/ci/`** at the target repo root — never cwd clutter. Review run artifacts stay under `.ai/review/` (**rr-review**).
- **No Renovate onboarding CLI** in this plugin. Do not add per-repo Renovate CI unless the user asked.
- Nested `gitlab` / `github` / `publish` / `deployment` skills are **not** plugin-listed; load them by path only.

## Orchestration

AskQuestion when: forge is `unknown`; task-shape is unclear; forge target is ambiguous; `--draft` ship next-steps; or nested issue path needs draft approval. Delivery channels: prefer AskQuestion for enumerable options; same options as short prose if the tool/harness is unavailable — do not stall. Nested skills are `disable-model-invocation`; do not wait for the user to @-mention them. Task agents: N/A.
