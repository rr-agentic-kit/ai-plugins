# Task shapes (progressive load)

Load when the invoke needs shape-specific detail. Shapes and TodoWrite ids are **identical** whether entry is `/s-ci`, `/s-gh`, or `/s-glab`. **s-ci** may skip forge bind when a run/job URL already implies forge + `owner/repo` — routing passes that context to the delegate.

## Ship routes

`--create-pr` | `--create-mr` | `--update-pr` | `--update-mr` | `--add-pr` | `--add-mr` | `--create-pr-mr` | `--update-pr-mr` | `--add-pr-mr` → same **PR/MR upsert** (PR vs MR from forge after `detect-remote` or direct forge entry; `-pr-mr` = forge-agnostic). Create / update / add are **not** different shapes. Nested forge skill branches on preflight `exists` vs `ready_create`.

Prose “open/create/update/add PR/MR” without a named route → same ship shape.

Pass explicit merge base via forge skill preflight `--base` when handoff/user names one (`ship_base_branch` or prose). Otherwise preflight detects the closest `origin/*` ancestor (follow-up stacks keep non-trunk bases) and emits `result.base_branch` for forge `--base` / `--target-branch`.

## `--draft` (optional, with ship routes)

Human title/body gate — **not** a toggle for forge draft on create. Forge create **always** passes forge `--draft`; skill `--draft` only gates disk title/body AskQuestion.

1. Write `.ai/ci/pr-mr-title.txt` and `.ai/ci/pr-mr-body.md`; report paths.
2. AskQuestion: **Ship** | **Keep draft only** | **I'll edit**.
3. **Keep draft only** → stop (files remain). **I'll edit** → wait; on continue **re-read disk files** (user edits win — do not regenerate) and AskQuestion again. **Ship** → proceed using current disk title/body.

Without skill `--draft`: draft title/body in context (may still write body file for CLI `--body-file`); no AskQuestion gate. Forge create still uses `--draft`.

## `--fix` (pipeline)

Pipeline fix for a failed CI job. Skip ship **title** step. Forge probe optional when a run/job URL supplies host + `owner/repo`.

1. Load [fix/pipeline-fix.md](fix/pipeline-fix.md) + [fix/pipeline-fix-rules.md](fix/pipeline-fix-rules.md).
2. Follow pipeline-fix steps: `intake` → `fetch` (active forge skill **debug-pipeline** row) → `locate` → `reproduce` → `classify` → `apply` → `verify`.
3. With no argument, use the current branch's open PR/MR as debug-pipeline fallback.

TodoWrite ids: `root`, `forge`, `load`, `execute`, `intake`, `fetch`, `locate`, `reproduce`, `classify`, `apply`, `verify` (skip ship `title`; skip `forge` when URL is sufficient).

## `--fix --sonar`

Sonar remediations. Skip ship **title** / forge bind unless PR lookup needs an override AskQuestion.

1. Load [sonar-fix.md](sonar-fix.md) + [fix/pipeline-fix-rules.md](fix/pipeline-fix-rules.md).
2. Run active forge skill **Sonar fix** row once (default: open PR/MR for current branch). Optional `--pr <id>` or `--branch <name>` overrides.
3. Apply fixes per sonar-fix.md.

TodoWrite ids: `root`, `load`, `execute` (skip forge/title unless scope needs forge PR lookup).

## `--pull-dependabot`

Batch-merge `origin/dependabot/**`. Skip ship **title**. Forge bind required (must be `github`).

1. Load [pull-dependabot.md](pull-dependabot.md).
2. Run active forge / s-ci **pull-dependabot** apply row (one shell; escalate only). Escalate per that ref only.

TodoWrite ids: `root`, `forge`, `load`, `execute` (skip `title`).

## issue

Skip ship **title** / [pr-mr-templates.md](pr-mr-templates.md). After forge bind, load forge skill and run its **Issue create** row. TodoWrite ids: `root`, `forge`, `load`, `execute`.

## CI / review / publish / deploy

Steps `root` → `forge`, then matching forge skill task row (no invent). No ship **title** unless the ask also ships a PR/MR.
