# success-criteria

**Owner:** Build-precise gate before final write — split **static** (script) vs **judgment** (compose/challenge).

**Load when:** Pre-write gate after compose chain completes (before pre-save reflection); also after each level’s Gate 3.

Item identity and DoR: [doc-standards/item-schema.md](doc-standards/item-schema.md).

## Gate overview

Planning docs are **not ready to write** until static checks pass and judgment criteria are accepted. Fail static → do not write (unless user accepts partial). Fail judgment → return to discovery/compose or surface clarifications.

Run from plugin root:

```bash
python3 scripts/validate_planning.py <output-dir>
```

`--challenge` static pass runs this script. Challenge agent does **not** re-check refs if the script ran. If the script was skipped, challenge may flag build-on-non-ready as judgment.

## Static (script)

`validate_planning.py` owns:

- Unique IDs; parent / supersede pointers exist; no cycles; no cascade-level skips
- Numbering density among siblings; max depth 2
- Kind invariant; `idea` has no children
- Required closed keys; spec/build legality (DoR-as-code)
- `spec == ready` ⇒ method fields present; cross-doc parent `ready` (same-doc container exempt)
- `build != none` ⇒ FRD leaf with `spec == ready`
- md headers or yaml closed keys vs `items.json` drift

Schema: [schemas/items.schema.json](schemas/items.schema.json).

Parent walk (no skips):

```
ES-n → MRD-n.m → BRD-n.m → PRD-n.m → FRD-n.m
```

| Result | Action |
|--------|--------|
| Script exit 0 | Static pass |
| Script FAIL | Fail → re-compose affected levels or fix `items.json` |
| Script skipped | Challenge may include ref/status findings; record `STATIC SKIPPED` |

## Judgment (compose / challenge)

AI owns — do not encode as script FAILs:

- Compound leaves (multiple shalls/actors/outcomes in one leaf)
- MoSCoW inflation; Kano mis-class; weak triad prose (`if_wrong` not a real blast radius)
- Vague AC ("fast", "user-friendly") without measurable proxy
- Shall not testable

### Testable acceptance criteria

Every `must-correct` / `must-present` FRD leaf must have:

- At least one Gherkin scenario (Given/When/Then)
- At least one error/edge path
- No vague language without measurable proxy

| Vague term | Required resolution |
|------------|---------------------|
| "Fast" | Latency target (e.g. p95 < 200ms) |
| "Secure" | Specific control or standard reference |
| "Scalable" | Concrete scale target (users, RPS, data volume) |
| "Easy to use" | Task-completion metric or usability criterion |

## Criterion: Zero unresolved ambiguity

- No open `clarifications_needed[]` unless user explicitly accepted gaps.
- No `assumptions` with `blocking: true` and `validated: false`.
- No conflicting facts across levels (per cascade inheritance rules).
- Decision log in `session-state.json` complete for all user-facing choices.
- Verbatim Q&A for those choices is in `raw-history/` (not a substitute for the decision log).

## Criterion: Decision traceability

Every recorded decision must:

- Have a `goal_ref` pointing to an `ES-*` id (vision or metric) when the exec-summary exists.
- Be `user_confirmed: true` (or explicitly accepted as assumption).
- Not contradict a later-level fact.

## Criterion: Doc-standard compliance

Each composed doc passes its doc-standard **done-when** checklist:

| Doc | Checklist owner |
|-----|-----------------|
| exec-summary | [doc-standards/exec-summary.md](doc-standards/exec-summary.md) |
| mrd | [doc-standards/mrd.md](doc-standards/mrd.md) |
| brd | [doc-standards/brd.md](doc-standards/brd.md) |
| prd | [doc-standards/prd.md](doc-standards/prd.md) |
| frd | [doc-standards/frd.md](doc-standards/frd.md) |

## Gate output

```json
{
  "gate_passed": true,
  "criteria": {
    "static": { "passed": true, "script": "validate_planning.py", "errors": [] },
    "traceability": { "passed": true, "orphans": [], "broken_links": [] },
    "acceptance_criteria": { "passed": true, "vague_terms": [] },
    "ambiguity": { "passed": true, "open_clarifications": [] },
    "decisions": { "passed": true, "unconfirmed": [] },
    "doc_standards": { "passed": true, "failures": [] }
  },
  "final_status": "ok"
}
```

`traceability` in this object is the script result (duplicated for the gate record). Judgment findings live under `acceptance_criteria` / `doc_standards`.

| `gate_passed` | `final_status` |
|---------------|----------------|
| `true` | `ok` |
| `false`, fixable | `partial` — write docs with warning header |
| `false`, blocking | Do not write; return to discovery |

## Partial write policy

When `gate_passed: false` but user accepts partial:

- Prepend warning to each doc:

```markdown
> **Status: PARTIAL** — Success criteria not fully met. See session-state.json assumptions/decisions and raw-history/ for gaps.
```

YAML equivalent: `status: PARTIAL` at document root plus the same sentence in `warning`.

- List failing criteria in `session-state.json` (`checkpoint.pending_clarifications` and unvalidated `assumptions[]`). Do not write `session-log.md`.
- Set `final_status: partial` in output metadata.
