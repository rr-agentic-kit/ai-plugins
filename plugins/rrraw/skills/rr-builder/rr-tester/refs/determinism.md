# determinism

**Owner:** Global deterministic behavior across phases and multi-pass chains.

## Stable scope ordering

Before assess, identify-missing, or plan:

1. Normalize scope per [input-resolution.md](input-resolution.md).
2. Expand `diff` / `uncommitted` / `repo` to concrete file lists via repo tools.
3. Sort files lexicographically by path.
4. Sort symbols within a file alphabetically when enumerating test targets.

Same inputs → same ordered work list.

## JSON parse retry policy

Applies to agent final messages and structured tool outputs:

1. Attempt `JSON.parse` on entire final message (strip markdown fences if present).
2. On failure: one retry requesting valid JSON only.
3. Second failure: hard-stop with `AGENT_OUTPUT_PARSE_FAILED`; include first 200 chars of raw output in `details`.

No further retries. No partial acceptance of malformed JSON.

## Plan merge rules (maintain + exclude + add)

When combining plan tracks or epoch carry-over:

1. Dedupe by `(action, path)`; later epoch wins on conflict.
2. Sort by `priority` ascending, then `path` lexicographically.
3. Tie-break equal priority: `risk` high > medium > low (from identify-missing linkage when available).
4. Execution order: `maintain` → `exclude` → `add`.
5. Trim-before-add: `maintain` steps sourced from `overtest_tests[]` or over-calibration signals execute before `exclude` and `add` steps in same epoch.

## Epoch loop (`complete-missing`)

Default `--max-epochs`: 3 (safety cap — not an expected exit path; see [input-resolution.md](input-resolution.md)).

```
assess → exit? → identify-missing → plan → write → verify → reassess → exit or continue
```

### Exit semantics (strict gates)

| Condition | `exit_reason` | `final_status` |
|-----------|---------------|----------------|
| Reassess: all scopes `pass`, zero `flagged` findings, `enumeration_complete: true` on assess + identify-missing | `quality_gate_met` | `ok` |
| All remaining gaps resolved via exclude track + `coverage_verify.passed` (or skipped per coverage-exclusions) | `exclusions_applied` | `ok` |
| User-recorded `wontfix` covers every remaining `flagged` item | `wontfix_acknowledged` | `ok` |
| Write `oracle_check.passed` is false after retry | `oracle_failed` | `failed` |
| Verify rerun `passed` is false | `verify_failed` | `failed` |
| Phase returns `enumeration_complete: false` | `enumeration_incomplete` | `failed` (hard-stop, no next epoch) |
| `epoch >= max_epochs` with any `flagged` not `wontfix` | `epoch_budget_exhausted` | `partial` |

**No `acceptable_residual` or `overtest_gate_met` success exits.** Overtest, redundant, and maintainability findings are `flagged` rows like any other — chain exits `ok` only when zero `flagged` remain (or all covered by `wontfix`).

### Per-epoch invariants

- **Enumeration:** assess and identify-missing must set `enumeration_complete: true` or orchestrator hard-stops with `enumeration_incomplete`.
- **Maintain before exclude before add:** epoch N cannot start write `exclude` track until all `maintain` steps are `solved`, `fixed`, or user `wontfix`; cannot start `add` until all `exclude` steps are `excluded`, `fixed`, or user `wontfix`.
- **Write completeness:** write must execute every plan step in order (`maintain` → `exclude` → `add`); unexecuted steps without user `wontfix` → write `status: partial`.
- **Reassess:** mandatory after write in complete-missing; must re-run full exhaustive assess (not delta-only).
- **Carry-over:** only `wontfix` and `fixed` persist across epochs; `flagged` must shrink each epoch or signal stuck skill quality.
- **write:** Must run test command, validation pipeline, and oracle check before epoch counts as complete.
- **verify** (fix/migrate/complete-missing): Rerun implicated tests; `exit_code === 0` required.

## Verify and reassess gates

| Flow | Verify required | Reassess required |
|------|-----------------|-------------------|
| `write` (standalone) | yes | no |
| `complete-missing` | yes | yes (each epoch) |
| `fix-broken` | yes | optional (chain includes assess) |
| `migrate` | yes | yes (final assess) |

Skill blocks completion declaration if verify fails, even when agent returns `status: ok`.

## Oracle validation (write phase)

Chain exit requires `oracle_check.passed: true`. Gate definition lives here; tactics live in `agents/test/write.md`.

## Finding status lifecycle (markdown output)

Applies when `--output md` (see [output-formats.md](output-formats.md)). Inter-agent contract remains JSON `PhaseOutput`.

| Status | Meaning | Set by |
|--------|---------|--------|
| `flagged` | Issue identified, no action yet | assess, identify-missing, flaky, perf-audit |
| `solved` | Change applied this run | write, fix, migrate (`changes` / `fixes` / `artifacts`) |
| `fixed` | Verified — tests green + reassess pass or oracle ok | verify + reassess for that scope |
| `excluded` | Coverage exclusion applied and verified | write exclude track + `coverage_verify` |
| `wontfix` | Acknowledged, intentionally deferred | user prompt only (plan `constraints_applied` with `source: "user"`) |

### Transition rules

1. New findings always start `flagged`.
2. `solved` requires matching entry in write `changes[]`, fix `fixes[]`, or migrate `steps_executed[]` for that path/kind.
3. `fixed` requires verify `passed: true` AND (reassess scope `pass`/`warn` without the same high-severity signal OR write `oracle_check.passed` for that path).
4. Epoch carry-over: unresolved `flagged` persist into next epoch report; `fixed` rows kept for audit trail.
5. `excluded` requires write `coverage_exclude` step completed and `coverage_verify.passed: true` (or `validation_pipeline.coverage_verify.skipped: true` when no coverage tooling). Transitions like `fixed` for residual clearing.
6. `wontfix` only via explicit user constraint in `payload.constraints.wontfix[]` or user prompt text recorded in plan `constraints_applied` with `source: "user"`. Agents must not self-assign `wontfix`.
7. **Hard-stop:** plan/write must not record `wontfix` without `constraints_applied[].source === "user"`.
8. **Residual rule:** anything still `flagged` at chain end blocks `final_status: ok` unless marked user `wontfix` or `excluded`. Agent-origin wontfix for non-testable files is invalid — those must route through exclude track.

### ID stability

Findings use `F{n}`, missing `M{n}`, excluded `X{n}`, plan `P{n}` / exclude `E{n}` within a run. Status updates merge on `(ID)` or `(path, kind)` when ID absent.
