# Test Type Evaluation

## Core Principle
**Test at the lowest level that provides confidence.**

## Test Pyramid

```
        /\
       /E2E\      5-15 tests (critical flows only)
      /------\
     /Contract\   Per service boundary (API contracts)
    /----------\
   /   Integ   \  20-30% of suite (boundaries, API clients, routing)
  /------------\
 /  Component  \  Frontend: render + interaction in simulated DOM
/--------------\
|    Unit      | 70-80% of suite (business logic, validation, composables)
+--------------+
```

### Pyramid Violations

| Anti-pattern | Problem | Fix |
|--------------|---------|-----|
| **Ice cream cone** (mostly E2E) | Slow, flaky, expensive | Push coverage down to unit/integration |
| **Hourglass** (unit + E2E, no integration) | Missing contract validation | Add integration tests at boundaries |
| **Inverted pyramid** (mostly integration) | Slow feedback, hard to debug | Extract business logic to unit tests |

---

## Unit Tests

### Write When:
- Pure business logic, validation, transformations
- No external dependencies (DB, HTTP, filesystem)
- Deterministic and isolated

### Criteria:
- Business rules (pricing, discounts, permissions, domain logic)
- Validation logic, data transformations, algorithms
- State machines and workflow transitions
- Edge cases: nulls, empty collections, boundary values

### Not Unit Tests:
- Requires database, HTTP, or filesystem
- Requires framework context (Spring, React/Vue context)
- Tests framework behavior

---

## Component Tests (frontend)

Mount UI in simulated DOM (Vitest + `happy-dom`/`jsdom`), assert on output and user-visible interactions. No running backend. Sits above unit, below integration.

### Write When:
- SFC or view component — template render, conditional branches, props/emits
- User interactions — clicks, form input, emitted events
- No live backend required — mock HTTP with MSW or stub composables

### Not Component Tests:
- Pure composable/util with no DOM → **unit**
- Full stack with real API + navigation → **integration** or **E2E**

---

## Property-Based Testing (PBT)

PBT generates many inputs from stated properties (invariants). Complements unit and integration tests.

### When PBT Pays Off:

1. **Combinatorial or large input space** — validators, parsers, serializers, mappers
2. **Clear invariants** — "round-trip encode/decode equals identity", "output length ≤ input length"
3. **High defect density per example** — data transformations where edge combinations matter
4. **Deterministic core** — pure functions or logic isolated behind injectable clocks/IO

**Skip PBT when:** mostly UI/DOM, requires live services, nondeterministic without heavy setup, or properties are unclear.

### Tooling: **fast-check** (JS/TS), **jqwik** (Java), **Hypothesis** (Python), **PropEr** (Erlang).

### Anti-patterns:

| Anti-pattern | Problem |
|--------------|---------|
| PBT with vague properties | Passes without meaning; tighten invariants |
| PBT for code with hidden global state | Flaky — extract pure core first |
| Only PBT, zero examples | Harder onboarding; keep a few named examples |

---

## Integration Tests

### Write When:
- Tests contract between components (API endpoints, DB queries, service boundaries)
- Requires external dependency (database, message queue, cache, external API)
- Validates wiring (DI, configuration, middleware) or side effects

### Backend Criteria:
- API endpoints, database operations, service boundaries
- Authentication/authorization, external API integration

### Frontend Criteria:
- Component integration, state management (Pinia/Vuex, Redux/Zustand)
- API client, routing (navigation, guards), form submission flows

### Not Integration Tests:
- Pure business logic → unit
- UI rendering without external services → component
- Framework behavior → trust the framework

---

## Contract Tests

See [contract-test.md](contract-test.md) for detailed guidance, workflows, and criteria.

**When to use:** Multi-service architecture with external consumers, cross-team boundaries, or independent deployment schedules.

---

## Decision Tree

```
Does it use injected fakes/stubs (FakeHelm, mock repository, stub HTTP) with no live I/O?
├─ YES → UNIT TEST (fakes do not make it integration)
│
└─ NO → Does it have external dependencies (DB, HTTP, filesystem, real cluster)?
    ├─ NO → Can it be tested in isolation?
    │   ├─ YES → UNIT TEST
    │   └─ NO → Refactor production per [`testability.md`](../../../code/coder/refs/testability.md) (**extract-pure-core**), then UNIT TEST; if refactor is out of scope → **BLOCKED (code lane)** — do not mock around a god method
    │
    └─ YES → Is this a service boundary with external consumers?
        ├─ YES → Does it need independent deployment?
        │   ├─ YES → CONTRACT TEST (+ integration for full behavior)
        │   └─ NO → INTEGRATION TEST
        │
        └─ NO → Does it test internal boundary (DB, filesystem, k3d cluster)?
            ├─ YES → INTEGRATION TEST (or k3d layer in CI-component repos)
            └─ NO → Mock dependency → UNIT TEST
```

---

## Examples by System Type

| Code | Test Type | Rationale |
|------|-----------|-----------|
| `calculatePrice(order)` | Unit | Pure calculation, no dependencies |
| `validateEmail(string)` | Unit | Pure validation, deterministic |
| `useAuth` composable (refs/computed only) | Unit | Pure reactive logic, no DOM |
| `UserForm.vue` render + submit emit | Component | Renders in simulated DOM; asserts emit/DOM output |
| `findOrdersByStatus()` query | Integration | Tests query against real DB |
| `POST /api/orders` (internal) | Integration | API endpoint + DB |
| `POST /api/orders` (external) | Contract + Integration | Contract: schema; Integration: full behavior |
| Login form submission | Integration | Form + validation + API + navigation |
| Critical auth/checkout flow | E2E | Cross-system, revenue/compliance critical |

---

## Coverage Targets

| Test Type | Target | Rationale |
|-----------|--------|-----------|
| **Unit** | 70-80% of suite | Fast, stable, catches most bugs |
| **Integration** | 20-30% of suite | Validates boundaries, slower but necessary |
| **Contract** | Per service boundary | One per external API endpoint/consumer |
| **E2E** | 5-15 tests total | Critical flows only, expensive |

### By Code Category

| Code Category | Unit | Integration | Contract | Total |
|---------------|------|-------------|----------|-------|
| Business logic | 100% | N/A | N/A | 100% |
| Validation / utilities | 100% | N/A | N/A | 100% |
| API endpoints (internal) | N/A | 80%+ | N/A | 80%+ |
| API endpoints (external) | N/A | 80%+ | 100% | 100% |
| Database queries | N/A | 80%+ | N/A | 80%+ |
| Service boundaries | N/A | 50%+ | 100% | 100% |
| UI components | 50-80% | 20-30% | N/A | 70-80% |

---

## Anti-Patterns

| Anti-pattern | Fix |
|--------------|-----|
| Unit test hitting database | Mock repository, test logic only |
| Integration test for pure logic | Extract to unit test |
| Testing framework behavior | Trust framework, test your code |
| Mock-heavy unit tests | Use real objects or extract pure logic |
| Duplicate coverage at multiple layers | Keep highest-value test, delete others |
| Contract test for internal APIs | Use integration tests |
| No contract tests for public APIs | Add contract tests for all external APIs |

---

## Prioritization

```
        Unit | Contract | Integration
High  |  ▲▲▲ |   ▲▲▲   |     ▲▲
Med   |  ▲▲  |    ▲    |     ▲
Low   |  ▲   |         |
```

1. High-value unit tests (business logic, validation)
2. High-value contract tests (external APIs with multiple consumers)
3. High-value integration tests (critical queries, auth flows)
4. Medium-value unit + contract + integration tests
5. Low-value unit tests (getters/setters with logic)

---

## E2E Tests

E2E tests catch failures that only manifest when the full stack runs together. **Not** a safety net for missing lower-level tests.

### Write E2E When ALL Conditions Are True:
1. Failure mode only exists when frontend + backend + infra run together
2. Flow is a critical business path (revenue, data integrity, compliance)
3. No combination of integration tests can cover the contract boundary
4. Cost of production incident exceeds maintenance burden

### Hard Criteria for Inclusion:
- **Authentication flows** — token issuance, refresh, logout across boundaries
- **Multi-system transactions** — 3+ services where partial failure causes inconsistency
- **External integration boundaries** — payment, third-party APIs with realistic contract drift
- **Compliance-critical paths** — audit trails, GDPR, customs clearance
- **The "golden path"** — the #1 thing the system must always do

### Hard Criteria for Exclusion:
- CRUD operations (integration tests)
- UI validation (frontend unit tests)
- Error states mockable at integration level
- Flows that duplicate existing contract tests

### Target: 5-15 E2E scenarios maximum. Runnable in < 10 minutes. Flaky test = P1 bug.

---

## Quick Reference

- [ ] Pure logic? → Unit test
- [ ] Touches DB/HTTP/filesystem? → Integration test
- [ ] Service boundary with external consumers? → Contract test + Integration test
- [ ] Tests framework behavior? → Skip
- [ ] Already covered at lower level? → Skip or refactor
- [ ] Multiple teams depend on this API? → Contract test is mandatory
- [ ] Would this catch a real production bug? → Keep
- [ ] Test breaks on refactor without behavior change? → Coupled to implementation
