---
name: rr-refactor
description: Fixed-point behavior-invariant coder-rule refactoring via rr-builder --refactor or orchestrate refactor stage.
disable-model-invocation: true
user-invocable: false
---

# rr-refactor

**Human overview:** [README.md](README.md)

## Purpose

Drive expanded production-source scope to **two consecutive** full-scope assessments with **`remaining_fix: 0`**. Optional in-run scratch under **`.ai/refactor/<runId>/`** (`state.json`, epochs). **Orchestrate:** durable output is a lean chat-style note `docs/rr/tasks/{slice_id}/{NNNN}-{step}.refactor.md`. **Handoff `--refactor`** without cursor: chat summary only (same lean shape — no required `REFACTOR_DIR/report.md`). Behavior-invariant refactoring only — tests must pass after each epoch. **`PLUGIN_ROOT`** = installed **rrraw** plugin root.

## When to use

- **`rr-builder --refactor`** handoff (parent sets `lane: refactor`)
- Orchestrate **refactor** stage after build, before review (pre-review, pre-step-validate)
- God methods/classes, magic numbers, visibility drift, dead code, stack Prefer/Avoid cleanup

## When not to use

| Need | Use instead |
|------|-------------|
| Feature implementation | **rr-coder** `--coder` |
| Sonar-only fix loop | **rr-ci** |
| Multi-lane review + fix | **rr-review** `--review --fix` |

## Procedure

Every run validates a param block from **`refs/params.md`** (parent handoff or orchestrate refactor stage). Handoff normalization: **`refs/input-resolution.md`**.

**Delivery channels:** Prefer AskQuestion for empty MR scope, collector Task failure after retry, and verify failure after rollback. Text-mode: same options as short prose; do not stall waiting for a widget.

TodoWrite **`merge: false`** before step 3 — `refactor-parse`, `refactor-scope`, `refactor-epoch-loop`, `refactor-close`. Exactly one **`in_progress`**; **`merge: true`** on completion.

### 1. parse

Confirm param block. Default → `scope: MR`, `epoch_cap: 5`. **Abort before step 2:** unknown flag; invalid path; conflicting scope; invalid **`--epoch-cap`**.

### 2. id

Mint **`runId`** and create **`REFACTOR_DIR`** via **`refs/artifacts.md`** § Run id helper (do not invent wall-clock ids manually). Set **`REFACTOR_ID`** for collector **`Task`**s.

### 3. scope

Resolve production-source candidates per **`refs/params.md`**. Empty MR diff → **AskQuestion** once (path or `all`). When scope exceeds 50 files, split by module per **`refs/artifacts.md`** § Module split. Write **`scope.json`** per **`refs/artifacts.md`**.

Tool seed (once): Checkstyle/Biome/Spotless on scoped files → phase buckets per `pack-tool-map.md`. Re-run on **touched** files after structural edits within an epoch.

### 4. epoch-loop

For `epoch = 1..epoch_cap`, execute:

| Substep | Owner | Output |
|---------|-------|--------|
| **assess** | inline-spec and/or **`Task`** `refactor-collector` per module | **`epochs/epoch-{NNN}-assess.json`** |
| **triage** | orchestrator session | **`epochs/epoch-{NNN}-manifest.json`** |
| **converge-or-execute** | orchestrator session | Skip execute when zero fix items; else **`refs/inline-fix.md`** |
| **verify** | orchestrator session | Tests + lint/static on touched files; manifest `verified` or rollback |
| **expand-scope** | orchestrator session | Update **`scope.json`** **`expanded_files`** when execute ran |

Substep contracts: **`refs/leaf-contract.md`**, **`refs/artifacts.md`**. **Collect default:** command session **`Read`**s collector spec (**inline-spec**). **`Task`** collector **only** when >50 files / multi-module — one Task per module (`ASSESS_MODE: full`, `BAND: all`).

Write **`state.json`** after every assess. Do not mark phases or an epoch complete without its assess, manifest, and state artifacts.

After each assess, increment `consecutive_zero_fix_assessments` when `remaining_fix: 0`; otherwise reset it to `0`. Reset `consecutive_zero_fix_assessments` to `0` whenever verified edits change `expanded_files`; the next assessment may start a new clean sequence.

### 5. close

Terminal convergence from **`state.json`** (and optional scratch under **`REFACTOR_DIR`**) per **`refs/artifacts.md`** § Terminal convergence — **no** required `report.md`.

| Mode | Durable output |
|------|----------------|
| **Orchestrate** (parent supplies `slice_id` + `{NNNN}` + step) | **Write** lean `docs/rr/tasks/{slice_id}/{NNNN}-{step}.refactor.md` per **`refs/artifacts.md`** § Lean task note. Optional Steps pointer `→ refactor: \`…\``. Chat: that path |
| **Handoff** without cursor | Chat summary only — same lean shape (status, scope, epochs, summary bullets); do **not** require `REFACTOR_DIR/report.md` |

## Convergence

Terminal **`status`**, **`terminal_reason`**, **`remaining_fix`**, and **`no_progress`** semantics: **`refs/artifacts.md`** § Terminal convergence (`state.json`) + param default **`epoch_cap: 5`**.

**Gates (summary):** **`complete`** only when expanded scope is **stable** and **two consecutive** full-scope assessments report **`remaining_fix: 0`** (tests alone insufficient). **`partial`** / **`stopped`** — per artifacts ref.

## Phase apply order (within execute)

Apply fixes in phase order **1→8** per **`refs/fix-disposition.md`**. Mandatory assess packs when tool seeds are empty: **4**, **6**, **7** residual, **8** — **`agents/refactor/collector.md`**.

## Task agents

| Concern | Agent | When |
|---------|-------|------|
| Assess | `refactor-collector` | Multi-module only (>50 files) |
| Fix | command session inline | Always |

**Forbidden:** **`Task`** for fix worker; bulk phase completion without epoch artifacts; advancing with remaining `auto_fixable` findings while claiming `complete`.

## Stop conditions

- Invalid params; empty scope after resolution
- Collector **`Task`** failure after one retry → **AskQuestion**
- Test failure after rollback → **AskQuestion** or **`stopped`**
- **`epoch_cap`** before two clean assessments → **`partial`**; use `confirmation_pending` when `remaining_fix: 0`

## Load table

**Core bundle (steps 1–3):** load before **`scope.json`** is written.

| Ref | When |
|-----|------|
| **`refs/params.md`** | Parse + scope (steps 1–3) |
| **`refs/input-resolution.md`** | Parent handoff normalization |
| **`refs/artifacts.md`** | Id mint, disk layout, merge, module split, terminal semantics |

**Assess bundle (epoch assess substep):** load before first collector inline-spec or **`Task`**.

| Ref | When |
|-----|------|
| **`refs/leaf-contract.md`** | Collector Task envelope + partial merge |
| **`agents/refactor/collector.md`** + **`agents/refactor/refs/pack-tool-map.md`** | Before assess |
| **`skills/rr-builder/rr-coder/SKILL.md`** + **`refs/code.principles.md`** | Before assess |
| Stack detect → language refs + **`skills/rr-builder/rr-coder/refs/observability.md`** | Before assess on scoped stack |
| **`srp-cohesion.md`**, **`testability.md`**, **`compliance-rubric.md`** | Before assess phases 4+ |

**Execute bundle (converge-or-execute substep):** load before **`refs/inline-fix.md`**.

| Ref | When |
|-----|------|
| **`agents/refactor/fix.md`** | Before inline execute (not a **`Task`**) |
| **`refs/fix-disposition.md`**, **`refs/inline-fix.md`** | Before inline execute |

**Dispatch:** **`refs/agent-index.md`** — when building collector **`Task`** prompts only.

If a required definition or ref is missing or unreadable, stop: `missing ref: <path>`.

## Done-when

- Convergence reached (`complete` / `partial` / `stopped` / skip) per **`refs/artifacts.md`**
- **Orchestrate:** lean `{NNNN}-{step}.refactor.md` written (or skip note when scope empty per slice-pipeline)
- **Handoff:** chat lean summary emitted
- Orchestrate stage: parent sets **`step_refactor_done: true`** (or skip note when scope empty per slice-pipeline)
