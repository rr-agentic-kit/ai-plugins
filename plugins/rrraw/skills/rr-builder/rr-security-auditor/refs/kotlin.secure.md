# Kotlin Security (Spring Boot 3.5 / Spring Security 6.x)

Kotlin-specific secure implementation patterns. OWASP principles live in `secure.owasp.md`.

---

## Version

Kotlin 2.x, Spring Boot 3.5, Spring Security 6.x.

---

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| Data classes for DTOs | Exposing JPA entities in API |
| `@PreAuthorize` with SpEL | URL-only security |
| Kotlin null safety + explicit checks | Nullable without validation (Jackson can bypass) |
| `require()` / `check()` preconditions | Silent failures or unchecked assumptions |
| Sealed classes for error types | Generic exceptions leaking internals |
| Coroutine-safe SecurityContext propagation | Losing SecurityContext in coroutines |
| `@ConfigurationProperties` with data classes | `@Value` for secrets |

---

## Common Mistakes

### String interpolation in @Query — SQL injection
```kotlin
// BUG: Kotlin ${} interpolates at compile time; user input can be injected
@Query("SELECT u FROM User u WHERE u.email = '${email}'")
fun findByEmail(email: String): User?

// FIX: named parameter
@Query("SELECT u FROM User u WHERE u.email = :email")
fun findByEmail(@Param("email") email: String): User?
```

### SecurityContext lost in coroutine scope
```kotlin
// BUG: SecurityContextHolder uses ThreadLocal; coroutines switch threads
GlobalScope.launch(Dispatchers.IO) {
    val user = SecurityContextHolder.getContext().authentication  // null!
}

// FIX: use SecurityContextHolder strategy or propagate context
runBlocking {
    withContext(Dispatchers.IO) {
        SecurityContextHolder.setContext(/* captured before launch */)
        // or use DelegatingSecurityContextExecutorService
    }
}
```

### Data class copy() — mass assignment of sensitive fields
```kotlin
// BUG: copy() allows client to override any field
data class UserUpdate(val name: String, val role: String)
// Client sends {"name":"x","role":"ADMIN"} → role escalated

// FIX: DTO with only updatable fields; role changes via separate admin endpoint
data class UserUpdate(val name: String)
```

### Jackson bypasses Kotlin null safety on deserialization
```kotlin
// BUG: Jackson can deserialize null into non-null field; NPE or bad state
data class CreateOrderRequest(val items: List<Item>)  // items non-null
// Client sends {"items": null} → Jackson may set null, bypassing Kotlin

// FIX: validate at boundary, use @Valid + @NotNull, or @JsonSetter(nulls = Nulls.FAIL)
```

### Exposing entity with var mutable fields
```kotlin
// BUG: mutable entity returned; caller can modify internal state
@GetMapping("/users/{id}")
fun getUser(@PathVariable id: Long) = repo.findById(id).orElseThrow()

// FIX: map to DTO (data class with val only)
@GetMapping("/users/{id}")
fun getUser(@PathVariable id: Long) = repo.findById(id)
    .map { it.toResponse() }.orElseThrow()
```

---

## Search Patterns

```bash
rg "@Query.*\$\{" --type kotlin
```
SQL injection via Kotlin string interpolation.

```bash
rg "\.copy\(" --type kotlin
```
Potential mass assignment via data class copy.

```bash
rg "var\s+\w+.*:.*Entity" --type kotlin
```
Mutable entity fields (also check `@Entity` classes).

```bash
rg "GlobalScope\.launch|runBlocking" --type kotlin
```
Coroutine anti-patterns (security context loss).

```bash
rg "@RequestBody.*Entity" --type kotlin
```
Entity used as request body (mass assignment risk).

---

## Cross-References

- `secure.owasp.md` — language-agnostic OWASP patterns
- `secure.principles.md` — security rules and PII protection
- [`skills/code/coder/refs/java.spring.md`](../../code/coder/refs/java.spring.md) § Security — Spring Security config (shared with Java)
- `kotlin-v2.md` — general Kotlin patterns
- `java.secure.md` — many Spring Security patterns apply to both
