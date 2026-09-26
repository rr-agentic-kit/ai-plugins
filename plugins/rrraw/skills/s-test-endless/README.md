# Endless add-test (`rr-builder --add-endless-test`)

Coverage-first, multi-epoch test perfection for a repo or path scope.

## Why

Teams need stronger tests beyond a single assess/write pass: coverage-informed discovery, planner-sized work-packs, worker execution, verify, and re-assess until defects clear or epoch budget exhausts. Done when actionable defect **`COUNTS:`** reach policy zero (typically all non-ADEQUATE counts at **0**) under **`test-heuristics.md`**.

## What

Mechanical loop: coverage gateway → exhaustive assess → planner work-packs → worker execute → verify → re-assess.

| Artifact | Role |
|----------|------|
| `REVIEW_DIR/test/assess/` | Assessment markdown (`COUNTS:`, tables) |
| `REVIEW_DIR/plans/trp-*.md` | Work order + execution progress |
| `REVIEW_DIR/test/state/` | Optional checkpoint for resume |

**Out of scope:** application production-code review; MR merge-oriented test fix (use **s-review**).

Chunk geometry: **`skills/s-review/refs/chunking.md`** only.

## When

### Use when

- Coverage-first multi-epoch loop on repo or path scope
- **`rr-builder --add-endless-test`** handoff (`lane: add_endless_test`)

### Avoid when

- MR / branch test-review fix → **s-review** `--test --fix`
- One-off assess / write / migrate → **s-tester** via **`--tester`**

## Philosophy

- **Eval-first:** assess before plan; verify before re-assess; exit rules in **`exit-conditions.md`** trump optimism.
- **Plan markdown SoT:** dispatch and progress live on **`trp-*.md`** — checkpoint is resume-only, never overrides plans.
- **Depth-0 orchestrator:** leaf work via **`Task`** only; helpers collapse deterministic probe/queue math.
- **Scoped-only:** requires **`Scope:`** + **`PLUGIN_ROOT`**; stops on trunk **`main`/`master`** per policy.
- **Manifest in chat:** §3b work-pack table is user-visible markdown, not Shell-only echo.

## UX

### Invoke

Manual `@s-test-endless` / slash — **`disable-model-invocation: true`**. Parent **`rr-builder --add-endless-test`** may `Read` by path.

### Intake

Parent normalizes **`payload.endless_test`**; orchestrator resolves **`Scope:`**, **`Start:`**, **`--max-epochs`** (default **5**), **`--max-parallel`**.

### Clarify

**AskQuestion** / **AskUserQuestion** in **`input-resolution.md`** when scope ambiguous — same options as prose if tool unavailable.

### Output

Terminal shapes only: **`Test review complete`**, **`Stopped:`**, **`Deferred:`** per **`terminal-report.md`**.

### Close

**TodoWrite** epoch updates; final block cites phase reached and remaining gaps.

## Design notes

- **Plan markdown vs checkpoint:** execution truth stays on plan files; **`endless-add-test-checkpoint.json`** is host-resume metadata only (see **`artifacts.md`**).
- **Main-chat manifest vs helpers:** §3b table is pasted for operator visibility; **`manifest-table`** helper emits deterministic rows so the orchestrator does not invent grouping heuristics.

## Constraints

| Field | Value |
|-------|-------|
| Invoke | Internal via **`rr-builder --add-endless-test`** |
| Default epochs | **5** (`--max-epochs`) |
| Start slices | **`fresh`** \| **`plan`** \| **`execute`** |
| Orchestrator depth | **0** — no nested orchestrator **`Task`** |
| Helper scripts | **`PLUGIN_ROOT/scripts/endless_test_helpers/cli.py`** |

## Notes

| File | Role |
|------|------|
| `SKILL.md` | Handoff procedure |
| `refs/orchestration.md` | Loop index |
| `refs/phases/*.md` | Phase mechanics |
| `refs/orchestration-core.md` | Shared pre-flight + callbacks |
