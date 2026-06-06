# shared-heuristics

**Owner:** Cross-phase quality heuristics only. No workflow or routing logic.

Used by: assess, identify-missing, flaky (severity), identify-redundant (via assess).

## Verdict definitions

| Verdict | Meaning |
|---------|---------|
| `pass` | Adequate coverage of protected behavior; assertions are meaningful; no high-severity gaps in scope |
| `warn` | Tests exist but weak, partial, or redundant; medium gaps; flakiness risk |
| `fail` | Missing critical tests, broken suite, or assertions that cannot detect regressions |

Aggregate scope verdict: worst of child file verdicts (`fail` > `warn` > `pass`).

## Redundancy signals

Flag as redundant when **two or more** apply:

- Duplicate assertion of the same outcome via copy-pasted cases
- Testing framework/library behavior instead of project code
- Multiple tests with identical arrange-act; only trivial assert variation
- Snapshot churn with no behavioral assertion
- E2E duplicating unit coverage with no additional integration signal

Output: `redundant_tests[]` on assess contract ([contracts.md](contracts.md)).

## Weak assertion patterns

Treat as `warn` or downgraded confidence:

- Assert only `not null` / truthy on complex objects
- Mock-only tests with no interaction verification
- `assertDoesNotThrow` as sole behavioral check
- Hard-coded dates/IDs without factory control
- Sleep-based synchronization without condition waits

## Flakiness severity categories

| Severity | Indicators |
|----------|------------|
| `low` | Rare timeout; single env; passes on rerun |
| `medium` | Order-dependent; shared static state; clock sensitivity |
| `high` | Race in async/concurrency; parallel suite interference |
| `critical` | Non-deterministic pass rate >10%; blocks CI reliability |

## Missing-test risk heuristic

For identify-missing priority (skill may sort; agent assigns raw risk):

| Risk | Signals |
|------|-----------|
| `high` | Public API, payment/auth, data mutation, concurrency |
| `medium` | Branching logic, error paths, integration boundaries |
| `low` | Trivial getters, generated code, thin delegates |
