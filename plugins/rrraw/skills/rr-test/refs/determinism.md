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

## Plan merge rules (maintain + add)

When combining plan tracks or epoch carry-over:

1. Dedupe by `(action, path)`; later epoch wins on conflict.
2. Sort by `priority` ascending, then `path` lexicographically.
3. Tie-break equal priority: `risk` high > medium > low (from identify-missing linkage when available).
4. `maintain` track processed before `add` track in execution order.
5. Trim-before-add: `maintain` steps sourced from `overtest_tests[]` or over-calibration signals execute before `add` steps in same epoch.

## Epoch loop (`complete-missing`)

Default `--max-epochs`: 3.

```
assess → exit? → identify-missing → plan → write → verify → reassess → exit or continue
```

### Exit semantics (any satisfied → stop chain)

| Condition | Exit reason |
|-----------|-------------|
| Reassess `verdict` is `pass` for all in-scope production files | `quality_gate_met` |
| Reassess has zero `fail` and zero high-priority missing items | `acceptable_residual` |
| Reassess has zero high-severity `overtest_tests[]` and zero high `over_assertion` signals in scope | `overtest_gate_met` (combined with acceptable residual when overtest was flagged) |
| `epoch >= max_epochs` | `epoch_budget_exhausted` |
| Write `oracle_check.passed` is false after retry | `oracle_failed` |
| Verify rerun `passed` is false | `verify_failed` |

### Overtest gate (epoch quality)

After **reassess** in complete-missing chains:

1. If prior epoch assess had `counts.overtest > 0` or any high-severity `over_assertion` / `ai_artifact` signal:
   - Reassess must show `counts.overtest === 0` and no high-severity `over_assertion` / `ai_artifact` for chain to exit via `acceptable_residual` or `quality_gate_met`.
2. Medium-severity residual overtest may exit only when zero `fail` scopes and no high-priority missing items.
3. Skill surfaces unresolved overtest in markdown findings with status `flagged` until cleared or `wontfix` (user constraint).

### Per-epoch requirements

- **write:** Must run test command, validation pipeline, and oracle check before epoch counts as complete.
- **verify** (fix/migrate/complete-missing): Rerun implicated tests; `exit_code === 0` required.
- **reassess:** Mandatory after write in complete-missing; optional after fix-broken.

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
| `wontfix` | Acknowledged, intentionally deferred | user prompt or plan constraint |

### Transition rules

1. New findings always start `flagged`.
2. `solved` requires matching entry in write `changes[]`, fix `fixes[]`, or migrate `steps_executed[]` for that path/kind.
3. `fixed` requires verify `passed: true` AND (reassess scope `pass`/`warn` without the same high-severity signal OR write `oracle_check.passed` for that path).
4. Epoch carry-over: unresolved `flagged` persist into next epoch report; `fixed` rows kept for audit trail.
5. `wontfix` only via explicit user constraint recorded in plan `constraints_applied`.

### ID stability

Findings use `F{n}`, missing `M{n}`, plan `P{n}` within a run. Status updates merge on `(ID)` or `(path, kind)` when ID absent.
