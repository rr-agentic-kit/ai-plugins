# shared-heuristics

**Owner:** Cross-phase quality heuristics only. No workflow or routing logic.

Used by: assess, identify-missing, flaky (severity), identify-redundant (via assess), plan (calibration), write (assertion tactics).

## Verdict definitions

| Verdict | Meaning |
|---------|---------|
| `pass` | Adequate coverage of protected behavior; assertions calibrated to test role; no high-severity gaps in scope |
| `warn` | Tests exist but under- or over-calibrated, partial, redundant, or maintainability issues; medium gaps; flakiness risk |
| `fail` | Missing critical tests, broken suite, or assertions that cannot detect regressions |

Aggregate scope verdict: worst of child file verdicts (`fail` > `warn` > `pass`).

## Assertion calibration model

Calibration = assertion specificity matched to **test role**. Both under- and over-calibration degrade signal.

| Calibration | Symptom | Typical verdict impact |
|-------------|---------|------------------------|
| **Under** | `not null`, mock-only, `assertDoesNotThrow`, no error-path checks | `warn` or `fail` on critical paths |
| **Right** | Asserts observable outcomes for the behavior under test; stable across refactors | supports `pass` |
| **Over** | Full-object deep equality, snapshot of internals, asserting implementation details | `warn`; may block `pass` when widespread |

### Test role → assertion guidance

| Role | Assert | Avoid |
|------|--------|-------|
| Unit | Return value, state change, side-effect on port | Private fields, full DTO equality when 2 fields matter |
| Integration | Boundary contract, persistence, message shape (key fields) | Duplicating unit assertions on same code path |
| E2E | User-visible outcome, critical path status | Every intermediate DTO field |
| Error path | Exception type/code, error payload essentials | Exact full stack trace text |

Google sizing heuristic (plan phase): **S** = single behavior, minimal arrange; **M** = one collaboration; **L** = multi-step flow — prefer splitting L into S/M rather than one over-asserted L test.

## Redundancy signals

Flag as redundant when **two or more** apply:

- Duplicate assertion of the same outcome via copy-pasted cases
- Testing framework/library behavior instead of project code
- Multiple tests with identical arrange-act; only trivial assert variation
- Snapshot churn with no behavioral assertion
- E2E duplicating unit coverage with no additional integration signal

Output: `redundant_tests[]` on assess contract ([contracts.md](contracts.md)).

## Overtest signals (`overtest_tests[]`)

Flag when **one or more** apply (distinct from redundancy — same test may be redundant *and* over-asserted):

- Full-object `equals` / deep-equal on DTOs where ≤3 fields are behaviorally relevant
- Snapshot of entire response/HTML/JSON when behavioral contract is subset of fields
- Asserting private methods, internal cache keys, or log line ordering
- Multiple assertions on unrelated dimensions in one test (multi-behavior smell)
- Mock verify on calls that are not part of the behavior under test

Output: `overtest_tests[]` on assess contract. Count in `counts.overtest`.

Severity: `medium` for isolated cases; `high` when pattern blocks refactor or masks real failures.

## Weak assertion patterns (under-calibration)

Treat as `warn` or downgraded confidence:

- Assert only `not null` / truthy on complex objects
- Mock-only tests with no interaction verification
- `assertDoesNotThrow` as sole behavioral check
- Hard-coded dates/IDs without factory control
- Sleep-based synchronization without condition waits

Signal kind: `weak_assertion`.

## Maintainability signals

Treat as `warn` when clarity or change cost is high:

- **Mystery guest** — opaque fixtures/data with no link to scenario name
- **Unclear intent** — test name does not describe behavior; comments explain what code does
- **Multi-behavior** — one test verifies unrelated outcomes (split candidate for plan `maintain`)
- **Conditional logic** in test body obscuring arrange-act-assert
- **Magic numbers/strings** without named constants or factory

Signal kinds: `maintainability`, `multi_behavior`.

## Mock and boundary rules

| Pattern | Verdict signal |
|---------|----------------|
| Mock replaces type under test | `implementation_coupling` — often `fail` |
| Over-mocking collaborators (entire subgraph stubbed) | `mock_boundary` — `warn` |
| Verify every call on mock regardless of behavior | `over_mock_verify` — `warn` |
| Test hits real boundary (DB, HTTP) with no isolation where unit intended | `boundary_leak` — context-dependent |

Prefer testing through public API; use test doubles at **collaborator** boundaries only.

## Test smell cross-reference

Map findings to [testsmells.org](https://testsmells.org) catalog when applicable. Set optional `smell_id` on signal.

| Smell (testsmells.org) | Signal kind | Direction |
|------------------------|-------------|-----------|
| Assertion Roulette | `weak_assertion` | under |
| Sensitive Equality | `over_assertion` | over |
| Mystery Guest | `maintainability` | maintainability |
| Eager Test | `multi_behavior` | over/maintainability |
| Duplicate Assert | `redundancy` | redundant |
| Lazy Test | `weak_assertion` | under |
| Magic Number Test | `maintainability` | maintainability |
| Redundant Print | `maintainability` | low severity |
| General Fixture | `maintainability` | maintainability |

## AI-generated test artifacts

Flag when typical LLM failure modes appear:

| Pattern | Signal kind | Severity |
|---------|-------------|----------|
| Empty or placeholder test (`TODO`, `assertTrue(true)`) | `ai_artifact` | high |
| Tests for non-existent API / hallucinated imports | `ai_artifact` | high |
| Spec drift — test asserts outdated contract vs production | `ai_artifact` | high |
| Verbose boilerplate with no distinct cases | `ai_artifact` | medium |
| Copy-paste cases with renamed strings only | `redundancy` + `ai_artifact` | medium |

Write phase must run validation pipeline (compile → run → oracle → optional mutation spot-check) per [agents/test/write.md](../../../agents/test/write.md).

## Mutation gap heuristic

When coverage tools report green but assertions are weak, flag `mutation_gap`:

- High line coverage + `weak_assertion` signals on same path
- No assertion on branch that differs from happy path only by return value
- Research consensus: mutation score better fault-detection signal than raw coverage alone

Severity: `medium` default; `high` on payment/auth/data mutation paths.

Do not require bundled PIT/Stryker — heuristic only unless project already runs mutation tooling.

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
|------|---------|
| `high` | Public API, payment/auth, data mutation, concurrency |
| `medium` | Branching logic, error paths, integration boundaries |
| `low` | Trivial getters, thin delegates with testable behavior |

**Low-risk routing:** When low-risk signals coincide with a non-testable category from [coverage-exclusions.md](coverage-exclusions.md), assess emits `non_testable` (not `missing_test`). Low-risk + testable behavior → `missing_test` with `risk: low`.

## Exhaustive enumeration

No sampling, no "top N". Every file in normalized scope gets a row; every signal in scope gets emitted.

### Production surface definition

Per detected stack, enumerate:

| Stack | Surfaces to score |
|-------|-------------------|
| Backend (Java/Kotlin/C#) | Public types, exported functions, REST handlers, service methods |
| Frontend (React/Vue) | Components with logic (not pure layout), hooks, stores |
| CLI / scripts | Commands, subcommands, entry points |
| DevOps | Pipeline stages with testable logic, config validators |

### Test pairing

- Every production file in `scope_manifest.production_files` must map to ≥0 test files.
- **Classify first** per [coverage-exclusions.md](coverage-exclusions.md) non-testable taxonomy.
- Non-testable production file → emit `non_testable` (required); do **not** emit `missing_test`.
- Testable production file with no test file → emit `missing_test` (required).
- When test exists but gaps remain → emit `missing_coverage` on specific behaviors.

### Redundant + overtest scan

- Every test method in scope must be scanned for redundancy and overtest signals — not only files with obvious smells.
- `redundant_tests[]` and `overtest_tests[]` counts must reconcile with per-scope `signals[]`.

### identify-missing reconciliation

Three-bucket invariant (must reconcile):

```
items.length + excluded.length + adequately_covered.length === production_files.length
uncovered_production_paths must be empty
```

- Emit an `items[]` entry for every `missing_test` and `missing_coverage` signal from assess.
- Emit an `excluded[]` entry for every `non_testable` signal from assess.
- `excluded[]` paths must **not** appear in `items[]` or `uncovered_production_paths`.
- `enumeration_complete: true` only when reconciliation holds and `uncovered_production_paths` is empty.
- Sort `items[]` by priority ascending, then `production_path` lexicographically — **no truncation**.

## Signal kind enum (assess `signals[].kind`)

Standard values for `signals[].kind`:

| Kind | Category |
|------|----------|
| `weak_assertion` | under-calibration |
| `over_assertion` | over-calibration |
| `redundancy` | duplicate coverage |
| `maintainability` | clarity / change cost |
| `multi_behavior` | should split |
| `implementation_coupling` | private API / internal snapshot |
| `mock_boundary` | mock misuse |
| `over_mock_verify` | excessive verify |
| `boundary_leak` | wrong test level |
| `flakiness_risk` | non-determinism |
| `missing_coverage` | gap (scope-level) |
| `ai_artifact` | LLM-generated defect |
| `mutation_gap` | weak fault detection |
| `missing_test` | no test file for testable production path |
| `non_testable` | production path excluded from coverage (resolution, not gap) |

Optional `non_testable_reason` on signal evidence when kind is `non_testable` (category from coverage-exclusions.md).

Optional `smell_id`: testsmells.org identifier (e.g. `SensitiveEquality`).

Severity: `low` | `medium` | `high` per signal; aggregate scope verdict per tables above.
