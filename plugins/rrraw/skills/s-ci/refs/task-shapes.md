# Task shapes (progressive load)

Load from root Procedure step **task-shape** when the invoke needs shape-specific detail. Root keeps thin dispatch only.

## Ship routes

`--create-pr` | `--create-mr` | `--update-pr` | `--update-mr` | `--add-pr` | `--add-mr` | `--create-pr-mr` | `--update-pr-mr` | `--add-pr-mr` → same **PR/MR upsert** (PR vs MR from forge after `detect-remote`; `-pr-mr` = forge-agnostic). Create / update / add are **not** different shapes. Nested forge skill branches on preflight `exists` vs `ready_create`.

Prose “open/create/update/add PR/MR” without a named route → same ship shape.

Pass explicit merge base via `mr-add-preflight --base` when handoff/user names one (`ship_base_branch` or prose). Otherwise preflight detects the closest `origin/*` ancestor (follow-up stacks keep non-trunk bases) and emits `result.base_branch` for forge `--base` / `--target-branch`.

## `--draft` (optional, with ship routes)

Human title/body gate — **not** a toggle for forge `gh`/`glab` `--draft`. Forge create **always** passes `--draft`; skill `--draft` only gates disk title/body AskQuestion. Title/body authoring SoT: `refs/ci/pr-mr-templates.md` **Author every ship invoke**.

1. Run **Author every ship invoke**; write `.ai/ci/pr-mr-title.txt` and `.ai/ci/pr-mr-body.md`; report paths.
2. AskQuestion: **Ship** | **Keep draft only** | **I'll edit**.
3. **Keep draft only** → stop (files remain). **I'll edit** → wait; on continue **re-read disk files** (user edits win — do not regenerate) and AskQuestion again. **Ship** → proceed using current disk title/body.

Without skill `--draft`: still run **Author every ship invoke** (may write body file for CLI `--body-file`); no AskQuestion gate. Forge create still uses `--draft`. Never reuse a prior `.ai/ci/pr-mr-*` from an earlier invoke.

## `--fix --sonar`

Sonar remediations. Skip root `title`. Forge bind optional at start; **required** once the run is PR-scoped (list `result.pull_request` or user `--pr`) so Ship/Wait can use forge wait primitives.

1. Load `refs/ci/sonar-fix.md` + `refs/ci/fix/pipeline-fix-rules.md`.
2. Run `sonar-list-issues --lean` (default: open PR/MR for current branch). Scope tokens: `--pr <id>`, `--branch <name>`, `--sonar overall|new-code`, or a pasted Sonar issues URL — mapping in `refs/ci/sonar-fix.md` List step.
3. Apply fixes per `refs/ci/sonar-fix.md` (`CODE_SMELL` rows go to **s-refactor** automatically). **PR-scoped:** after edits, commit+push tip → wait CI (`pre-merge-status` / `gh run watch`) → re-enter list→edit→ship→wait for new Sonar dirty until clean (`epoch_cap: 5`). **Branch-only / `overall` / `new-code`:** stop after Summary counts.

TodoWrite ids: `root`, `load`, `execute` (add `forge` when PR-scoped ship/wait runs).

## `--pull-dependabot`

Batch-merge `origin/dependabot/**`. Skip root `title`. Forge bind required (must be `github`).

1. Load [pull-dependabot.md](pull-dependabot.md).
2. Run `s-ci pull-dependabot --verify-cmd '<cmd>'` (optional `--dry-run` first). Escalate per that ref only.

TodoWrite ids: `root`, `forge`, `load`, `execute` (skip `title`).

## issue

Skip root step `title` / `refs/ci/pr-mr-templates.md`. After forge bind, load forge skill and run its **Issue create** row. TodoWrite ids: `root`, `forge`, `load`, `execute`.

## CI / review / publish / deploy

Steps `root` → `forge`, then matching Shared-refs load row (no invent). No `title` unless the ask also ships a PR/MR.
