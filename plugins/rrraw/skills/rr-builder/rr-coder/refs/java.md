# Java Standards (Version-Agnostic)

Version-specific features and prefer/avoid tables live in `java-17.md`, `java-21.md`, `java-25.md`.
This file covers cross-version principles: type safety, security, immutability, concurrency, error handling, logging, tooling.

## Always Avoid
- Raw types — always parameterize generics
- `null` returns from public APIs — use `Optional<T>` for nullable results
- Checked exceptions on interfaces — use unchecked domain exceptions
- `StringBuffer` — use `StringBuilder` or `String.formatted()`
- Legacy `Date`/`Calendar` — use `java.time.*` exclusively
- `Hashtable`, `Vector`, `Stack` — use `Map.of()`, `List.of()`, `Deque`
- Wildcard imports in production code — use explicit imports

## Type Safety

- No raw `Object` parameters in public APIs
- Prefer `sealed` + pattern matching over `instanceof` chains
- Prefer JSpecify `@NonNull` / `@Nullable` consistently for type nullability — do not use Jakarta annotations as type-nullability markers (Jakarta `@NotNull` is Bean Validation runtime, not static nullness)
- Compile with `-Xlint:all` and treat warnings as errors in CI

| Prefer | Avoid |
|--------|-------|
| Annotated nullness contracts + analysis (SpotBugs; NullAway when already in the project) | `Objects.requireNonNull` / `if (x == null)` / blank checks on paths already covered by annotated contracts |
| Narrow manual guards only at non-annotated interop / untyped foreign code | Defensive null/blank guards “just in case” after a validated boundary |

## Security

- Never concatenate user input into SQL — use `PreparedStatement` or JPA named params
- Never use `Runtime.exec()` or `ProcessBuilder` with unsanitized input
- Use `SecureRandom` — never `Math.random()` for security-sensitive values
- Validate all external input at system boundaries
- Never serialize/deserialize untrusted data with Java native serialization
- Use `MessageDigest` with SHA-256+ — never MD5 or SHA-1 for security
- Never log sensitive data: passwords, tokens, PAN, CVV, PII

## Style
- Prefer functional syntax (streams, lambdas, method references) when neither approach has a clear readability or performance advantage
- When structural code (loops, if/else) is more readable or intent-revealing, use it — functional is the default, not the mandate
- Prefer method references over equivalent lambdas
- Prefer least-necessary visibility (`private` → package-private → `protected` → `public`) per [§ Visibility / encapsulation](code.principles.md#visibility--encapsulation) (**CP031**)

## Immutability
- Prefer immutable objects — records, `Collections.unmodifiableX()`, `List.of()`
- Mark fields `final` by default
- Return defensive copies of mutable collections from public APIs

## Concurrency
- Never share mutable state without synchronization
- Prefer `java.util.concurrent` over `synchronized` blocks
- Use `CompletableFuture` for async pipelines — avoid blocking `.get()` without timeout
- Virtual threads (21+): see `java-21.md` for pinning gotchas and patterns

## Error Handling
- Define domain exception hierarchy rooted in unchecked exceptions
- Never swallow exceptions — log with full context or rethrow
- Use `try-with-resources` for all `AutoCloseable` resources
- Provide meaningful messages — include entity IDs, operation context

## Logging
- Use SLF4J API + Logback or Log4j2 implementation
- Structured logging via logstash-logback-encoder or equivalent
- Use parameterized logging: `log.info("Processing {}", id)` — never string concat
- Never log: passwords, tokens, card data, PII
- Cross-language Prefer/Avoid, disposition, **CP028**–**CP030**: [`observability.md`](observability.md)

## Tooling (enforce in CI)
- Build: Maven 3.9+
- Static analysis: SpotBugs + Find Security Bugs plugin
- Style: Checkstyle or Spotless
- Dependency audit: OWASP Dependency-Check
- Test: JUnit 5 + Mockito + AssertJ
