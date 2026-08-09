# output-formats

**Owner:** Adapt structured `PhaseOutput` (and chain results) to user-facing response modes.

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| `md` | default (`--output md`) | Structured markdown tables with status column via [report-template.md](report-template.md) |
| `text` | `--output text` | Concise plain-text summary for chat |
| `json` | `--output json` | Full structured payload |
| `report` | `--output report` | **Alias for `md`** — normalize to `md` before formatting |

## Three-layer architecture

| Layer | Format |
|-------|--------|
| Inter-agent | JSON `PhaseOutput` — determinism parse unchanged |
| Default user output | `md` — findings work queue with status |
| Quick chat | `text` |
| Automation | `json` |

## Mapping: PhaseOutput → text

1. Print `summary` line first.
2. If `status === failed`, print `data.error.message` or top failure reason.
3. Phase-specific highlights:

| Phase | Text highlights |
|-------|-----------------|
| assess | aggregate `verdict`, `counts` (include `overtest`), `enumeration_complete` |
| identify-missing | all `items` by priority + `excluded` count (or count + "see md" when >10) |
| plan | count of `maintain` + `exclude` + `add` steps; `maintain_before_exclude_before_add` flag |
| write | files changed, steps completed/skipped, coverage verify, execution pass/fail, oracle pass/fail |
| fix / migrate | fix/step count, rerun pass/fail |
| flaky | `likely_root_cause`, `severity` |
| debug | `diagnosis`, first fix_plan step |
| perf-audit | top 3 hotspots by `share_pct` |
| init-discovery | stack summary, blocking questions count |

4. When `final_status === partial`, print residual count and re-run guidance.
5. Omit empty arrays and null fields.

## Mapping: chain → json

```json
{
  "action": "complete-missing",
  "resolution_trace": {},
  "epochs": [{ "epoch": 1, "phases": { "assess": {}, "write": {} } }],
  "exit_reason": "quality_gate_met",
  "final_status": "ok",
  "residual_count": 0
}
```

Include `resolution_trace` from input-resolution in root payload. When `final_status` is `partial`, include `residuals[]` with all `flagged` findings.

## Mapping: chain → md

Primary user-facing artifact. Apply [report-template.md](report-template.md).

### Status merge rules

1. Build findings rows from assess `signals`, `redundant_tests`, `overtest_tests`, identify-missing `items`, plan steps.
2. Initial status: `flagged` for all new findings ([determinism.md](determinism.md) § Finding status lifecycle).
3. After write/fix/migrate: matching paths → `solved`.
4. After verify + reassess (or oracle pass for standalone write): matching paths → `fixed`.
5. Write exclude track + `coverage_verify.passed` → `excluded`.
6. User `wontfix` from plan `constraints_applied` (source: `user`) → `wontfix`.
7. Epoch carry-over: persist `flagged` from prior epoch; retain `fixed` for audit.
8. At chain end: any remaining `flagged` (not `wontfix`) → emit Residuals section; `final_status: partial` when `exit_reason: epoch_budget_exhausted`.

### Row construction by phase

| Source | ID prefix | Kind column |
|--------|-----------|-------------|
| assess `signals[]` | `F{n}` | `signals[].kind` |
| assess `overtest_tests[]` | `F{n}` | `over_assertion` |
| assess `redundant_tests[]` | `F{n}` | `redundancy` |
| identify-missing `items[]` | `M{n}` | `missing_coverage` |
| identify-missing `excluded[]` | `X{n}` | `non_testable` |
| plan `maintain` / `exclude` / `add` | `P{n}` / `E{n}` | `plan_maintain` / `plan_exclude` / `plan_add` |
| write `changes[]` | link to finding ID | update status → `solved` |
| flaky / perf-audit | `F{n}` | phase-specific |

### Optional artifact I/O

On multi-epoch chains (`complete-missing`, `migrate` with epochs > 1): skill may write/overwrite `.rr-test/report.md` with the same markdown emitted to chat. Idempotent per run; optional — single-shot invocations need not write disk.

## Errors

Resolution errors (`AMBIGUOUS_ACTION`, etc.) format as:

- **text:** `Error: <code> — <message>`
- **json:** `{ "error": PhaseError, "resolution_trace": {} }`
- **md:** error header only; skip findings tables
