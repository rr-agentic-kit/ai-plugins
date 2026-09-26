# s-refactor

Fixed-point phased refactor for **`rr-builder --refactor`** and orchestrate **refactor** stage — behavior-invariant coder-rule cleanup with optional scratch epochs and a lean durable note.

## Why

Production code accumulates structural violations (god methods, visibility drift, dead code) that block maintainability without changing product behavior. **s-refactor** drives an expanded MR or repo scope through repeated assess → triage → inline fix → verify cycles until **two consecutive** full-scope assessments report zero auto-fixable findings. Audience: parent **rr-builder** after handoff (`lane: refactor`) or orchestrate refactor stage.

**Done-when:** converge / skip / partial / stopped per **`refs/artifacts.md`** + (orchestrate) lean **`{NNNN}-{step}.refactor.md`**. No required **`REFACTOR_DIR/report.md`**.

## What

Behavior-invariant refactoring on production source only. Collects violations in eight phased packs, triages to a manifest, applies fixes inline in the orchestrator session (no fix **`Task`**), verifies tests + lint on touched files, and expands scope when edits surface new neighbors.

**Out of scope:** observable behavior changes, commit/push/MR, Sonar-only remediation (**s-ci**), feature work (**s-coder**).

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
| Feature implementation | **s-coder** `--coder` |
| Sonar-only fix loop | **s-ci** |
| Multi-lane review + fix | **s-review** `--review --fix` |
| One-off assess without epoch loop | Collector spec only — not this orchestrator |

## Philosophy

- **Behavior-invariant** — tests must pass after each verified epoch; rollback on verify failure.
- **Eval-first convergence** — two consecutive zero-fix assessments on stable expanded scope; single clean pass is insufficient.
- **Scratch epochs** — `.ai/refactor/<runId>/` holds `state.json` / assess / manifest; durable SoT is the lean task note (orchestrate) or chat summary (handoff).
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

Optional scratch under **`.ai/refactor/<runId>/`**; orchestrate **Write** lean **`docs/rr/tasks/{slice_id}/{NNNN}-{step}.refactor.md`**; handoff without cursor → chat lean summary only.

### Close

Convergence status + lean note/summary; parent sets **`step_refactor_done: true`** (or skip note when orchestrate scope empty).

## Design notes

- **Thin parent → this skill** — same pattern as **s-test-endless**; collector/fix agent bodies live under **`agents/refactor/`**, not duplicated in README.
- **MR scope:** inline git per **s-review** params (no `scripts/scope/*`).
- **Schemas and terminal semantics** live in **`refs/artifacts.md`** — SKILL Convergence is summary + link only.

## Constraints

- `disable-model-invocation: true` — manual `@s-*` / slash invoke; parent may `Read` by path.
- Default scope: **Current MR**; `--scope all` / `--scope full` for full repo; positional paths narrow scope.
- **`Task`** collector only when scope splits by module (**>50** files).
- Epoch cap default **5** (`--epoch-cap`).
- Phase apply order **1→8** per **`refs/fix-disposition.md`**.
- Missing required ref → stop: `missing ref: <path>`.
- **`report.md` under `.ai/refactor/` is never a done-when.**

## Notes

| Path | Role |
|------|------|
| `SKILL.md` | Orchestrator procedure |
| `refs/params.md` | CLI grammar + param block |
| `refs/artifacts.md` | Scratch layout, lean task note, terminal convergence |
| `refs/leaf-contract.md` | Collector Task envelope + merge |
| `refs/inline-fix.md` | Inline execute SoT |
| `refs/fix-disposition.md` | Phase-specific fix rules |
| `refs/agent-index.md` | Task `subagent_type` map |

Executor source of truth: `SKILL.md`. This README is the human spec — not a Procedure echo.
