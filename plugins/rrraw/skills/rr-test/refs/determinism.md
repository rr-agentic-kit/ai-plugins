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
| `epoch >= max_epochs` | `epoch_budget_exhausted` |
| Write `oracle_check.passed` is false after retry | `oracle_failed` |
| Verify rerun `passed` is false | `verify_failed` |

### Per-epoch requirements

- **write:** Must run test command and oracle check before epoch counts as complete.
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
