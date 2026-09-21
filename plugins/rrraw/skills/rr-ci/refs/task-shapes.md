# Task shapes (progressive load)

Load from root Procedure step **task-shape** when the invoke needs shape-specific detail. Root keeps thin dispatch only.

## Ship routes

`--create-pr` | `--create-mr` | `--update-pr` | `--update-mr` | `--add-pr` | `--add-mr` | `--create-pr-mr` | `--update-pr-mr` | `--add-pr-mr` → same **PR/MR upsert** (PR vs MR from forge after `detect-remote`; `-pr-mr` = forge-agnostic). Create / update / add are **not** different shapes. Nested forge skill branches on preflight `exists` vs `ready_create`.

Prose “open/create/update/add PR/MR” without a named route → same ship shape.

Pass explicit merge base via `mr-add-preflight --base` when handoff/user names one (`ship_base_branch` or prose). Otherwise preflight detects the closest `origin/*` ancestor (follow-up stacks keep non-trunk bases) and emits `result.base_branch` for forge `--base` / `--target-branch`.

## `--draft` (optional, with ship routes)

Human title/body gate — **not** a toggle for forge `gh`/`glab` `--draft`. Forge create **always** passes `--draft`; skill `--draft` only gates disk title/body AskQuestion.

1. Write `.ai/ci/pr-mr-title.txt` and `.ai/ci/pr-mr-body.md`; report paths.
2. AskQuestion: **Ship** | **Keep draft only** | **I'll edit**.
3. **Keep draft only** → stop (files remain). **I'll edit** → wait; on continue **re-read disk files** (user edits win — do not regenerate) and AskQuestion again. **Ship** → proceed using current disk title/body.

Without skill `--draft`: draft title/body in context (may still write body file for CLI `--body-file`); no AskQuestion gate. Forge create still uses `--draft`.

## `--fix --sonar`

Sonar remediations. Skip root `title` / forge bind unless PR lookup needs an override AskQuestion.

1. Load [sonar-fix.md](sonar-fix.md) + [pipeline-fix-rules.md](pipeline-fix-rules.md).
2. Run `sonar-list-issues --lean` (default: open PR/MR for current branch). Optional `--pr <id>` or `--branch <name>` overrides.
3. Apply fixes per sonar-fix.md.

TodoWrite ids: `root`, `load`, `execute` (skip forge/title unless scope needs forge PR lookup).

## `--pull-dependabot`

Batch-merge `origin/dependabot/**`. Skip root `title`. Forge bind required (must be `github`).

1. Load [pull-dependabot.md](pull-dependabot.md).
2. Run `rr-ci pull-dependabot --verify-cmd '<cmd>'` (optional `--dry-run` first). Escalate per that ref only.

TodoWrite ids: `root`, `forge`, `load`, `execute` (skip `title`).

## issue

Skip root step `title` / [pr-mr-templates.md](pr-mr-templates.md). After forge bind, load forge skill and run its **Issue create** row. TodoWrite ids: `root`, `forge`, `load`, `execute`.

## CI / review / publish / deploy

Steps `root` → `forge`, then matching Shared-refs load row (no invent). No `title` unless the ask also ships a PR/MR.
