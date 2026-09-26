# Value Heuristics Reference

Detailed **diagnostic rubrics** for evaluating test value. Sources (curated, not full catalogs): Google SMURF (suite tradeoffs); TestLint / Reichhart et al. (2007); Meszaros *xUnit Test Patterns*; testsmells.org (Peruma et al.); TU Delft severity-threshold research; mutation testing (PIT / Stryker). **ISO/IEC 25002** is a meta-model for quality definitions---not embedded here; use this file's observable criteria instead.

**Inter-rater convergence target:** Two independent assessors evaluating the same codebase should produce verdict distributions within **5%** of each other. Every decision point in this file has an **observable criterion** and **boundary examples** to eliminate subjective judgment.

---

## Assertion strength taxonomy

Classify the **strongest oracle** in each test (the assertion that would fail first if behavior broke). Verification power matters more than assertion count (see mutation testing below).

| Level | Name | Observable criterion | Example |
|-------|------|------------------------|---------|
| **0** | **No oracle** | No assertion, or tautological / redundant (`assertTrue(true)`, expected == actual by mistake) | Empty test body; Unknown Test |
| **1** | **Existence** | Non-null, non-empty, type-only, or "defined" checks without value | `assertNotNull(result)` as *only* check |
| **2** | **Shape** | Structure check: count, key presence, status code, type, or schema --- where the asserted value is a **structural property** of the output, not a **domain-specific computed result** | `assertEquals(3, list.size())` when 3 is just "how many came back"; `expect(keys).toContain("id")` |
| **3** | **Value** | Specific output for given input: the expected value is a **domain-specific computed result** that would change if business logic changed | `assertEquals(90.00, total)` where 90.00 = 100 x 0.9 discount |
| **4** | **Behavioral contract** | Invariant, boundary, state transition, or expected failure path --- test **proves a rule holds** or **breaks at a defined edge** | `assertThrows(CreditLimitExceeded, ...)` at amount == limit+1 |

### Level classification decision rules

Apply these rules **in order** (first match wins) to resolve boundary cases:

| # | Rule | Decision | Rationale |
|---|------|----------|-----------|
| 1 | Assertion checks a **boundary condition** (at-limit, at-limit+1), **state transition** (A->B), **invariant that must always hold**, or **expected exception at a defined edge** | **Level 4** | Proves a contract, not just one output |
| 2 | Expected value is **hardcoded in the test AND derivable from the test's input through business logic** (e.g. input=100, discount=10%, expected=90.00) | **Level 3** | Verifies a computation, not a shape |
| 3 | Assertion uses `assertThrows` / `expect(...).toThrow(...)` for a **non-boundary** error (e.g. null input, missing entity) | **Level 3** | Expected failure for given input, but not a boundary contract |
| 4 | HTTP status code with **exact value** (200, 201, 404) where the **test name states the scenario** that determines the status (e.g. "when order not found") | **Level 3** | Status is a domain-specific outcome of the scenario |
| 5 | `assertEquals(N, collection.size())` where N is **derivable from the test's input setup** (e.g. inserted 3 active + 1 inactive, expect 3 active back) | **Level 3** | N is a value computed from input |
| 6 | Expected value is a **structural property** of the output (size, key count, HTTP status class, type name) AND could remain the same even if domain logic changed | **Level 2** | Verifies shape, not domain behavior |
| 7 | HTTP status code where the test is a **smoke / wiring check** (test name like "endpoint responds", "health check OK") | **Level 2** | Structural verification only |
| 8 | `assertEquals(N, collection.size())` where N is **not traceable to input setup** or test name does not state what N means | **Level 2** | Shape check without domain traceability |
| 9 | Guard assertions (non-null, non-empty, instanceof) **before** a Level 3+ assertion in the same test | **Not counted as the test's level** | Guard assertions are setup validation, not the oracle |
| 10 | Guard assertions as **the only** assertions in the test | **Level 1** | No value verification |

### Boundary examples (calibration)

```
# Level 2: count is structural, no domain computation
test "returns users":
    insert(userA, userB, userC)
    result = repo.findAll()
    assertEquals(3, result.size())        # L2: count only, no value on WHO or filtering

# Level 3: count IS derivable from input through business logic (filtering)
test "returns only active users":
    insert(userA_active, userB_active, userC_inactive)
    result = repo.findActive()
    assertEquals(2, result.size())        # L3 (rule 5): 2 derives from 2 active in setup

# Level 3: asserts domain-computed content
test "returns active users with correct data":
    insert(userA_active, userB_active, userC_inactive)
    result = repo.findActive()
    assertThat(result).extracting("id")
        .containsExactly(userA.id, userB.id)  # L3: specific output from input

# Level 3: status code IS the domain outcome (rule 4)
test "should return 404 when order not found":
    response = get("/orders/nonexistent-id")
    assertEquals(404, response.status)    # L3: 404 is the business answer

# Level 2: status code is structural wiring check (rule 7)
test "health endpoint responds":
    response = get("/actuator/health")
    assertEquals(200, response.status)    # L2: smoke check

# Level 4: boundary contract (rule 1)
test "rejects order at credit limit boundary":
    customer.creditLimit = 1000
    order = Order(customer, amount: 1000)   # exactly AT limit
    assertDoesNotThrow(() -> service.place(order))   # L4: boundary holds
    order2 = Order(customer, amount: 1001)  # one over
    assertThrows(CreditLimitExceeded, () -> service.place(order2))  # L4: breaks

# Level 3 (NOT Level 4): exception but NOT at a boundary (rule 3)
test "rejects null customer":
    assertThrows(IllegalArgumentException, () -> service.place(null))  # L3

# Guard assertion: does NOT determine test level (rule 9)
test "calculates discount for premium customer":
    result = service.calculateDiscount(premiumCustomer, 100)
    assertNotNull(result)           # guard, ignored for level
    assertEquals(90.00, result)     # L3: this IS the test's oracle
```

**Rules for assess:**

- Every test should have **at least one Level 3+** assertion on its **primary objective**, unless the test is explicitly a **structural integration test** (wiring, health, schema validation). Classify a test as "structural" only when its **name** and **body** both indicate no domain behavior is being verified. Level 2 as **sole** oracle is acceptable only for structural tests.
- **Level 0--1 as the only oracle** -> treat as **Critical** smell (see **Severity-classified test smells**): typically **NON-COMPLIANT** or **OVER-TESTED** depending on verdict matrix.
- Cross-check weak suites: **low mutation score** with high line coverage -> assertions too weak (Level 0--1 dominance or unkillable mutants).

---

## Purpose clarity checklist

A test has **clear purpose** (required for **ADEQUATE**) when **all four** conditions are met. If **any** fails, purpose is **unclear** -> **UNCLEAR** verdict (unless Critical/Major smell already applies).

| # | Condition | How to check | Fail example |
|---|-----------|-------------|--------------|
| 1 | **Test name states one behavior** | Name contains a subject + condition + expected outcome (e.g. "rejects order when credit limit exceeded") | `testProcess`, `test1`, `shouldWork` |
| 2 | **Body tests what name claims** | The production method called and assertions match the name's stated behavior | Name says "validates email" but body only asserts non-null on unrelated field |
| 3 | **One primary behavior per test** | Removing any single assertion group would leave the test still meaningful for a different behavior = violation (test is doing two things) | Test verifies both creation AND deletion in one method |
| 4 | **Assertions target the stated behavior** | All non-guard assertions relate to the behavior named in the test | Test "calculates total" also asserts audit log was written |

**Boundary examples (calibration):**

```
# CLEAR purpose (all 4 pass)
test "should apply 10% discount for premium customers":
    order = Order(customer: premium, amount: 100)
    total = pricing.calculateTotal(order)
    assertEquals(90.00, total)
    # Name: subject=discount, condition=premium, outcome=applied
    # Body: calls calculateTotal, asserts the discount result
    # One behavior: discount calculation
    # Assertion targets: total is the stated behavior

# UNCLEAR purpose (condition 1 fails: name is vague)
test "testOrderService":
    order = service.createOrder(data)
    assertNotNull(order)
    assertEquals("PENDING", order.status)
    # Name does not state what behavior is being tested

# UNCLEAR purpose (condition 2 fails: name/body mismatch)
test "should validate email format":
    user = service.createUser(validData)
    assertNotNull(user.id)
    assertEquals("ACTIVE", user.status)
    # Name says email validation, body tests user creation

# UNCLEAR purpose (condition 3 fails: two unrelated behaviors)
test "should create and archive order":
    created = service.create(data)
    assertEquals("NEW", created.status)
    archived = service.archive(created.id)
    assertEquals("ARCHIVED", archived.status)
    # Two independent behaviors: creation + archival
```

---

## Goal fit and brief-driven coverage

When **`BRIEF_PATH`** is set, **`Read`** it once before the walk.

### Goal / acceptance coverage

Map each explicit acceptance or regression signal from the brief to test evidence. Missing coverage → **MISSING**, heuristic **`Goal / acceptance coverage`**, with brief item cited in **reason**.

### Bug regression

When MR-as-ticket or Jira describes a defect:

- Test must recreate the reported failure condition
- Test must fail when the production fix is removed/reverted
- Test must assert corrected behavior — not merely “no exception” or HTTP 2xx

No such test → **MISSING**. Weak existing test → **NON-COMPLIANT** or **UNCLEAR** per matrix precedence.

### Activation coverage

Reusable/library/component surfaces need evidence that a consumer/job/export path exercises or wires the surface. Unit tests alone on an unwired package → **MISSING**, heuristic **`Activation coverage`**.

### Boundary-limit coverage

When brief or code **AR001** identifies a boundary, require enforcement appropriate to the stack (contract/consumer test, forbidden-import rule, API-surface test, CI wiring test). Missing → **MISSING**, heuristic **`Boundary-limit coverage`**.

When code reports **AR002**, do **not** fabricate a boundary test.

---

## Verdict decision matrix

Use this **after** mapping production units to tests. **Precedence:** `MISSING` if no adequate test for a unit that heuristics require; else classify existing tests by smell severity, then **UNCLEAR** / assertion-overload paths.

```
                    Tests exist for this unit?
                    /                          \
                  NO                            YES
                  |                              |
              MISSING                    Any Critical smell?
             (if coverage               /                    \
              required)              YES                     NO
                  |                    |                       |
                  |            OVER-TESTED              Any Major smell?
                  |            OR NON-COMPLIANT          /              \
                  |            (see rules below)      YES              NO
                  |                    |                |                |
                  |                    |          NON-COMPLIANT    Purpose unclear
                  |                    |                |           OR Assertion overload
                  |                    |                |           (Minor; see below)?
                  |                    |                |                /        \
                  |                    |                |          YES          NO
                  |                    |                |           |            |
                  |                    |                |      UNCLEAR or   ADEQUATE
                  |                    |                |      NON-COMPLIANT
                  |                    |
                  +--------------------+-- Critical: OVER-TESTED vs NON-COMPLIANT
                                           rules below (deterministic, not preference)
```

### OVER-TESTED vs NON-COMPLIANT (Critical smell)

When a Critical smell is detected, use this **deterministic rule** (not "prefer"):

| Condition | Verdict | Rationale |
|-----------|---------|-----------|
| Test has **zero** assertions on production output (only `verify()` / interaction checks, or empty body, or tautological) | **OVER-TESTED** | Net negative: maintenance cost with no bug-detection value |
| Test has **at least one** assertion on production output, but the assertion is broken by a Critical smell (wrong layer, conditional logic, framework behavior) | **NON-COMPLIANT** | Some behavior is tested but the test is structurally invalid |
| Test's **only** assertions are Level 0--1 AND the test exercises real production code | **NON-COMPLIANT** | Real code runs but assertions don't catch regressions |
| Test's **only** assertions are Level 0--1 AND the test exercises only mocks/framework | **OVER-TESTED** | Neither the code nor the assertions provide value |

**Decision rules:**

| Verdict | When |
|--------|------|
| **MISSING** | No test targets this method/branch **and** heuristics say it should be covered (not trivial getter, not generated-only, not config-only per **Coverage gap identification**). |
| **OVER-TESTED** | Tests exist but **net negative value**: zero assertions on production output, only `verify()` / interaction checks, empty body, or tautological --- per the OVER-TESTED vs NON-COMPLIANT table above. |
| **NON-COMPLIANT** | Tests exist **and** any of: (a) **Critical** smell with at least one production-output assertion (per table above); (b) **any Major** smell; (c) **Assertion overload** (Minor) while test **purpose is clear** per **Purpose clarity checklist** --- overload is still quality debt. If **Assertion roulette** (Major) also applies, classify via Major -> **NON-COMPLIANT**. |
| **UNCLEAR** | Tests exist; **no Critical or Major** smell; **and** purpose is **not clear** per **Purpose clarity checklist**, **or** **Assertion overload** (Minor) **with** unclear purpose. |
| **ADEQUATE** | Tests exist; purpose is **clear** per **Purpose clarity checklist**; **no Critical/Major**; **not** UNCLEAR; **not** NON-COMPLIANT from assertion overload. Other **Minor** smells (Mystery guest, Magic numbers, etc.) **alone** -> **ADEQUATE** with optional note. |

**UNCLEAR vs ADEQUATE:** Apply **Purpose clarity checklist** (4 conditions). All pass = clear = ADEQUATE candidate. Any fail = unclear = **UNCLEAR** (unless Critical/Major smell already applies --- then use that verdict).

---

## Severity-classified test smells

**15 curated smells** (from literature/tools; full catalogs not copied). **Critical** and **Major** drive **NON-COMPLIANT** / **OVER-TESTED**. **Assertion overload** (Minor) can yield **UNCLEAR** or **NON-COMPLIANT**. Other **Minor** smells are note-only unless paired with Critical/Major.

### Critical (NON-COMPLIANT or OVER-TESTED)

| Smell | Observable criterion | Counting rule | Source |
|-------|----------------------|---------------|--------|
| **No oracle / tautological assertion** | Level **0** oracle only; empty executable body; redundant assertion | Any single occurrence triggers | testsmells.org: Empty Test, Unknown Test; **Trivial assertions** below |
| **Full mock chain** | **All** external collaborators of the production method are mocked AND the test has **no** assertion on a return value or state change --- only `verify()` / interaction checks. "All" = every dependency the method calls is a mock/stub; if **at least one** collaborator is real and exercised, this smell does **not** apply (but **Implementation coupling** may) | Count collaborators from the production method's signature + body; if mock count == total external calls, this is "all" | Mock overuse |
| **Framework testing** | Test asserts behavior that belongs to the ORM, framework, or library --- not application rules. Indicator: the test would pass identically on a **different** application using the same framework | If removing all application code and replacing with a trivial entity still passes the test, it's framework testing | Framework testing |
| **Wrong layer** | **Unit test** (no Spring context, no test DB, no HTTP server) calls a real DB, HTTP endpoint, or filesystem. **Integration/E2E test** tests only pure logic that has no I/O. Note: in-memory DBs (H2) in a unit test = wrong layer; **TestContainers** or `@PhoenixWeblessIntegrationTest` = integration test (correct layer if testing DB interaction) | Check test annotations/config: no `@...IntegrationTest`, no `@DataJpaTest`, no test container setup = unit test. If it hits real I/O, wrong layer | Layer-appropriate testing |
| **Conditional test logic** | `if` / `switch` / ternary / loop in test body selects which assertions run; the test report shows one pass but multiple paths exist | Any `if`/`switch`/ternary in test body (not in test data setup or builder) triggers | TestLint, testsmells.org |

**Examples (Critical):**

```
# Full mock chain --- OVER-TESTED
# All 3 collaborators mocked; only verify(); zero assertions on output
test "should process":
    mock(repo.find).returns(entity)
    mock(mapper.toDto).returns(dto)
    mock(validator.validate).returns(true)
    service.process(id)
    verify(repo.find was called)

# NOT full mock chain --- 2/3 mocked but asserts return value
test "should process":
    mock(repo.find).returns(entity)
    mock(validator.validate).returns(true)
    result = service.process(id)    # mapper is real
    assertEquals(expectedDto, result)  # assertion on output -> not full mock chain
    # May still be Implementation coupling (Major) if verify() is also present

# Framework testing
test "should save entity":
    entity = new Entity()
    repository.save(entity)
    assert repository.findById(entity.id) is present

# Wrong layer: unit test with real DB
# No @IntegrationTest, no TestContainers, but hits JDBC
test "should find user":
    connection = DriverManager.getConnection(...)
    result = dao.findUser(connection, id)
    assertNotNull(result)

# Conditional test logic --- masks coverage
test "should work":
    if (featureFlag) { assert x } else { assert y }
```

### Major (typically NON-COMPLIANT)

| Smell | Observable criterion | Counting rule | Source |
|-------|----------------------|---------------|--------|
| **Implementation coupling** | Asserts call order, private API, internal state, or uses `verify()` on a collaborator **when the test also has assertions on public output**. A single `verify()` as the **sole** assertion = Full mock chain (Critical), not this smell | Triggered when `verify()` / `inOrder()` / spy assertions coexist with output assertions, OR when test accesses private fields / `wrapper.vm` internals | Implementation coupling |
| **Eager test** | One test invokes **3+ distinct production methods** (methods on the system-under-test or its direct API). Accessor calls on the **result** (e.g. `result.getName()`) do **not** count; only calls that trigger distinct production behavior count | Count distinct method calls on SUT or production classes that perform logic/mutation. Accessors on returned DTOs/entities are excluded | Meszaros, TestLint |
| **Assertion roulette** | **5+** assertion statements without assertion-level messages or clearly separating context (e.g. `assertEquals(a, x)` x5 with no message arg). Assertions **inside a loop** count as `iterations x assertions_per_iteration` | Count literal assertion call sites; loop body assertions multiply by iteration count. `assertAll()` groups count each lambda as one assertion | testsmells.org, VU Brussels |
| **Collateral assertions** | Asserts properties that are **not named** in the test name or its **stated objective** per **Purpose clarity checklist** condition 4 | Compare each assertion's target property to the behavior stated in the test name. Unrelated properties trigger this smell | Assertion discipline |
| **Sensitive equality** | Exact match on volatile values: `toString()`, timestamps, UUIDs, float without epsilon --- **when these are not business-critical fields**. If the exact value IS the business requirement (e.g. formatted invoice number), this smell does **not** apply | Check each `assertEquals`/`isEqualTo` target: is it a generated/volatile value, or a business-defined one? | testsmells.org Sensitive Equality; **Time and timestamp handling** |

### `verify()` classification decision tree

Because `verify()` appears in multiple smells, use this tree to classify consistently:

| Pattern | Classification |
|---------|---------------|
| `verify()` is the **only** assertion-like statement in the test (no `assertEquals`, `assertThat`, etc.) | **Full mock chain** (Critical) --- OVER-TESTED |
| `verify()` coexists with assertions on production output (`assertEquals`, `assertThat` on return value or state) | **Implementation coupling** (Major) --- NON-COMPLIANT |
| `verify()` on a **side-effect call** (e.g. `verify(emailService).send(...)`) as the **only** assertion, AND the production method's **primary purpose** is that side effect (e.g. `sendNotification()`) | **Not a smell** --- the side-effect IS the behavior under test; classify assertions on the `verify()` arguments at Level 3+ if they check specific values |
| `verify()` on a side-effect call where the production method's primary purpose is **not** that side effect (e.g. `placeOrder()` verified for `repo.save()`) | **Implementation coupling** (Major) |

**Examples (Major):**

```
# Implementation coupling: verify + output assertion
test "should calculate total":
    result = service.calculateTotal(order)
    assertEquals(90.00, result)          # output assertion (good)
    verify(auditService).log(any())      # implementation coupling (bad)

# Eager test: 3+ distinct SUT methods
test "full lifecycle":
    service.create(data)        # SUT method 1
    service.update(id, patch)   # SUT method 2
    service.archive(id)         # SUT method 3
    assert ...

# NOT eager test: accessors on result don't count
test "should map user correctly":
    result = mapper.toDto(user)
    assertEquals("John", result.getName())    # accessor on result, not SUT method
    assertEquals("john@x.com", result.getEmail())  # accessor on result

# Assertion roulette: 5+ without messages
test "batch":
    assertEquals(a, x)
    assertEquals(b, y)
    assertEquals(c, z)
    assertEquals(d, w)
    assertEquals(e, v)  # 5th: triggers roulette

# Assertion roulette in loop: 2 assertions x 3 iterations = 6
test "all items valid":
    for item in [a, b, c]:
        assertNotNull(item.id)
        assertEquals("VALID", item.status)  # 6 total -> roulette

# Sensitive equality: volatile value
test "should create user":
    user = service.create(data)
    assertEquals("2024-01-15T10:00:00Z", user.createdAt)  # volatile timestamp

# NOT sensitive equality: business-defined format
test "should format invoice number":
    invoice = service.createInvoice(data)
    assertEquals("INV-2024-00001", invoice.number)  # business format = not volatile
```

### Minor

| Smell | Observable criterion | Verdict when this smell applies | Counting rule | Source |
|-------|----------------------|--------------------------------|---------------|--------|
| **Assertion overload** | **6+** assertion statements in one test method (hard threshold). Assertions inside loops count as `iterations x assertions_per_iteration`. `assertAll()` lambdas each count as one. Does NOT apply when all assertions verify **properties of a single returned object** from one method call (that is structural validation, not overload) | **UNCLEAR** if test purpose is **not clear** per **Purpose clarity checklist**. **NON-COMPLIANT** if purpose **is** clear but assertion count >= 6. If **Assertion roulette** (5+ without messages) also applies, use Major -> NON-COMPLIANT | Count literal assertion call sites; multiply loop body assertions by iteration count | Heuristic (maintenance / **Flaky Test Diagnosis**) |
| **Mystery guest** | External file/DB/etc. not set up in fixture; test depends on pre-existing external state | Note only (does not change verdict alone) | - | Meszaros, testsmells.org |
| **General fixture** | `beforeEach` / setup builds state unused by this test method | Note only | - | Meszaros, testsmells.org |
| **Magic numbers** | Numeric literals in assertions without named constant or derivation comment | Note only | - | testsmells.org |
| **Duplicate test** | Same scenario **80%+** assertion overlap with another test in the suite (same inputs, same assertions, minor variation) | Note only | Compare assertion targets and input setup between test pairs | Duplicate Assert (concept) |

**Assertion overload exception:** When a test asserts **multiple properties of a single returned object** from **one** method call (e.g. `assertEquals(name, dto.getName()); assertEquals(email, dto.getEmail()); ...`), count this as **one logical assertion group**, not N separate assertions, provided all properties belong to the **same behavior** stated in the test name. This exception prevents false-flagging DTO mapping tests or constructor validation tests.

---

## Per-finding diagnostic card

Replace informal "scores" with **observable fields** for each **non-ADEQUATE** row (optional for ADEQUATE). When emitting **`assess-output.md`** reports, map these fields into the **mode-specific table columns** (live-assess: target, verdict, tests, assertion-level, reason, heuristic; test-assess: target, verdict, smell, assertion-level, evidence, heuristic) — the card is the assessment **process**; the table is the **artifact**.

**TARGET (symbol, not line ranges):** Use **`<qualified.name>#<symbol>`** --- the **production unit** under verdict: method, constructor, type (class / struct / trait / enum / object), composable, or file top-level. **Do not** use `[Lx-Ly]` here; line numbers belong in **EVIDENCE** only if needed.

| Pattern | Example |
|--------|---------|
| Type + method | `com.acme.orders.OrderService#placeOrder` |
| Type + constructor | `com.acme.Order#Order` or `com.acme.Order#<init>` (match stack/ecosystem) |
| Type-only (file/type scope) | `com.acme.Order` or `com.acme.Order` when the row is the whole type |
| Trait / protocol / interface | `com.acme.Pricing` (type) or `com.acme.Pricing#method` for a default/required member |
| Enum | `com.acme.Status` (type) or `com.acme.Status#VALUE` for a constant under test |
| Module function | `orders.handlers#createOrder` / `crate::auth::verify` --- follow repo's qualified style |
| Vue SFC / component | `src/views/Checkout.vue#setup` or per **`vue-test.md`** |
| Branch-level row | Same **TARGET** as the method, add **`branch:`** field: `branch: amount > creditLimit` |

```
TARGET: <qualified.name>#<method|constructor|class|trait|enum|...>
branch: <condition>   (only when this row is a specific branch verdict)
VERDICT: MISSING | OVER-TESTED | NON-COMPLIANT | UNCLEAR | ADEQUATE
SMELL: <name> (severity: Critical | Major | Minor)
ASSERTION_LEVEL: <0-4> -- <No oracle | Existence | Shape | Value | Behavioral contract>
EVIDENCE: <one line: pattern, test id, or Lx-Ly if helpful>
HEURISTIC: <section title from this file, e.g. Severity-classified test smells / Assertion strength taxonomy>
```

**Finding line (compact):**  
`<qualified.name>#<symbol> VERDICT tests=[...] -- <section title>: <reason>`  
Optional: `branch: <condition>` after TARGET when not ADEQUATE on the whole method.  
When non-ADEQUATE, append smell severity and assertion level inline if known, e.g. `-- Severity-classified test smells (Critical: Full mock chain); ASSERTION_LEVEL=1`.

---

## Trivial assertions (Level 0--1)

```
test "should return non-null":
    result = service.process()
    assert result is not null  # Alone: Level 1 --- rarely catches real bugs
```

**Problem:** Passes when logic is wrong if output is still non-null. Pair with Level 3+ on the same objective or treat as **no oracle** for that behavior.

---

## Value pattern detection

### Business rule tests

```
test "should apply discount for premium customers":
    order = Order(customer: premiumCustomer, amount: 100)
    total = pricingService.calculateTotal(order)
    assert total == 90.00
```

**Value:** Level 3+; validates rule.

### Edge case tests

```
test "should reject order exceeding credit limit":
    customer.creditLimit = 1000
    order = Order(customer, amount: 1001)
    assert throws CreditLimitExceededException when orderService.place(order)
```

**Value:** Level 4; boundary behavior.

### Error handling tests

```
test "should return empty when external service unavailable":
    mock(externalApi.fetch).throws(ServiceUnavailableException)
    result = service.getData()
    assert result is empty
```

**Value:** Level 3+ on degradation path.

---

## Assertion discipline

Single-purpose tests; assert only what the name implies (**Major** if collateral assertions).

| Rule | Rationale |
|------|-----------|
| Test name = contract | Name lists what must hold |
| No collateral assertions | **Major** smell if unrelated properties asserted |
| Fail for the right reason | Unrelated assertions -> misleading failures |

See **Assertion roulette** and **Sensitive equality** under **Major**.

---

## Layer-appropriate testing

| Layer | Should test | Should NOT test | Infrastructure indicators |
|-------|-------------|-----------------|--------------------------|
| **Unit** | Business logic, validation, transformations | Database, HTTP, external services, filesystem | No Spring context, no test DB, no HTTP server, no TestContainers. **H2 in-memory = still DB = NOT unit** |
| **Integration** | API contracts, DB queries, wiring, service boundaries | UI polish, every error string | `@...IntegrationTest`, `@DataJpaTest`, TestContainers, `@WebMvcTest`, MSW with real component tree |
| **E2E** | Critical flows, cross-system | Every component | Playwright, Cypress, full server + client |

**Wrong layer** -> **Critical** (see examples in prior sections).

### Layer classification decision rules

| Pattern | Layer | Rationale |
|---------|-------|-----------|
| Test uses H2 / in-memory DB but has no `@IntegrationTest` annotation | **Wrong layer** (Critical) | In-memory DB is still a database; test should be classified and annotated as integration |
| Test uses TestContainers with `@IntegrationTest` | **Integration** (correct) | Real DB in correct test layer |
| Test uses `@WebMvcTest` / `MockMvc` | **Integration** (correct) | Partial Spring context for controller testing |
| Test mocks all I/O and tests only logic | **Unit** (correct if no Spring context) | Pure logic test |
| Test has `@SpringBootTest` but only tests a single service with mocked deps | **Consider wrong layer** | Full context for a unit-like test; flag as note, not Critical |

---

## Coverage gap identification

### High-priority gaps (MISSING when untested)

| Category | Structural detection criteria | Example |
|----------|------------------------------|---------|
| **Public methods on service/controller classes** | Class has `@Service`, `@RestController`, `@Component`, or equivalent framework annotation; or class name ends with `Service`, `Controller`, `Handler`, `Processor`, `UseCase`, `Interactor` | `OrderService#placeOrder` |
| **Error paths and validation failures** | Method has `throw`, `catch`, validation annotations (`@Valid`, `@NotNull` on parameters), or guard clauses that return early / throw | `UserService#createUser` when `@Valid` param has no test for invalid input |
| **Edge cases: nulls, empty collections, boundaries** | Method has null checks, empty-collection guards, comparison operators (`<`, `>`, `<=`, `>=`, `==`) on numeric values | `DiscountService#calculate` with `if (amount <= 0)` branch untested |
| **State transitions** | Method changes an entity's status/state field; or method name includes `transition`, `change`, `update`, `activate`, `deactivate`, `archive` | `OrderService#cancelOrder` changes status from ACTIVE to CANCELLED |

### Lower-priority gaps (ADEQUATE without test)

| Category | Structural detection criteria | Example |
|----------|------------------------------|---------|
| **Getters/setters without logic** | Method body is only `return this.field` or `this.field = param` with no conditional logic, no computation, no side effects | `User#getName()` returning `this.name` |
| **DTOs/entities without validation** | Class has only fields + accessors; no `@Valid`, no custom `validate()`, no computed properties, no business methods | `UserDto` with only getters/setters |
| **Config-only classes** | Class has only `@Bean` methods returning configured instances with no conditional logic; or class has only `@Value`/`@ConfigurationProperties` fields | `AppConfig#dataSource()` |
| **Generated code** | Files in generated output directories (`target/generated-sources`, `build/generated`); or classes with `@Generated` annotation; or MapStruct/Lombok-generated code | `UserMapperImpl` generated by MapStruct |

### Frontend component heuristics

For Vue/React (and similar):

- Interactive component **without** render/interaction test -> **MISSING** (high priority). "Interactive" = has event handlers, form inputs, or user-triggered state changes.
- Conditional rendering **without** both branches tested -> **MISSING** on untested branches. Applies to `v-if`/`v-else`, ternary in JSX, conditional CSS classes with behavioral impact.
- Composable/hook with reactive state **without** unit test -> **MISSING**.
- Route guard with redirect **without** test -> **MISSING**.
- Static-only component (no props, no events, no state, no conditional rendering) -> **ADEQUATE** without dedicated test.
- Asserting `wrapper.vm` / internal state vs. DOM or a11y -> **NON-COMPLIANT** (**Implementation coupling**).

---

## Mutation testing (optional reported metric)

Coverage measures **execution**, not **detection**. When supported, run mutation testing (**Stryker** JS/TS, **PIT** Java) and report **mutation score** / **test strength** (killed / covered mutants).

- **Role:** Reported in assess output---not a default hard gate unless the project elevates it.
- **Interpretation:** Low mutation score + high line coverage -> weak assertions; cross-check **Assertion strength taxonomy** and **Critical** smells.

---

## Refactoring for Testability

When production structure blocks an adequate **unit** or **component** test, do **not** close the gap with a mock-heavy workaround or a duplicate integration test if a behavior-preserving extraction is local. Remediation recipes and **CP** mapping: [`testability.md`](../../s-coder/refs/testability.md).

### Production blocks unit layer

| Field | Rule |
|-------|------|
| **Trigger** | Logic is unit-testable in principle (deterministic rules, no mandatory live I/O) but production forces full framework context, full mock chain (**Full mock chain** smell), or only `@SpringBootTest` / full stack can exercise the rule |
| **Live-assess verdict** | **MISSING** on the production target when no adequate unit/component test exists |
| **Write mode** | Emit **`BLOCKED (code lane):`** per `testability.md` — do not output **`TEST WRITTEN:`** |
| **Do not** | Claim closed via mocks when **extract-pure-core** or **introduce-port** is local and behavior-preserving |

**Example:** `OrderService#createOrder` validates items, computes total, saves, and publishes — only an IT exists; unit test would mock repository, validator, mapper, and event bus with **verify()** only → **MISSING** + cross-lane **`remediation: extract-pure-core`**.

### Duplicate layer coverage

| Field | Rule |
|-------|------|
| **Trigger** | Same production symbol covered by a mock-heavy **unit** test **and** an **integration** test with overlapping oracle on the same behavior |
| **Verdict** | **OVER-TESTED** on the weaker test (usually the mock-only unit) |
| **Fix (tester lane)** | Delete or narrow the weaker test after production seams exist; if production blocks a real unit test, escalate per **Production blocks unit layer** instead of keeping both |

**Cross-lane:** Emit one **`BLOCKED (code lane):`** line per blocked production path in assess summary (see **`assess-output.md`**). List under terminal **Remaining gaps** / **Blocked (code lane)** — do not claim pyramid or coverage targets met for those items.

---

## Flaky Test Diagnosis

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Timestamp failures | Sensitive equality | **Time and timestamp handling** below |

For standard flaky causes (shared state, CI environment, fixture order): isolate tests, use deterministic time, per-test setup/teardown.

---

## Flaky test quarantine escalation

When not fixable this iteration:

1. **Quarantine** --- `@Disabled` / `it.skip` / `@Ignore` with reason, or flaky tag.
2. **Backlog** --- Track what is needed to unquarantine.
3. **Document** --- In assess output: quarantined tests with reason and follow-up.

If a test engineer agent reports flaky-not-fixable, orchestrator does not treat the step as fully successful without **Remaining gaps** or follow-up.

---

## Time and timestamp handling

| Timing drives business logic? | Assert |
|-------------------------------|--------|
| Yes (SLA, expiry, audit window) | Exact or injected clock |
| No (audit "has a timestamp") | Presence or range; not exact wall clock |

Avoid exact-time assertions for non-critical fields (**Sensitive equality**). Prefer injected `Clock` at boundaries.

---

## Suite-level health (reporting)

Optional **aggregate** signals may appear as a **one-line NOTE** or **LAYERS** line in **`assess-output.md`** (e.g. mutation score, flaky ratio): assertion density, oracle strength (Level 3+ share), Major+ smell density. **Reported metrics**, not substitutes for per-target verdict rows.
