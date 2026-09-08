# Testability (coding lane)

Design production code so the test pyramid in [`test-types.md`](../../../quality/tester/refs/test-types.md) is achievable: **unit** on pure domain and validation, **integration** on boundaries (DB, HTTP, wiring), **E2E** on golden paths only.

**Overlap with tester lane:** Test strategy, verdicts, and pyramid classification live under **`skills/quality/tester`**. This ref covers **production seams** that make those tests possible. When the tester lane cannot close a gap without production edits, it emits a **cross-lane finding** — map remediation here and cite the matching **CPNNN** in code-review reports.

**Out of scope:** Missing Vitest/Playwright/Jest packages (test **infrastructure** per [`project-detection.md`](../../toolchain/refs/project-detection.md)); framework slice tests (`@WebMvcTest`, `@DataJpaTest`) as correct integration layers; inventing a separate rubric ID — use the **CP mapping** table below.

## Observable signals

| Signal | Likely cause | Primary CP |
|--------|--------------|------------|
| Only full stack (`@SpringBootTest`, k3d, live HTTP) can reach business rules | Domain not extracted from orchestration/I/O | **CP015** |
| Unit test needs many mocks for one production method | Mixed concerns; no ports at boundaries | **CP004**, **CP015** |
| Same behavior covered by mock-heavy unit **and** integration | Duplicate layer coverage — keep higher-value test | tester: **Duplicate layer coverage** |
| `new HttpClient()`, static clock, direct SQL/`fs` in domain path | Missing seam — inject port or move to adapter | **CP025** (boundary) |
| Inverted `LAYERS` line in test assess | Suite symptom — trace to production targets | see CP mapping |
| Isolated mapper/DTO tests + one big IT, no domain unit tests | Layer-tested-in-isolation anti-pattern | **CP015** / **CP023** |

## Prefer / Avoid

| Prefer | Avoid | Why |
|--------|-------|-----|
| Pure domain functions / value objects testable without framework | Business rules in controller, repository, YAML, or shell | Rules need fast unit oracles |
| Ports (interfaces) for DB, HTTP, queue, clock | Concrete infra types in domain/service constructors | Enables fakes without full mock chains |
| One integration test per boundary; many unit tests on rules | IT for every branch of pure logic | Slow feedback, hard to debug |
| Fakes at port boundary (in-memory repo, stub HTTP) | Mocking every collaborator of a god method | Weak oracles; refactor coupling |
| Test **behavior** at use-case entry (driver port) | Isolated tests for every mapper/DTO layer | Tests survive implementation refactors |
| Injectable `Clock` / randomness at boundary | `now()` / `random()` inside domain rules | Deterministic unit tests |

## Refactor recipes

Behavior-preserving extractions only. Refactor command: Phase **2** (long methods) and Phase **4** (cohesion) per [`srp-cohesion.md`](srp-cohesion.md).

| ID | Recipe | When |
|----|--------|------|
| **extract-pure-core** | Pull calculation/validation into a function or domain type; service orchestrates only | Logic is deterministic but buried in I/O-heavy method |
| **introduce-port** | Define repository/client interface; infra implements; unit tests use fake | Unit test would otherwise mock entire persistence or HTTP stack |
| **inject-time** | Accept `Clock` / time provider at boundary; domain uses injected time | Tests need deterministic expiry, SLA, or audit windows |
| **thin-boundary** | HTTP/CLI handler validates shape and delegates; no rules in handler | Rules duplicated or untestable at framework edge |

**Code-review Context:** `testability: <recipe-id>` plus **CPNNN** (e.g. `testability: extract-pure-core` + **CP015**).

## CP mapping

| Symptom | Primary CP | Recipe |
|---------|------------|--------|
| validate + calculate + persist + emit in one method | **CP015** | **extract-pure-core** |
| I/O + orchestration in same function body | **CP004** | **extract-pure-core** or **introduce-port** |
| Branch on dialect/driver/vendor string at call site | **CP025** | **introduce-port** / encapsulate in adapter API |
| God type blocks isolated tests | **CP023** | SRP split per `srp-cohesion.md` |
| Rules only reachable via full framework context | **CP015** | **extract-pure-core** + **thin-boundary** |

## When not to escalate (tester → code)

| Situation | Lane |
|-----------|------|
| Recommended test packages not installed | Tester: infrastructure step in plan-add |
| Correct integration slice for boundary under test | Tester: **ADEQUATE** at integration layer |
| CI-component repo: pytest + `test-*.yml` per `ci-component-test.md` | Tester: overlay rules, not application pyramid |
| Behavior change required to add a seam | Code: **`escalate_human`** / brief — not silent refactor |

## Cross-lane handoff

When tester assess or write mode cannot add an adequate unit/component test without production edits:

```text
BLOCKED (code lane): <paths> | reason: <one line> | remediation: <recipe-id>
```

Remediation **recipe-id** values: `extract-pure-core`, `introduce-port`, `inject-time`, `thin-boundary`. Code lane resolves via **`, inline fix under rr-review`**, **``**, or **``** as appropriate.
