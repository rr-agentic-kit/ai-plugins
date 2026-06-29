# success-criteria

**Owner:** Build-precise gate before final write — traceability, testable acceptance criteria, zero unresolved ambiguity.

**Load when:** Pre-write gate after compose chain completes.

## Gate overview

Planning docs are **not ready to write** until all criteria below pass. Fail → return to discovery/compose or surface clarifications.

## Criterion 1: Traceability chain

Every FRD requirement must trace upward:

```
fr-N → prd-story-N → prd-goal-N → brd-obj-N → exec-metric-N (or exec-vision)
```

Validation:

1. Parse all `traces_to` / `goal_ref` links in composed docs.
2. Flag orphan requirements (no parent).
3. Flag broken links (parent id does not exist).
4. Flag requirements that skip a level (fr → exec without intermediate links).

| Result | Action |
|--------|--------|
| Zero orphans, zero broken links | Pass |
| Orphans or broken links | Fail → re-compose affected levels |

## Criterion 2: Testable acceptance criteria

Every P0 functional requirement in FRD must have:

- At least one Gherkin scenario (Given/When/Then)
- At least one error/edge path for P0 reqs
- No vague language ("fast", "user-friendly") without measurable proxy

| Vague term | Required resolution |
|------------|---------------------|
| "Fast" | Latency target (e.g. p95 < 200ms) |
| "Secure" | Specific control or standard reference |
| "Scalable" | Concrete scale target (users, RPS, data volume) |
| "Easy to use" | Task-completion metric or usability criterion |

## Criterion 3: Zero unresolved ambiguity

- No open `clarifications_needed[]` unless user explicitly accepted gaps.
- No `assumptions` with `blocking: true` and `validated: false`.
- No conflicting facts across levels (per cascade inheritance rules).
- Decision log complete for all user-facing choices.

## Criterion 4: Decision traceability

Every recorded decision must:

- Have a `goal_ref` pointing to exec-summary vision or metric.
- Be `user_confirmed: true` (or explicitly accepted as assumption).
- Not contradict a later-level fact.

## Criterion 5: Doc-standard compliance

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
    "traceability": { "passed": true, "orphans": [], "broken_links": [] },
    "acceptance_criteria": { "passed": true, "vague_terms": [] },
    "ambiguity": { "passed": true, "open_clarifications": [] },
    "decisions": { "passed": true, "unconfirmed": [] },
    "doc_standards": { "passed": true, "failures": [] }
  },
  "final_status": "ok"
}
```

| `gate_passed` | `final_status` |
|---------------|----------------|
| `true` | `ok` |
| `false`, fixable | `partial` — write docs with warning header |
| `false`, blocking | Do not write; return to discovery |

## Partial write policy

When `gate_passed: false` but user accepts partial:

- Prepend warning to each doc:

```markdown
> **Status: PARTIAL** — Success criteria not fully met. See session-log.md for gaps.
```

- List failing criteria in `session-log.md`.
- Set `final_status: partial` in output metadata.
