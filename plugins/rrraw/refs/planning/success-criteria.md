# success-criteria

**Owner:** Build-precise gate before freeze/accept — split **static** (script) vs **judgment** (compose/challenge).

**Load when:** Pre-freeze/accept gate after compose chain completes (before pre-save reflection); also after each level’s Gate 3.

Item identity and DoR: [doc-standards/item-schema.md](doc-standards/item-schema.md).

## Gate overview

Planning docs are **not ready to freeze/accept** until static checks pass and judgment criteria are accepted. Files on disk are drafts until freeze. Fail static → do not freeze/accept (unless user accepts partial). Fail judgment → return to discovery/compose or surface clarifications.

Run from plugin root:

```bash
sh scripts/validate_planning.sh <output-dir>
```

`--challenge` static pass runs this script. Challenge agent does **not** re-check refs if the script ran.

## Static (script)

`validate_planning.sh` owns:

- Unique IDs; parent / supersede pointers exist; no cycles; no cascade-level skips
- Numbering density among siblings; max depth 2
- Kind invariant; `idea` has no children
- Required closed keys; spec legality (DoR-as-code)
- `spec == ready` ⇒ real rank present (`—` does not count); cross-doc parent `ready` (same-doc container exempt)
- md `_key_:` headers vs `items.json` drift
- Ranked-leaf `Rationale` present and resolving when `decision-ledger.yaml` exists (`LEDGER_MISSING` is a warning and skips these checks)
- When `status.yaml` exists: `PARENT_UNFROZEN`, `STALE_PIN`, `REV_WHILE_OPEN`, `HAND_BUMP` ([baselines.md](baselines.md)). Do **not** FAIL major/minor policy, `NEXT_LOCKED`, or `CURRENT_NOT_PATCH`. Independent product/docs patches are valid. `future.md` and `agent.plan.md` are not script input. **PR CI** (setup-installed) is the authoritative fail-closed path — local-only is insufficient ([setup.md](setup.md)).

Schema: [schemas/items.schema.json](schemas/items.schema.json).

Parent walk (no skips):

```
ES-n → MRD-n.m → BRD-n.m → PRD-n.m
```

| Result | Action |
|--------|--------|
| Script exit 0 | Static pass |
| Script FAIL | Fail → re-compose affected levels (compose overwrites the doc + `items.json`) |
| Script skipped | Challenge may include ref/status findings; record `STATIC SKIPPED` |

## Judgment (compose / challenge)

AI owns — do not encode as script FAILs:

- Compound leaves (multiple shalls/actors/outcomes in one leaf)
- MoSCoW inflation vs the posture legend; Kano mis-class
- Vague AC ("fast", "user-friendly") without measurable proxy
- Shall not testable
- Posture unconfirmed or missing ES Posture **section**; Must set disagrees with the legend (`signed_v1` re-cut as MVP, shipped behavior as new Must under `existing`)
- Frozen level still has leftover `partial` notes the user has not discarded or completed
- Must / `must-correct` item rests on a `vague` `flips_when` (fabricated numbers are worse — call those out too)
- Binding viability `hold`/`kill` unresolved; open re-decision queue
- Unlock / patch-only-current / "this looks like a minor" (skill classify in [baselines.md](baselines.md) — never script FAILs)

Do **not** encode posture or note-session checks as `validate_planning.sh` FAILs. Sidecars are not script input.

Vague terms (any level — do not restate per-level Gherkin done-when here):

| Vague term | Required resolution |
|------------|---------------------|
| "Fast" | Latency target (e.g. p95 < 200ms) |
| "Secure" | Specific control or standard reference |
| "Scalable" | Concrete scale target (users, RPS, data volume) |
| "Easy to use" | Task-completion metric or usability criterion |

## Criterion: Viability

- Exec-summary has What-must-be-true and Viability-verdict **prose sections**. Missing prose is judgment, never a script FAIL.
- `session_state.viability[]` has an entry for each frozen level.
- Binding `hold`/`kill` (ES, MRD) unresolved → not `ok`; docs carry the VIABILITY HOLD banner; `gate_passed: false`.
- Accepted advisory `hold`/`kill` (BRD/PRD) does not block `ok` (still record; banner only on binding-level `hold`).
- `kill` without a revival trigger in the ledger is a failure.
- Dissent is recorded, not averaged.

## Criterion: Rationale coverage

- Every ranked leaf has `_rationale_: r-NNN` pointing at a live (or explicitly `superseded`) ledger record.
- Leaves without a real rank and containers may omit it.
- Open `re_decision_queue` (`status: open`) is **blocking** — drain before freeze/accept.
- A Must or `must-correct` resting on `condition_strength: vague` is a judgment finding, never a script FAIL.

## Criterion: Zero unresolved ambiguity

- No open `clarifications_needed[]` unless user explicitly accepted gaps.
- No `assumptions` with `blocking: true` and `validated: false`.
- No conflicting facts across levels (per cascade inheritance rules).
- Decision log in `session-state.json` complete for all user-facing choices (`project_posture` confirmed; `scope_change` / `note_routed` when those paths ran).
- Verbatim Q&A for those choices is in `raw-history/` (not a substitute for the decision log).
- No leftover `partial` notes on frozen levels ([note-sessions.md](../../skills/rr-planner/refs/note-sessions.md)).

## Criterion: Decision traceability

Every recorded decision must:

- Have a `goal_ref` pointing to a ranked `ES-*` id (usually a metric) when the executive-summary exists. `project_posture` logged before a metric exists may fill `goal_ref` on the next compose once a metric is minted.
- Be `user_confirmed: true` (or explicitly accepted as assumption).
- Not contradict a later-level fact.

## Criterion: Doc-standard compliance

Each composed doc passes its doc-standard **done-when** checklist. Do not restate those ticks here.

| Doc | Checklist owner |
|-----|-----------------|
| executive-summary | [doc-standards/executive-summary.md](../../skills/rr-discovery/refs/doc-standards/executive-summary.md) |
| mrd | [doc-standards/mrd.md](../../skills/rr-discovery/refs/doc-standards/mrd.md) |
| brd | [doc-standards/brd.md](../../skills/rr-discovery/refs/doc-standards/brd.md) |
| prd | [doc-standards/prd.md](../../skills/rr-planner/refs/doc-standards/prd.md) |

## Gate output

```json
{
  "gate_passed": true,
  "criteria": {
    "static": { "passed": true, "script": "validate_planning.sh", "errors": [] },
    "traceability": { "passed": true, "orphans": [], "broken_links": [] },
    "acceptance_criteria": { "passed": true, "vague_terms": [] },
    "ambiguity": { "passed": true, "open_clarifications": [] },
    "decisions": { "passed": true, "unconfirmed": [] },
    "doc_standards": { "passed": true, "failures": [] },
    "posture": { "passed": true, "existence": "greenfield", "commitment": "unsigned" },
    "notes": { "passed": true, "partial_on_frozen": [] },
    "viability": { "passed": true, "verdict": "proceed", "open_queue": [] },
    "rationale_coverage": { "passed": true, "missing": [] }
  },
  "final_status": "ok"
}
```

`traceability` in this object is the script result (duplicated for the gate record). Judgment findings live under `acceptance_criteria` / `doc_standards` / `posture` / `notes` / `viability` / `rationale_coverage`. `posture`, `notes`, condition quality, and an open re-decision queue are never script FAILs (queue is a process block). Missing ranked-leaf rationale is a script FAIL when the ledger file exists.

| `gate_passed` | `final_status` |
|---------------|----------------|
| `true` | `ok` |
| `false`, fixable | `partial` — keep drafts; prepend warning header |
| `false`, blocking | Do not freeze/accept; return to discovery |

## Partial accept policy

When `gate_passed: false` but user accepts partial:

- Prepend warning to each doc already on disk (skill mutates files; do not restash bodies through chat):

```markdown
> **Status: PARTIAL** — Success criteria not fully met. See session-state.json assumptions/decisions and raw-history/ for gaps.
```

Binding viability `hold` uses this banner instead (do not freeze; do not set `final_status: ok`):

```markdown
> **Status: VIABILITY HOLD** — Missing evidence is named in session-state.json `viability[]` and decision-ledger.yaml. Do not treat this plan as accepted.
```

- List failing criteria in `session-state.json` (`checkpoint.pending_clarifications` and unvalidated `assumptions[]`). Do not write `session-log.md`.
- Set `final_status: partial` in output metadata.
