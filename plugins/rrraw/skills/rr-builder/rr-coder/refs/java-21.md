# Java 21 Standards

## Version
Java 21 (LTS). Major release: virtual threads, pattern matching for switch, and record patterns all finalized.

## Java 21 Features — Use These
- **Virtual threads** (JEP 444) — `Thread.ofVirtual().start()`, lightweight threads for I/O-bound work
- **Pattern matching for switch** (JEP 441) — exhaustive switch with type patterns, guarded patterns
- **Record patterns** (JEP 440) — deconstruct records in switch and instanceof
- **Sequenced collections** (JEP 431) — `SequencedCollection`, `SequencedSet`, `SequencedMap` with `getFirst()`, `getLast()`, `reversed()`
- **Structured concurrency** (preview) — `StructuredTaskScope` for fan-out/fan-in
- **Scoped values** (preview) — `ScopedValue` replaces `ThreadLocal` for virtual threads
- **Generational ZGC** (JEP 439) — default ZGC mode, better throughput

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `Thread.ofVirtual().start(runnable)` for I/O tasks | Platform thread pools for I/O-bound work |
| `Executors.newVirtualThreadPerTaskExecutor()` | Fixed thread pools for request-per-thread servers |
| `switch (obj) { case String s -> ... }` | `if/else instanceof` chains |
| `case String s when s.length() > 5 ->` (guarded) | Pattern match then `if` inside case body |
| `case Point(int x, int y) ->` record pattern | `case Point p -> { int x = p.x(); }` |
| `list.getFirst()` / `list.getLast()` | `list.get(0)` / `list.get(list.size() - 1)` |
| `list.reversed()` | `Collections.reverse(new ArrayList<>(list))` |
| `sealed` + exhaustive switch (no default) | Default branch on sealed types (hides missing cases) |
| `-XX:+UseZGC` (generational by default) | `-XX:+UseZGC -XX:-ZGenerational` unless benchmarked |

## Common Mistakes

### Virtual threads + synchronized = pinning
```java
// BUG: virtual thread pins to carrier thread inside synchronized
synchronized (lock) {
    httpClient.send(request, handler); // blocks carrier thread
}

// FIX: use ReentrantLock — virtual threads unmount on lock contention
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    httpClient.send(request, handler);
} finally {
    lock.unlock();
}
```
Run with `-Djdk.tracePinnedThreads=short` to detect pinning in dev/test.

### Virtual threads + thread pools = wasted
```java
// WRONG: defeats the purpose — limits concurrency artificially
var executor = Executors.newFixedThreadPool(100);
executor.submit(virtualThreadTask);

// RIGHT: one virtual thread per task, no pooling
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    futures.forEach(f -> executor.submit(f));
}
```

### Virtual threads + ThreadLocal = memory leak
```java
// BAD: millions of virtual threads × ThreadLocal = OOM
private static final ThreadLocal<ExpensiveObject> cache = ThreadLocal.withInitial(...);

// FIX: use ScopedValue (preview) or pass context explicitly
private static final ScopedValue<RequestContext> CTX = ScopedValue.newInstance();
ScopedValue.runWhere(CTX, context, () -> handleRequest());
```

### Exhaustive switch on sealed type — forgetting new subtypes
```java
sealed interface Event permits Created, Updated, Deleted {}
// Compiler enforces exhaustiveness — adding a new permit forces all switches to update
// This is the point: don't add a default branch
switch (event) {
    case Created c -> handle(c);
    case Updated u -> handle(u);
    case Deleted d -> handle(d);
    // NO default — compiler catches missing cases
}
```

### Record pattern null handling
```java
// NPE: record pattern doesn't match null
switch (obj) {
    case Point(var x, var y) -> use(x, y);
    // case null -> ... // must handle explicitly if obj can be null
}
```

## Not Available in 21 (Don't Generate)
- Scoped values — preview only, API may change
- Structured concurrency — preview only, API may change
- String templates — preview, later removed entirely
- Module import declarations (25+)
- Flexible constructor bodies (25+)
- Compact source files / instance main methods — preview only
- Value classes — not present

## Library Choices

| Purpose | Library | Version | Notes |
|---------|---------|---------|-------|
| Build | Maven | 3.9+ | Or Gradle 8.x+ |
| Testing | JUnit 5 | 5.10+ | + Mockito 5.x + AssertJ 3.25+ |
| Static analysis | SpotBugs | 4.8+ | + Find Security Bugs |
| Annotations | JSpecify | 1.0 | `@NonNull`/`@Nullable` |
| JSON | Jackson | 2.16+ | Full record pattern support |
| HTTP client | `java.net.http.HttpClient` | built-in | Works well with virtual threads |
| Concurrency testing | JCStress | latest | Validate lock-free / virtual thread code |
