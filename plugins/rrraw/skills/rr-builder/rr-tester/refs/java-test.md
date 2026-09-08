# Java Test Reference (JUnit 5.11 + Mockito 5.x + Phoenix Testing)

## Commands

```bash
sdk env && mvn test                      # Run all tests
sdk env && mvn test -Dtest=ClassName     # Run specific test class
sdk env && mvn test -Dtest=ClassName#methodName  # Run specific method
```

## Test Annotations

| Annotation | Use Case | Spring Context |
|------------|----------|----------------|
| Plain JUnit | Business logic, utilities | None |
| `@WebMvcTest` | Controller unit tests | Partial |
| `@PhoenixWeblessIntegrationTest` | Service/repository integration | Full, no web |
| `@PhoenixWebIntegrationTest` | Full HTTP testing | Full + Web Server |

## Naming Convention

- Unit: `*UnitTest.java`
- Integration: `*IntegrationTest.java`

## Prefer / Avoid

| Prefer | Avoid |
|--------|-------|
| `@ParameterizedTest` with `@MethodSource` / `@CsvSource` for multi-data cases | Multiple `@Test` methods with same structure, different inputs |
| `@PhoenixWeblessIntegrationTest` for service tests | `@SpringBootTest` (slower, loads everything) |
| `@MockitoBean` (Spring Boot 3.4+) for mocks | `@MockBean` (deprecated, forces context reload) |
| AssertJ `assertThat(x).isEqualTo(y)` | JUnit `assertEquals(y, x)` (worse failure messages) |
| `enhancedSamePropertyValuesAs(expected, "id")` | Manual field-by-field assertions |
| `@PostgresDataSets` for test data | Manual SQL inserts in `@BeforeEach` |
| `@Nested` classes for state-based grouping | Flat test methods with repeated setup |
| Project `MockClock` and `TestingClock` (from project testing module) | `Mockito.mockStatic(Instant.class)` (fragile) |
| `byMask()` for partial matching | Complex Hamcrest matcher chains |
| Shared `@MockitoBean` on class level | `@MockitoBean` on individual test methods |

## Parameterized Tests

Use `@ParameterizedTest` when 3+ tests share identical structure, only input/expected differ. Prefer `@MethodSource` for complex args, `@CsvSource` for simple tuples.

```java
@ParameterizedTest(name = "{0} -> violates {2}")
@MethodSource("validationViolations")
void constructor_invalidFields_violatesValidation(String username, String password, String expectedProperty) {
    var violations = validator.validate(new AuthRequest(username, password));
    assertThat(violations).hasSize(1);
    assertThat(violations.iterator().next().getPropertyPath().toString()).isEqualTo(expectedProperty);
}
static Stream<Arguments> validationViolations() {
    return Stream.of(Arguments.of(null, "pass", "username"), Arguments.of("user", null, "password"));
}
```

## Phoenix-Specific Patterns

### Database Testing

```java
@PhoenixWeblessIntegrationTest
@PostgresDataSets(setUpDataSet = "datasets/users.xml")
class UserServiceIntegrationTest { }
```

### Time Mocking

`MockClock` and `TestingClock` from project testing module (project testing utilities module).

```java
// Unit: @Spy private Clock clock = TestingClock.ofFixed(LocalDateTime.of(2024, 1, 15, 10, 0));
// Integration: @Autowired Clock clock; @BeforeEach void setUp() { MockClock.mockFixed(clock, LocalDateTime.of(2024, 6, 15, 12, 0)); }
```

### Custom Matchers

```java
// Deep comparison, ignoring generated fields
assertThat(actual, enhancedSamePropertyValuesAs(expected, "id", "createdAt"));

// Partial match - only check non-null fields
var mask = new UserDto();
mask.setStatus("ACTIVE");
assertThat(actual, byMask(mask));
```

### Nested Test Organization

Use `@Nested` classes for state-based grouping (e.g. `WhenOrderIsPending`, `WhenOrderIsShipped`).

## Common Mistakes

For diagnostic rubrics and anti-patterns, see [test.heuristics.md](refs/test.heuristics.md).

### Using @SpringBootTest for service tests

BUG: `@SpringBootTest` loads full context including web server — slow, flaky. FIX: `@PhoenixWeblessIntegrationTest` for service/repository tests.

### @MockBean on individual tests

BUG: Each `@MockBean` variant creates new Spring context — slow suite. FIX: Declare `@MockitoBean` at class level, shared across tests.

### Mocking time with Mockito.mockStatic

BUG: `Mockito.mockStatic(Instant.class)` is fragile, leaks between tests. FIX: Use project `TestingClock` / `MockClock` abstraction.

### Missing dataset cleanup

BUG: `@BeforeEach` with manual SQL inserts — test data leaks, order-dependent failures. FIX: `@PostgresDataSets(setUpDataSet = "datasets/users.xml")`.
