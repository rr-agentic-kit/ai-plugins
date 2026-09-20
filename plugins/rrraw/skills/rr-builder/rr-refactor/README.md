# rr-refactor

Fixed-point phased refactor for **`rr-builder --refactor`** and orchestrate **refactor** stage — behavior-invariant coder-rule cleanup with durable epoch artifacts.

## Why

Production code accumulates structural violations (god methods, visibility drift, dead code) that block maintainability without changing product behavior. **rr-refactor** drives an expanded MR or repo scope through repeated assess → triage → inline fix → verify cycles until **two consecutive** full-scope assessments report zero auto-fixable findings. Audience: parent **rr-builder** after handoff (`lane: refactor`) or orchestrate refactor stage.

**Done-when:** terminal **`report.md`** under **`.ai/refactor/<runId>/`** with **`Status: complete`**, or **`partial`** / **`stopped`** with documented reason per **`refs/artifacts.md`**.

## What

Behavior-invariant refactoring on production source only. Collects violations in eight phased packs, triages to a manifest, applies fixes inline in the orchestrator session (no fix **`Task`**), verifies tests + lint on touched files, and expands scope when edits surface new neighbors.

**Out of scope:** observable behavior changes, commit/push/MR, Sonar-only remediation (**rr-ci**), feature work (**rr-coder**).

### Verification

Mechanical tool seeds (Checkstyle/Biome/Spotless) plus mandatory LLM assess packs for phases 4, 6, 7 residual, and 8. Convergence requires artifact-backed **`remaining_fix: 0`** twice — not tests alone.

## When

### Use when

- **`rr-builder --refactor`** handoff with validated param block
- Orchestrate **refactor** stage after build, before review (pre-review, pre-step-validate)
- God methods/classes, magic numbers, visibility drift, dead code, stack Prefer/Avoid cleanup on MR or repo scope

### Avoid when

| Need | Use instead |
|------|-------------|
| Feature implementation | **rr-coder** `--coder` |
| Sonar-only fix loop | **rr-ci** |
| Multi-lane review + fix | **rr-review** `--review --fix` |
| One-off assess without epoch loop | Collector spec only — not this orchestrator |

## Philosophy

- **Behavior-invariant** — tests must pass after each verified epoch; rollback on verify failure.
- **Eval-first convergence** — two consecutive zero-fix assessments on stable expanded scope; single clean pass is insufficient.
- **Artifact-backed state** — every epoch writes assess, manifest, and state JSON; no silent phase completion.
- **Inline fix seam** — collector may **`Task`** only for large multi-module assess; fix always runs in orchestrator session.
- **Thin parent** — SKILL holds invariant procedure; refs hold params, disk layout, disposition, and execute detail.
- **Production-source filter** — exclude test roots, generated output, vendored trees unless explicitly targeted.

## UX

### Invoke

Parent **rr-builder** handoff or orchestrate refactor stage — not user-invocable directly (`disable-model-invocation: true`).

### Intake

Validate param block from **`refs/params.md`**; normalize parent payload via **`refs/input-resolution.md`**.

### Clarify

**AskQuestion** once for empty MR diff (path or `all`); after collector Task failure (retry exhausted); after verify failure post-rollback. Text-mode: same options as prose — do not stall.

### Output

Epoch artifacts under **`.ai/refactor/<runId>/`**; terminal chat line **`Report written: .ai/refactor/<runId>/report.md`**.

### Close

Terminal **`report.md`**; parent sets **`step_refactor_done: true`** (or skip note when orchestrate scope empty).

## Design notes

- **Thin parent → this skill** — same pattern as **rr-test-endless**; collector/fix agent bodies live under **`agents/refactor/`**, not duplicated in README.
- **MR scope:** inline git per **rr-review** params (no `scripts/scope/*`).
- **Schemas and terminal semantics** live in **`refs/artifacts.md`** — SKILL Convergence is summary + link only.

## Constraints

- `disable-model-invocation: true`, `user-invocable: false` — parent-only orchestration.
- Default scope: **Current MR**; `--scope all` / `--scope full` for full repo; positional paths narrow scope.
- **`Task`** collector only when scope splits by module (**>50** files).
- Epoch cap default **5** (`--epoch-cap`).
- Phase apply order **1→8** per **`refs/fix-disposition.md`**.
- Missing required ref → stop: `missing ref: <path>`.

## Notes

| Path | Role |
|------|------|
| `SKILL.md` | Orchestrator procedure |
| `refs/params.md` | CLI grammar + param block |
| `refs/artifacts.md` | Disk layout, helpers, terminal convergence |
| `refs/leaf-contract.md` | Collector Task envelope + merge |
| `refs/inline-fix.md` | Inline execute SoT |
| `refs/fix-disposition.md` | Phase-specific fix rules |
| `refs/agent-index.md` | Task `subagent_type` map |

Executor source of truth: `SKILL.md`. This README is the human spec — not a Procedure echo.
