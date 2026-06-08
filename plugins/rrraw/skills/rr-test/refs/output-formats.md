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
3. Phase-specific highlights (max 5 bullets):

| Phase | Text highlights |
|-------|-----------------|
| assess | aggregate `verdict`, `counts` (include `overtest`) |
| identify-missing | top 3 `items` by priority |
| plan | count of `maintain` + `add` steps |
| write | files changed, execution pass/fail, oracle pass/fail |
| fix / migrate | fix/step count, rerun pass/fail |
| flaky | `likely_root_cause`, `severity` |
| debug | `diagnosis`, first fix_plan step |
| perf-audit | top 3 hotspots by `share_pct` |
| init-discovery | stack summary, blocking questions count |

4. Omit empty arrays and null fields.

## Mapping: chain → json

```json
{
  "action": "complete-missing",
  "resolution_trace": {},
  "epochs": [{ "epoch": 1, "phases": { "assess": {}, "write": {} } }],
  "exit_reason": "quality_gate_met",
  "final_status": "ok"
}
```

Include `resolution_trace` from input-resolution in root payload.

## Mapping: chain → md

Primary user-facing artifact. Apply [report-template.md](report-template.md).

### Status merge rules

1. Build findings rows from assess `signals`, `redundant_tests`, `overtest_tests`, identify-missing `items`, plan steps.
2. Initial status: `flagged` for all new findings ([determinism.md](determinism.md) § Finding status lifecycle).
3. After write/fix/migrate: matching paths → `solved`.
4. After verify + reassess (or oracle pass for standalone write): matching paths → `fixed`.
5. User `wontfix` from plan `constraints_applied` → `wontfix`.
6. Epoch carry-over: persist `flagged` from prior epoch; retain `fixed` for audit.

### Row construction by phase

| Source | ID prefix | Kind column |
|--------|-----------|-------------|
| assess `signals[]` | `F{n}` | `signals[].kind` |
| assess `overtest_tests[]` | `F{n}` | `over_assertion` |
| assess `redundant_tests[]` | `F{n}` | `redundancy` |
| identify-missing `items[]` | `M{n}` | `missing_coverage` |
| plan `maintain` / `add` | `P{n}` | `plan_maintain` / `plan_add` |
| write `changes[]` | link to finding ID | update status → `solved` |
| flaky / perf-audit | `F{n}` | phase-specific |

### Optional artifact I/O

On multi-epoch chains (`complete-missing`, `migrate` with epochs > 1): skill may write/overwrite `.rr-test/report.md` with the same markdown emitted to chat. Idempotent per run; optional — single-shot invocations need not write disk.

## Errors

Resolution errors (`AMBIGUOUS_ACTION`, etc.) format as:

- **text:** `Error: <code> — <message>`
- **json:** `{ "error": PhaseError, "resolution_trace": {} }`
- **md:** error header only; skip findings tables
