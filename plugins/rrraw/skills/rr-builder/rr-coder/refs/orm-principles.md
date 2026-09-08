# ORM Principles (JPA / Hibernate)

Principles for JPA entity design, fetch strategies, and transaction boundaries. Complements `java.spring.md` and `code.principles.md`.

## Fetch Strategy

### Avoid Lazy Loading by Default

Prefer **EAGER** or **explicit fetch joins** when the association is used in most code paths. Lazy loading causes N+1 queries, `LazyInitializationException` outside transactions, and hidden performance costs.

**Lazy is acceptable only when**:

1. **Usage < 70%** — The association is accessed in fewer than 70% of call sites. If most callers need it, fetch it eagerly or via join.
2. **Depth ≥ 2** — The association is nested (e.g. `order.getItems().get(0).getProduct()`). Loading at 2+ levels deep can stay lazy; loading at depth 1 (direct child) should usually be eager or fetched explicitly.

**Rule of thumb**: If you traverse the association in > 70% of usages, or it's a direct child (depth 1), avoid `FetchType.LAZY` — use EAGER, `@EntityGraph`, or `JOIN FETCH` in the query.

### Caller-Controlled Fetch

Prefer one repository method that accepts an `EntityGraph` or fetch-spec parameter — the caller decides what to load. Avoid multiple `findById`, `findByIdWithItems`, `findByIdWithItemsAndShipments` variants. Example: `Optional<Order> findById(Long id, EntityGraph<Order> graph)` — caller passes `EntityGraphs.from(Order.class).addAttributeNodes("items").build()` when items are needed.

### Transaction Boundaries

- Use `@Transactional(transactionManager = "...", readOnly = true)` on service methods that read entities and traverse associations. Ensures the session stays open for lazy loads if present.
- With multiple datasources, always specify `transactionManager` explicitly — never rely on default.

## Query Performance

- **Unbounded queries**: Never use `findAll()` for list endpoints — use `Pageable` or `LIMIT`. Even for lookup tables assumed small, add an explicit limit (e.g. 100–200) so unexpected volume growth won't break the service.
- **Cartesian products**: `JOIN FETCH` at most one collection per query. Multiple collections in one query multiply rows (order × items × products). Use separate queries or `@EntityGraph` subgraphs.
- **Count queries**: Use `repository.count()` or `SELECT COUNT(...)` — never load entities just to get `.size()`.
- **Open Session in View**: Set `spring.jpa.open-in-view=false`. Default `true` masks N+1 in controllers and couples view layer to persistence.

## Batch Operations

- Use `saveAll(entities)` with `spring.jpa.properties.hibernate.jdbc.batch_size` (e.g. 50) — never `save()` inside a loop.
- For bulk updates: use `@Modifying` JPQL (`UPDATE Entity SET ... WHERE ...`) — never load-then-save in a loop.

## Security

- **Native queries**: Always use `:param` named parameters in `@Query(nativeQuery=true)` — never string concatenation (SQL injection).
- **Entity exposure**: Never return JPA entities from controllers — map to DTOs at API boundary. Entities leak internal fields, lazy proxies, and enable mass assignment.
- **toString()**: Exclude sensitive fields (passwords, tokens, PII) from entity `toString()` — they end up in logs.
- **Cascade delete**: Use `CascadeType.REMOVE` / `orphanRemoval=true` only within the same aggregate root — never across trust boundaries.

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| EAGER or explicit fetch for associations used in > 70% of paths | LAZY on direct children used in most paths |
| `JOIN FETCH` / `@EntityGraph` for read-only queries | N+1 from lazy collections |
| One method with `EntityGraph` parameter — caller controls fetch | Multiple `findByIdWithX`, `findByIdWithY` variants |
| `@Transactional(readOnly = true)` on read methods | Accessing lazy associations outside transaction |
| Projections / DTOs for list/display queries | Loading full entity graphs for display |
| `Pageable` or `LIMIT` for list queries | `findAll()` on unbounded tables |
| `saveAll()` + `batch_size` for bulk inserts | `save()` inside loops |
| `@Modifying` JPQL for bulk updates | Load-then-save in loops |
| `repository.count()` or `SELECT COUNT(...)` | Loading entities to get `.size()` |
| `spring.jpa.open-in-view=false` | Default OSIV (masks N+1 in controllers) |
| Minimum cascade needed | `CascadeType.ALL` on every relationship |
| DTOs at API boundary | Returning JPA entities from controllers |
| Named params `:param` in native queries | String concatenation in `@Query` |

## Common Mistakes

**BUG**: LAZY association on `User.roles` — every auth call needs roles, so it's used 100% of the time.

**FIX**: Use EAGER, or `@Transactional(readOnly = true)` with explicit `transactionManager` if keeping LAZY for other reasons.

**BUG**: No `@Transactional` on service method that calls `user.getRoles()` — `LazyInitializationException` when session closes.

**FIX**: Add `@Transactional(transactionManager = "omxTransactionManager", readOnly = true)` to the service method.

**BUG**: `repository.save(entity)` inside a loop for 1000 records — 1000 round-trips, slow and resource-heavy.

**FIX**: Collect entities in a list, call `repository.saveAll(list)`, and set `hibernate.jdbc.batch_size=50`.

**BUG**: `SELECT o FROM Order o JOIN FETCH o.items JOIN FETCH o.shipments` — cartesian product (orders × items × shipments rows).

**FIX**: Fetch at most one collection per query. Use separate queries or `@EntityGraph` with distinct subgraphs.

**BUG**: `@Query("SELECT * FROM users WHERE name = '" + name + "'", nativeQuery = true)` — SQL injection.

**FIX**: Use `@Query("SELECT * FROM users WHERE name = :name", nativeQuery = true)` with `@Param("name")`.
