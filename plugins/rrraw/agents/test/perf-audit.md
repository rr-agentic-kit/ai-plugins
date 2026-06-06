# perf-audit

Function-style executor for `--audit-test-performance`.

## Input

`PhaseInput` with `phase: "perf-audit"`.

Required:
- `payload.scope` (suite, module, or paths)
- Suite timing data from test runner profile or user-supplied metrics

## Execution

1. Collect per-test or per-file durations.
2. Rank `hotspots` by `share_pct` of `suite_total_ms`.
3. Propose `optimization_plan` with expected gain (parallelize, mock I/O, split fixtures, etc.).

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-test/refs/contracts.md) § perf-audit.

## Constraints

- Audit and plan only; no automatic refactor (user may follow with fix/write).
