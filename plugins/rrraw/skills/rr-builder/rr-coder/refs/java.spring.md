# Spring Boot 3.5 Standards

## Version & Baseline
- Spring Boot 3.5.x on Java 21+
- Jakarta EE 10 namespace (not javax.*) — enforce across all imports
- Spring Framework 6.x patterns

## Project Structure
```
src/main/java/
├── application/       # Use cases / application services
├── domain/            # Entities, value objects, domain services, ports
├── infrastructure/    # Adapters: JPA, HTTP clients, messaging
└── api/               # Controllers, request/response DTOs
```
Domain layer has zero Spring dependencies. Infrastructure depends on domain, never reverse.

## Configuration

- Use `@ConfigurationProperties` with validated records/classes — never `@Value` for structured config
- Validate config at startup: `@Validated` + Bean Validation (`@NotNull`, `@NotBlank`, `@Size`, …) — `@Validated` is for **config only**, not a default on every `@Service`
- Externalize all secrets via environment variables — never in `application.yml`
- Use Spring profiles correctly: `default`, `local`, `staging`, `production`
- Never commit `application-production.yml` with real values

## Web Layer

- Use `@RestController` + `@RequestMapping` — never mix `@Controller` with `@ResponseBody` ad-hoc
- Request/response DTOs as Java records — never expose JPA entities directly
- Validate all incoming requests with `@Valid` + Bean Validation on DTO fields/records (Jakarta Validation 3.x)
- Return `ResponseEntity<T>` for explicit HTTP status control
- Use `@ControllerAdvice` + `@ExceptionHandler` for centralized error handling
- Always return RFC 7807 Problem Details (`ProblemDetail`) for errors

| Prefer | Avoid |
|--------|-------|
| Field/record BV constraints on request/response DTOs; drop controller/service manual null/blank guards that duplicate them | Manual validation scattered in controllers |
| JSpecify `@NonNull` / `@Nullable` on Spring bean method signatures for nullness | Class-level `@Validated` + method-parameter `@NotNull`/`@NotBlank` as the project pattern for services |
| Domain layer Spring-free — nullness via JSpecify / design, not BV | Bean Validation or Spring validation annotations in `domain/` |

## Security (Spring Security 6.x)

- Never disable CSRF without justification and compensating controls
- Use method security (`@PreAuthorize`) for business-level authorization
- Never store passwords in plain text — BCrypt with strength ≥ 12
- Configure `SecurityFilterChain` as beans — never extend `WebSecurityConfigurerAdapter`
- Use `@Secured` or SpEL expressions — never hardcode roles as strings scattered in code
- For PCI scope endpoints: require MFA evidence in JWT claims and log all access

## Data Layer
- Use Spring Data JPA repositories — no raw `EntityManager` unless performance-justified
- Never use `@Query` with string concatenation — use named params `:param` or `?1`
- Use `@Transactional` at service layer — never on repository methods directly
- Fetch strategy: see `orm-principles.md` — avoid lazy when usage &gt; 70% or depth 1
- Use database migrations: Flyway (preferred) or Liquibase — never `ddl-auto=update` in production
- Use projections or DTOs for read-only queries — never load full entities for display

## Observability
- Micrometer metrics exposed via Actuator — secure `/actuator` endpoints
- Use `@Observed` or manual `Observation` API for business operation tracing
- Structured logging with Logback + logstash encoder
- Correlate logs with trace IDs via Micrometer Tracing (Brave/OTEL)
- Never expose sensitive data through Actuator endpoints
- Prefer low-cardinality meter tags; avoid unbounded ids as label keys
- Cross-language Prefer/Avoid, disposition, **CP028**–**CP030**: [`observability.md`](observability.md) — refactor may hygiene existing logs only; never silent-add `@Observed`/meters

## Virtual Threads (Spring Boot 3.2+)
- Enable: `spring.threads.virtual.enabled=true`
- No thread pool tuning needed for I/O-bound work — virtual threads handle it
- Avoid `synchronized` blocks on virtual threads — use `ReentrantLock`

## Testing
- `@SpringBootTest` only for full integration tests — use slices for unit tests
- `@WebMvcTest` for controller layer, `@DataJpaTest` for repository layer
- `Testcontainers` for real database/messaging integration tests
- Never mock infrastructure in unit tests of domain logic — domain has no Spring deps
- Use `@MockitoBean` (3.4+) instead of deprecated `@MockBean`

## Actuator / Production Readiness
- Expose only: `health`, `info`, `metrics`, `prometheus` — disable all others in production
- Implement proper `HealthIndicator` for critical dependencies
- Configure graceful shutdown: `server.shutdown=graceful`
- Set `management.endpoints.web.exposure.include` explicitly — never use `*`
