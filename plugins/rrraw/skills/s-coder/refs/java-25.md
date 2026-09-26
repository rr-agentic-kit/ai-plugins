# Java 25 Standards

## Version
Java 25 (LTS, Sep 2025). Builds on 21 with module imports, flexible constructors, scoped values finalized, and AOT improvements.

## Java 25 Features — Use These
- **Module import declarations** (JEP 511) — `import module java.base;` imports all public packages
- **Flexible constructor bodies** (JEP 513) — statements before `super()`/`this()` calls (validation, computation)
- **Compact source files / instance main methods** (JEP 512) — simplified entry points, implicit class
- **Scoped values** (JEP 506, finalized) — `ScopedValue` replaces `ThreadLocal` for virtual thread context
- **Compact object headers** (JEP 519) — reduced object memory footprint (~8 bytes saved per object)
- **Generational Shenandoah** (JEP 521) — production-ready low-pause GC
- **Key Derivation Function API** (JEP 510) — HKDF, standard KDF support
- **Post-quantum crypto** (inherited from 24) — ML-KEM (FIPS 203) and ML-DSA (FIPS 204) available via standard `KeyPairGenerator`/`KEM`/`Signature` APIs
- **JFR cooperative sampling + method timing** (JEP 518/520) — better profiling with lower overhead
- **JFR CPU-time profiling** (JEP 509, experimental) — per-thread CPU-time sampling
- **AOT profiling + CLI ergonomics** (JEP 514/515) — faster startup via ahead-of-time method profiling

## Still Preview / Incubator in 25 (Don't Use — No `--enable-preview`)
- **Structured concurrency** (JEP 505, 5th preview) — `StructuredTaskScope` API still evolving
- **Primitive types in patterns** (JEP 507, 3rd preview) — `case int i ->` in switch
- **Stable values** (JEP 502, preview) — lazy-initialized immutable holders
- **PEM encodings of cryptographic objects** (JEP 470, preview) — encode/decode keys, certs as PEM strings
- **Vector API** (JEP 508, 10th incubator) — SIMD operations

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `import module java.base;` for utility classes | Long import lists for `java.util.*`, `java.io.*`, etc. |
| `ScopedValue.runWhere(KEY, val, task)` | `ThreadLocal` with virtual threads (memory leak risk) |
| `ScopedValue.orElse(default)` (non-null default) | `ScopedValue.orElse(null)` — throws `IllegalArgumentException` in 25 |
| Flexible constructor: validate before `super()` | Workaround static factory just to validate args |
| `-XX:+UseCompactObjectHeaders` | Default headers when memory-constrained |
| `-XX:+UseShenandoahGC` for low-latency | Shenandoah without generational (old mode) |
| KDF API for key derivation | Manual HMAC-based key derivation |
| ML-KEM-768/1024 for new key encapsulation | RSA key exchange (not quantum-resistant) |
| ML-DSA-65/87 for new digital signatures | RSA/ECDSA only (plan migration timeline) |
| JFR method timing for production profiling | Sampling-only profilers for method-level insight |

## Common Mistakes

### ScopedValue.orElse(null) now throws
```java
// WORKED in preview (21-24), BREAKS in 25
ScopedValue<String> TENANT = ScopedValue.newInstance();
String val = TENANT.orElse(null); // IllegalArgumentException

// FIX: use orElse with non-null default, or isBound() check
String val = TENANT.isBound() ? TENANT.get() : null;
// Or: provide a meaningful default
String val = TENANT.orElse("default-tenant");
```

### Flexible constructors — still can't read `this` before super()
```java
class Child extends Parent {
    Child(String name) {
        // OK: validate args, compute values before super()
        if (name == null) throw new IllegalArgumentException("name required");
        var normalized = name.strip().toLowerCase();
        super(normalized);
    }

    Child(int id) {
        // COMPILE ERROR: can't access this.field before super()
        this.id = id; // not allowed
        super(id);
    }
}
```

### Module imports shadow explicit imports unexpectedly
```java
import module java.base;    // imports java.util.List, etc.
import com.myapp.util.List; // this specific import wins (explicit > module)
// But be aware: adding module imports to existing code can surface
// ambiguities if two modules export same simple name
```

### Structured concurrency is still preview — don't use
```java
// DON'T generate — requires --enable-preview which we don't enable
// Use CompletableFuture for async pipelines instead
CompletableFuture<A> a = CompletableFuture.supplyAsync(() -> fetchA(), executor);
CompletableFuture<B> b = CompletableFuture.supplyAsync(() -> fetchB(), executor);
CompletableFuture.allOf(a, b).join();
```

### Virtual thread pinning (still applies from 21)
```java
// synchronized still pins virtual threads in 25
// Use ReentrantLock for any block that does I/O
// Run with -Djdk.tracePinnedThreads=short to detect
```

## Not Available in 25 (Don't Generate)
- Value classes / value objects — still Valhalla EA, not in any JDK release
- String templates — removed after preview, not coming back in current form
- Vector API — still incubator, unstable API
- Any feature requiring `--enable-preview` — structured concurrency, primitive patterns, stable values, PEM encodings

## Migrating from 21 to 25

| Area | Change |
|------|--------|
| `ScopedValue` | Finalized — update `orElse(null)` calls |
| Constructors | Can now validate/compute before `super()` — simplify static factory workarounds |
| Imports | `import module java.base;` reduces boilerplate in utility-heavy files |
| GC | Evaluate Generational Shenandoah alongside ZGC for latency-sensitive services |
| Profiling | Enable JFR method timing in production for low-overhead method-level metrics |
| Object headers | Test `+UseCompactObjectHeaders` — significant memory savings for object-heavy workloads |
| Crypto | ML-KEM + ML-DSA available — start evaluating for harvest-now-decrypt-later threat model |

## Library Choices

| Purpose | Library | Version | Notes |
|---------|---------|---------|-------|
| Build | Maven | 3.9+ | Or Gradle 8.x+ |
| Testing | JUnit 5 | 5.11+ | + Mockito 5.x + AssertJ 3.26+ |
| Static analysis | SpotBugs | 4.8+ | + Find Security Bugs |
| Annotations | JSpecify | 1.0 | `@NonNull`/`@Nullable` |
| JSON | Jackson | 2.18+ | Java 25 compatible |
| Dep audit | OWASP Dependency-Check | 10.x+ | Or Snyk |
| Profiling | JDK Mission Control | 9.x | JFR analysis |
