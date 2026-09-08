# Java Security (Spring Boot 3.5 / Spring Security 6.x)

Java-specific secure implementation patterns. OWASP principles live in `secure.owasp.md`.

---

## Version

Java 21+, Spring Boot 3.5, Spring Security 6.x, Jakarta EE 10.

---

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `PreparedStatement` / JPA named params (`:param`, `?1`) | String concatenation in queries |
| `@PreAuthorize` / method security | URL-only security (path matchers alone) |
| BCrypt strength ≥ 12 | MD5, SHA1, SHA-256 for passwords |
| `@Valid` + Bean Validation | Manual validation scattered in controllers |
| `@ConfigurationProperties` for secrets | `@Value` with defaults in code |
| `SecurityFilterChain` bean | Deprecated `WebSecurityConfigurerAdapter` |
| Records for DTOs | Exposing JPA entities in API responses |
| `ProblemDetail` (RFC 7807) for errors | Stack traces or raw exception messages |
| `@JsonIgnore` on sensitive entity fields | Mass assignment (role, isAdmin, passwordHash) |

---

## Common Mistakes

### SQL injection via @Query string concat
```java
// BUG: SpEL #{#email} injects param into query string
@Query("SELECT u FROM User u WHERE u.email = '" + "#{#email}" + "'")
User findByEmail(@Param("email") String email);

// FIX
@Query("SELECT u FROM User u WHERE u.email = :email")
User findByEmail(@Param("email") String email);
```

### Missing @PreAuthorize on admin endpoints
```java
// BUG: any authenticated user can call
@DeleteMapping("/admin/users/{id}")
void deleteUser(@PathVariable Long id) { ... }

// FIX
@PreAuthorize("hasRole('ADMIN')")
@DeleteMapping("/admin/users/{id}")
void deleteUser(@PathVariable Long id) { ... }
```

### Exposing JPA entity (leaks password hash, internal fields)
```java
// BUG
@GetMapping("/users/{id}")
User getUser(@PathVariable Long id) { return repo.findById(id).orElseThrow(); }

// FIX: return DTO
@GetMapping("/users/{id}")
UserResponse getUser(@PathVariable Long id) {
    return repo.findById(id).map(UserMapper::toResponse).orElseThrow();
}
```

### CSRF disabled without justification
```java
// BUG: stateless API still needs CSRF for browser clients with cookies
http.csrf(csrf -> csrf.disable());

// FIX: for REST APIs using JWT, document why; for form-based auth, keep CSRF
http.csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()));
```

### Hardcoded secrets in application.yml
```yaml
# BUG
spring:
  datasource:
    password: "prod-secret-123"

# FIX: env var
spring:
  datasource:
    password: ${DB_PASSWORD}
```

### Wrong role prefix with @Secured
```java
// BUG: hasRole adds ROLE_ prefix — results in ROLE_ROLE_ADMIN
@PreAuthorize("hasRole('ROLE_ADMIN')")

// FIX
@PreAuthorize("hasRole('ADMIN')")
// or @Secured("ROLE_ADMIN") when using full authority name
```

---

## Search Patterns

```bash
rg "@Query.*\+\s*" --type java
```
SQL injection in Spring Data `@Query`.

```bash
rg "executeQuery\s*\([^?]*\+[^)]*\)" --type java
```
JDBC string concatenation in `executeQuery`.

```bash
rg "(SECRET|PASSWORD|KEY)\s*[:=]\s*['\"][^'\"]+['\"]" -t java -t yaml
```
Hardcoded secrets.

```bash
rg "@(Get|Post|Put|Delete)Mapping" --type java -A 5 | rg -v "@PreAuthorize|@Secured"
```
Unprotected endpoints (manual review — may have class-level security).

```bash
rg "csrf\(\)\.disable" --type java
```
CSRF disabled.

```bash
rg "@RequestBody.*Entity" --type java
```
Entity used as request body (mass assignment risk).

---

## Cross-References

- `secure.owasp.md` — language-agnostic OWASP patterns
- `secure.principles.md` — security rules and PII protection
- [`skills/code/coder/refs/java.spring.md`](../../code/coder/refs/java.spring.md) § Security — Spring Security config patterns
- `java.md` — general Java patterns
