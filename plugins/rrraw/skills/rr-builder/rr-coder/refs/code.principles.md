# Coding Principles

Cross-language principles for clean, extractable code. Language-specific patterns live in dedicated references (java.md, typescript.md, etc.).

## Prefer / Avoid

| Prefer | Avoid | Why |
|--------|-------|-----|
| Composition + interfaces | Class inheritance hierarchies | Inherited coupling crosses domain boundaries, blocks extraction |
| Early returns, guard clauses | Nested if/else > 2 levels | Deep nesting hides business logic |
| Named constants, enums | Magic numbers/strings | Scattered literals break when business rules change |
| Functions < 20 lines, single abstraction level | Mixed abstraction in one function | Harder to extract into separate services later |
| DRY at 3+ identical duplications | Premature extraction at 2 uses | Over-DRY couples features that should be independent |
| Immutable data, return new objects | Mutating function arguments | Mutation bugs are invisible in distributed systems |
| Fail fast with context-rich errors | Swallowing exceptions silently | Silent failures in one product mask issues across the platform |
| Result/Either types for expected failures | Exceptions for control flow | Exceptions cross domain boundaries unpredictably |
| Descriptive names | Comments explaining "what" | Names outlive comments; comments rot |
| KISS: simplest solution that works | YAGNI violations: building for hypothetical futures | Speculative abstractions add coupling without proven value |
| Bind repeated call/expression once per scope | Calling the same helper or non-trivial expression multiple times in one block when a local captures the result | Duplicate work, args can drift between calls, harder to read |
| Cite circuit, cache, rate-limit, load-shed, and encryption decisions (ADR, org standard, gateway config, or explicit none) on new egress, ingress, or sensitive hops | New out-of-process call, network handler, or secrets/PII path without a cited decision | Review cannot infer defaults — map to **AR004** in [`architecture.md`](architecture.md) |

### Early Returns

Prefer early returns over nested if/else. Use multi-line blocks with braces — avoid `if (condition) return x;` on one line; hard to scan.

```text
// Prefer
if (condition) {
  return value;
}
return default;

// Avoid
if (condition) return value;
return default;
```

### Bind repeated expressions once

When the **same** function call or non-trivial expression appears in multiple branches or conditions **within one scope**, evaluate it **once** and bind to a clearly named local. Do not repeat the call “for clarity” in each branch.

```text
// Prefer
count = count_items(output) if output is not None else 0
if output is not None and count > 0:
  ...
elif count == 0:
  ...

// Avoid
if output is not None and count_items(output) > 0:
  ...
elif count_items(output) == 0:
  ...
```

Map violations to **CP032** in [`compliance-rubric.md`](compliance-rubric.md). Overlaps **CP005** when the duplicate is copy-pasted logic rather than a repeated call.

## Implementation boundaries (adapter-intrinsic knowledge)

**Problem:** Values that belong inside a driver, adapter, or factory (e.g. persistence backend id, storage driver name, vendor-specific flavor) appear **outside** that boundary—as string literals in comparisons (`===`, `switch`) or as **parameters**—so callers depend on **how** the implementation works, not **what** it does.

### Prefer / Avoid

| Prefer | Avoid | Why |
|--------|-------|-----|
| Encapsulated API on the adapter (`isX()`, `supportsY()`, typed capability or strategy) | `if (impl === "…")` / `switch (dialect)` at repository, service, or UI call sites | Implementation identifiers stay in the module that owns the implementation |
| A single strategy or polymorphic backend per variant | The same if/else or SQL shape copy-pasted across files | Duplication and typos; changes don’t stay behind one boundary |
| Named constants or enums for **domain**-meaningful values (status, region, contract id) | Unnamed literals for rules the whole stack must agree on | Same as magic strings—see **CP003** in [`compliance-rubric.md`](compliance-rubric.md) |

### Classification notes

- **Implementation-intrinsic vs domain:** If the value only exists to pick **one** of several implementations (DB, queue, SDK), it is intrinsic—keep it in the factory/driver module. If it is part of the **business vocabulary** (order state, product code), treat it as domain and name it; unnamed or repeated domain literals map to **CP003**.
- **Const vs repeat:** A single local `const` with a clear name and **one** compare in a narrow function is often acceptable. The **same** literal **2+** times in a file or **3+** times across modules for branching or parameters should be consolidated; if the value is adapter-intrinsic, fix the **boundary** (adapter API), not only duplicate `const` per file—see **CP025** and **CP026** in [`compliance-rubric.md`](compliance-rubric.md).
- **Adapter boundary:** Literals used **only** where the implementation is defined (registration, factory, assigning `dialect`) are normal. Call sites that **branch** on those strings elsewhere are leaks unless the string is a **stable external** contract (documented API or wire format).

## Configurable surface design

When adding or changing **public fields** on a shared contract (REST params, DTOs, env schemas, Helm values, CI inputs):

| Prefer | Avoid | Why |
|--------|-------|-----|
| One delegated path for behavior (caller owns invocation shape) | Parallel config fields + branching that re-expose the same concern | Duplicated knobs drift; consumers own CLI/script/API shape |
| Consistent tunability across related dimensions | Some knobs exposed as parameters, siblings hardcoded without documented invariant | Callers cannot reason about defaults; hidden policy |
| Cross-read all sibling fields before adding a new public field | New field added in isolation | Shared fields need descriptions/contracts covering every consumer |
| Names and scope match actual behavior | Generic name + rules that encode one recipe | Misleading contracts block reuse and safe defaults |

Map violations to **CP010** (duplicate delegation path), **CP027** (surface cohesion), **CP025** (implementation-intrinsic leak). GitLab CI component illustrations: [`components.md`](../../../gitlab/gitlab-devops/refs/components.md).

## Observability

Cross-language log / metric / correlation Prefer/Avoid. Full disposition table and when-not-to-flag: [`observability.md`](observability.md). Stack details stay in language refs (Java/Spring/Python/TS/… §Logging or §Observability).

### Prefer / Avoid

| Prefer | Avoid | Why |
|--------|-------|-----|
| Project/stack established logger + established redact path when peers already use them | Second facade / `print`-only; hand-rolled mask when a redactor exists | One pipeline for levels, MDC/trace, redaction |
| Parameterized / structured logs; redact or omit secrets/PII (fail closed) | String concat; secrets/tokens/PAN/PII in args; log raw hoping scrubbers | Searchable logs; aggregators retain raw forever |
| Emit only actionable logs/metrics (worth-emitting + level matrix); correct levels/context on existing calls | Happy-path / duplicate / wrong-level noise; vanity or duplicate meters | Operators act on signal; fewer clear series |
| Low-cardinality metric labels; correlation ids when stack already provides MDC/OTEL/tracing; meters on critical edges when peers already instrument | Unbounded ids as metric labels; inventing propagation or silent add/remove of `@Observed`/spans/meters in refactor | Triage and series cost; flag gaps; do not invent culture or break dashboards |

Map violations to **CP028** (log hygiene / safety / tooling / noise), **CP029** (missing or vanity metrics on critical boundaries), **CP030** (correlation / cardinality). **CP007** stays swallow-vs-rethrow. Refactor: hygiene on **existing** statements may `fix` (including apply existing redactor / drop local noise); missing meters/spans/new log sites or series removal → `clarify` / `escalate_human`.

## Code Organization

### Feature-Based Structure

Organize by business behavior, not technical layers:

```
src/
  users/           # All user-related code together
    UserController
    UserService
    UserRepository
  orders/          # All order-related code together
  shared/          # Cross-cutting concerns only
```

**NOT** by technical layer:

```
src/
  controllers/     # Don't do this
  services/        # Loses domain cohesion
  repositories/
```

### Naming Conventions

Use language defaults. See language-specific references for conventions per stack.

### Visibility / encapsulation

Prefer the **narrowest** language-legal visibility that still satisfies **proven** call sites. Self-contained modules hide helpers and types that never cross the module boundary.

| Prefer | Avoid | Why |
|--------|-------|-----|
| Least necessary visibility for types, methods, fields, nested types, and module exports | Default `public` / `export` / capitalized Go names “for convenience” | Wider surface couples modules and blocks extraction |
| Module-local helpers stay non-exported / package-private / `internal` / unexported / `pub(crate)` | Public API used only inside one package or module | Callers outside the owning module should not depend on internals |

**Stack mapping (modifiers):** Java — `private` → package-private → `protected` → `public`. Kotlin — `private` → `internal` → `public`. TypeScript — no `export` / `#`/`private` before `export`. Go — unexported (`lower`) before exported (`Upper`). Rust — private → `pub(crate)` → `pub`. Python — `_name` / module-private before public re-export.

Map violations to **CP031** in [`compliance-rubric.md`](compliance-rubric.md). Refactor: narrow only with call-site evidence; published SPI / reflection / framework entry → `escalate_human`.

### When to Extract to Shared

Extract when:
- Used by 3+ features
- Zero domain-specific logic
- Stable interface (changes rarely)

Keep in feature when:
- Used by 1-2 features (duplicate if needed)
- Contains domain knowledge
- Evolving rapidly

## Common Mistakes

**BUG**: Extracting shared code too early — now two features are coupled

```
shared/
  OrderValidator    ← Used by orders/ and shipping/
```

**FIX**: Duplicate until 3+ features need it — each feature stays independently extractable

```
orders/
  OrderValidator    ← Owns its validation
shipping/
  ShipmentValidator ← Owns its validation
```

---

**BUG**: Service layer mixing domain logic + orchestration + persistence in one method

```
createOrder(request):
  if request.items is empty → throw validation error
  total = sum(request.items)
  order = save(new Order(request, total))
  publish(OrderCreated(order))
  return order
```

**FIX**: Domain model owns rules, service orchestrates

```
createOrder(command):
  order = Order.create(command)   ← Validation + rules inside domain object
  save(order)
  publish(order.domainEvents())
  return order
```

---

**BUG**: Pricing rules and SQL in the same service method — only integration tests can reach logic

```
calculateQuote(request):
  discount = if request.tier == "GOLD" then 0.15 else 0.0
  rows = jdbc.query("SELECT price FROM items WHERE id = ?", request.itemId)
  return rows[0].price * (1 - discount)
```

**FIX**: Domain owns rules; persistence is a port — unit-test `PricingPolicy`, integration-test repository

```
calculateQuote(request):
  price = itemRepository.findPrice(request.itemId)
  return PricingPolicy.apply(request.tier, price)
```

Full signals, recipes, and **CP** mapping: [`testability.md`](testability.md). Map violations via that table — do not invent a separate rubric ID.

## Testability

Design production code with **test seams** so the tester lane can place unit tests on rules and integration tests on boundaries. Observable signals, Prefer/Avoid, refactor recipes (`extract-pure-core`, `introduce-port`, `inject-time`, `thin-boundary`), and **CP015** / **CP004** / **CP025** / **CP023** mapping: [`testability.md`](testability.md).

## Comments

**Comment "why", not "what"**:

```
// Good - explains reasoning
// Exponential backoff to avoid overwhelming API during outages
delay = BASE_DELAY * pow(2, attempt)

// Bad - states the obvious
// Multiply BASE_DELAY by 2 to the power of attempt
delay = BASE_DELAY * pow(2, attempt)
```

### When to Comment
- Complex algorithms (explain approach)
- Business rules (explain why rule exists)
- Non-obvious optimizations (explain tradeoff)
- Workarounds (explain why needed, link to issue)
- Public APIs (document parameters, return values, errors)

### When NOT to Comment
- Obvious code (let code speak for itself)
- Redundant information (type signatures, variable names already clear)
- Outdated comments (remove or update)

## Validate at Boundaries

**Pattern**: Validate external resources once at trust boundaries. Access normally thereafter.

Use the stack’s boundary validation mechanism once; use type-level nullness annotations for contracts; do not re-guard internally (Java: see `java.md` / `java.spring.md` when loaded).

- **Trust boundaries**: API responses, database results, file reads, message payloads, environment config
- **Internal access**: Direct access reveals bugs (null = logic error, not missing data)
- **Anti-pattern**: Defensive checks everywhere train acceptance of undefined where it shouldn't exist

**Why this matters**:
- Defensive checks everywhere hide which service introduced bad data
- In distributed systems, silent undefined propagation crosses service boundaries
- Product extraction requires clear failure points (this service failed, not upstream)

Example (concept applies to any language):
```
// Boundary: validate once
data = fetchFromExternal() ?? defaultValue

// Internal: access normally
result = data.property  // If null here, that's a bug to fix
```

**When to validate**:
- External data at trust boundaries (API responses, database results, file reads, message payloads, user input)
- Genuinely optional properties per data model

**When NOT to validate**:
- Data created/validated in current service — direct access reveals bugs faster
- Everywhere "just in case" — trains acceptance of undefined where it shouldn't be

## Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Deep nesting (> 2 levels) | Extract to functions, use early returns |
| Long parameter lists (> 3 params) | Use objects/structs/data classes |
| God objects/functions | Split by responsibility — one reason to change; classify red/green/gray per [`srp-cohesion.md`](srp-cohesion.md) |
| Premature optimization | Optimize when measured need exists |
| Error swallowing (empty catch blocks) | Log with context, rethrow or return error |
| Accessing external resources without validation | Validate at trust boundaries, access normally internally |
