# output-formats

**Owner:** Adapt structured `PhaseOutput` (and chain results) to user-facing response modes.

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| `text` | default | Concise plain-text summary for chat |
| `json` | `--output json` | Full structured payload |
| `report` | `--output report` | Long-form markdown via [report-template.md](report-template.md) |

## Mapping: PhaseOutput → text

1. Print `summary` line first.
2. If `status === failed`, print `data.error.message` or top failure reason.
3. Phase-specific highlights (max 5 bullets):

| Phase | Text highlights |
|-------|-----------------|
| assess | aggregate `verdict`, `counts` |
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

## Mapping: chain → report

1. Apply [report-template.md](report-template.md) sections in order.
2. Populate from final epoch phase outputs.
3. No additional orchestration semantics in report mode.

## Errors

Resolution errors (`AMBIGUOUS_ACTION`, etc.) format as:

- **text:** `Error: <code> — <message>`
- **json:** `{ "error": PhaseError, "resolution_trace": {} }`
- **report:** error section only; skip template body
