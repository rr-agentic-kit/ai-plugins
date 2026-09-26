# Java 17 Standards

## Version
Java 17 (LTS). First LTS after the 6-month cadence shift. Strong encapsulation of JDK internals is enforced.

## Java 17 Features — Use These
- **Records** — immutable data carriers, replace boilerplate DTOs
- **Sealed classes/interfaces** — restrict hierarchy, enable exhaustive logic
- **Pattern matching for `instanceof`** — binding variable eliminates casts
- **Switch expressions** (`->` syntax, yield) — prefer over switch statements
- **Text blocks** (`"""`) — multiline strings for SQL, JSON, XML
- **`Stream.toList()`** — returns unmodifiable list (no `Collectors.toList()` needed)
- **`NullPointerException` messages** — helpful NPEs enabled by default since 16
- **Enhanced pseudo-random generators** — `RandomGenerator` interface, `RandomGeneratorFactory`

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `record Point(int x, int y) {}` | POJO with manual equals/hashCode/toString |
| `sealed interface Shape permits Circle, Rect` | Open interface + instanceof chains |
| `if (obj instanceof String s)` | `if (obj instanceof String) { String s = (String) obj; }` |
| `switch (x) { case A -> ...; }` expression | `switch` statement with fall-through + break |
| `"""..."""` text blocks | `"line1\n" + "line2\n"` concatenation |
| `stream.toList()` | `stream.collect(Collectors.toList())` for unmodifiable result |
| `RandomGenerator.of("L64X128MixRandom")` | `new Random()` when better distribution needed |
| `List.of()`, `Map.of()`, `Set.of()` | `Collections.unmodifiableList(new ArrayList<>(...))` |
| `String.formatted()` or `"".formatted()` | `String.format()` (same result, reads better) |
| `Optional.isEmpty()` | `!optional.isPresent()` |

## Common Mistakes

### Sealed class without exhaustive switch
```java
// Compiles but misses future subtypes — no compiler warning in 17
sealed interface Shape permits Circle, Rect {}
// Switch expressions on sealed types aren't exhaustive until pattern matching for switch (21+)
// In 17: always include default branch
switch (shape.getClass().getSimpleName()) { ... } // fragile
```
Use visitor pattern or if-else with instanceof pattern matching until 21.

### Records are shallowly immutable
```java
// BUG: caller mutates the list inside the record
record Order(String id, List<Item> items) {}
var order = new Order("1", new ArrayList<>(items));
order.items().add(new Item("hack")); // mutates internal state

// FIX: defensive copy in compact constructor
record Order(String id, List<Item> items) {
    Order { items = List.copyOf(items); }
}
```

### Stream.toList() returns unmodifiable list
```java
// THROWS UnsupportedOperationException
var list = stream.toList();
list.add(item); // boom

// If you need mutable: collect to ArrayList explicitly
var list = stream.collect(Collectors.toCollection(ArrayList::new));
```

### Text block trailing whitespace silently stripped
```java
// Trailing spaces removed — use \s escape to preserve
var csv = """
    name,value\s
    foo,bar\s
    """;
```

## Not Available in 17 (Don't Generate)
- Virtual threads (21+)
- Pattern matching for switch — finalized (21+)
- Record patterns (21+)
- Sequenced collections (21+)
- Structured concurrency (preview 21+)
- Scoped values (preview 21+)
- `StructuredTaskScope`, `Thread.ofVirtual()` — not present
- String templates — never finalized, removed

## Library Choices

| Purpose | Library | Version | Notes |
|---------|---------|---------|-------|
| Build | Maven | 3.8+ | Or Gradle 7.x+ |
| Testing | JUnit 5 | 5.9+ | + Mockito 5.x + AssertJ 3.24+ |
| Static analysis | SpotBugs | 4.7+ | + Find Security Bugs |
| Annotations | JSpecify | 1.0 | `@NonNull`/`@Nullable` |
| JSON | Jackson | 2.15+ | Native record support |
| HTTP client | `java.net.http.HttpClient` | built-in | Replaces Apache HttpClient for simple cases |
