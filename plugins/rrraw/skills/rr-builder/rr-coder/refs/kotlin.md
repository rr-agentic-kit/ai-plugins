# Kotlin 2.x Standards

## Version
Kotlin 2.1+ with K2 compiler (default). Target JVM 21. Spring Boot 3.5 with `kotlin-spring` and `kotlin-jpa` plugins.

## K2 Compiler — What Changed
- ~2x faster compilation; smart casts across `if`/`when` branches, logical `or`, inline functions, exception handling
- Stricter type inference: destructuring, SAM constructors, projected types, qualifier resolution

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `sealed interface` + exhaustive `when` (no `else`) | `enum` for types with data or open hierarchies |
| `value class UserId(val value: String)` | Raw `String`/`Long` for domain IDs |
| `data class` for DTOs, `data object` for singletons | Plain `class` with manual `equals`/`hashCode` |
| `?.let { }` / `?:` Elvis for null handling | `!!` (hides null bugs, crashes in prod) |
| `require()` / `check()` for preconditions | `if (!cond) throw IllegalArgumentException(...)` |
| `buildList { }` / `buildMap { }` | Mutable collection + manual `add` |
| `sequence { }` for lazy large collections | `list.map { }.filter { }` chains on large data |
| `getOrElse` / `getOrDefault` | `map[key]!!` or unchecked index access |
| `runCatching` + `Result` for expected failures | `try/catch` for control flow |
| `when (val x = expr)` scoped binding | `val x = expr; when { x is ... }` |
| Extension functions for cross-cutting utils | Utility classes with static methods |
| `object` for stateless singletons | `class` with all-static members |
| `also { log(it) }` for side-effects in chains | Breaking chains to add logging |
| `@JvmStatic` / `@JvmOverloads` for Java interop | Companion functions without JVM annotations |

## Spring Boot 3 + Kotlin

### Essential Plugins
```kotlin
plugins {
    kotlin("plugin.spring")   // opens @Component, @Service, @Configuration, etc.
    kotlin("plugin.jpa")      // no-arg constructor for @Entity
    kotlin("plugin.allopen")  // custom allopen targets if needed
}
```

### JPA Entities — Not Data Classes
```kotlin
@Entity
class Order(
    @Id @GeneratedValue var id: Long? = null,
    @Column(nullable = false) var status: String,
    @ManyToOne(fetch = FetchType.LAZY) var customer: Customer? = null
) {
    override fun equals(other: Any?) = other is Order && id != null && id == other.id
    override fun hashCode() = javaClass.hashCode()
}
```
JPA needs: mutable properties, non-final class (plugin.spring handles), no-arg constructor (plugin.jpa handles). Data classes break lazy loading and proxy creation.

### Annotation Targeting (2.2+)
Pre-2.2: annotations default to constructor param only — use `@field:NotBlank`. With 2.2+ flag `-Xannotation-default-target=param-property`, `@NotBlank` hits the field automatically.

## Coroutines

### Dispatcher Selection
| Dispatcher | Use For |
|------------|---------|
| `Dispatchers.Main` | UI updates, state management |
| `Dispatchers.IO` | Network, file, DB, JSON parsing |
| `Dispatchers.Default` | CPU-intensive (sorting, computation) |
| `Dispatchers.Unconfined` | Almost never — testing edge cases only |

### Structured Concurrency Rules
- Never use `GlobalScope` — creates uncontrolled coroutines, untestable, leaks
- Coroutines must not outlive their parent scope
- Use `supervisorScope` when child failures shouldn't cancel siblings
- Use `coroutineScope` when any child failure should cancel all

### Spring WebFlux
Spring handles `suspend fun` bridging automatically with `kotlinx-coroutines-reactor`. Declare controller methods as `suspend` — no Mono/Flux wrapping needed.

## Common Mistakes

### `!!` operator — NPE factory
```kotlin
// BUG: crashes at runtime when user is null
val name = repository.findById(id)!!.name

// FIX: handle null explicitly
val name = repository.findById(id)?.name
    ?: throw NotFoundException("User $id not found")
```

### Data class as JPA entity — broken proxies
```kotlin
// BUG: equals/hashCode uses all fields, breaks lazy loading, no proxy support
@Entity data class User(val id: Long, val name: String)

// FIX: regular class with manual equals/hashCode on id only (see above)
```

### Catching CancellationException — zombie coroutines
```kotlin
// BUG: swallows cancellation, coroutine never stops
launch {
    while (true) {
        try { doWork(); delay(1000) }
        catch (e: Exception) { /* swallows CancellationException */ }
    }
}

// FIX: check isActive, rethrow CancellationException
launch {
    while (isActive) {
        try { doWork() }
        catch (e: Exception) { if (e is CancellationException) throw e }
        delay(1000)
    }
}
```

### Inline + coroutines — broken lifecycle
```kotlin
// BUG: non-local return breaks coroutine
inline fun doAsync(block: () -> Unit) { /* ... */ }
// FIX: crossinline for lambdas passed to coroutine builders
inline fun doAsync(crossinline block: () -> Unit) { /* ... */ }
```

### Sealed interface + `else` in when — hides missing cases
```kotlin
// BUG: else hides missing cases when new subtypes added
when (event) { is Event.Created -> handle(event); else -> ignore() }
// FIX: no else — compiler forces update on new subtypes
when (event) { is Event.Created -> handle(event); is Event.Deleted -> remove(event) }
```

## Not Available / Preview Only (Don't Generate as Stable)
- Guard conditions in `when` — preview in 2.1, requires `-Xwhen-guards`
- Non-local `break`/`continue` — preview in 2.1
- Multi-dollar string interpolation — preview in 2.1
- Context receivers — experimental, API unstable

## Library Choices

| Purpose | Library | Version | Notes |
|---------|---------|---------|-------|
| Build | Gradle + Kotlin DSL | 8.x+ | `kotlin("jvm")` plugin 2.1+ |
| DI / Web | Spring Boot | 3.5+ | With `kotlin-spring` plugin |
| Testing | JUnit 5 + MockK | MockK 1.13+ | + AssertJ 3.25+ or kotest assertions |
| Coroutines | kotlinx-coroutines | 1.9+ | + `kotlinx-coroutines-reactor` for WebFlux |
| Serialization | Jackson Kotlin module | 2.17+ | `registerKotlinModule()` required |
| Serialization (alt) | kotlinx-serialization | 1.7+ | Compile-time, no reflection |
| HTTP client | Ktor Client | 3.0+ | Or `java.net.http.HttpClient` with coroutines |
| Validation | Jakarta Validation | 3.1+ | Use `@field:` target pre-2.2 |
| Static analysis | detekt | 1.23+ | Kotlin-native linter |

## Logging / Diagnostics

| Prefer | Avoid |
|--------|-------|
| SLF4J parameterized / structured logging (same as Java) | String templates concatenated into log messages |
| Redact secrets, tokens, PII from log args | Passwords, bearer tokens, PAN in log arguments |
| Micrometer / `@Observed` patterns from Spring peers when present | Silent new critical edges with no meter while siblings instrument |

Cross-language Prefer/Avoid, disposition, **CP028**–**CP030**: [`observability.md`](observability.md). Spring detail: [`java.spring.md`](java.spring.md) §Observability.
