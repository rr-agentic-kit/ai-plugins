# Project detection (endless add-test subset)

Manifest-first detection for pre-flight, assess context, and toolchain phases. Resolve from **`REPO_ROOT`** (or scoped path).

## Detection order

| Project type | Manifest | Test framework | Module detection |
| ------------ | ------------- | ------------------- | ----------------------------------- |
| Maven | pom.xml | JUnit, TestNG | `<modules>` in pom.xml |
| Gradle | build.gradle* | JUnit, TestNG | `include()` in settings.gradle |
| npm | package.json | Jest, Vitest, Mocha | `workspaces` in package.json |
| Python | pyproject.toml, requirements.txt | pytest, unittest | packages under src/ or tests/ |
| Go | go.mod | testing | packages |
| Cargo | Cargo.toml | cargo test | workspace members |
| .NET | *.csproj | xUnit, NUnit, MSTest | solution projects |

**First manifest match at cwd** (walk parents if needed) wins.

## Test file patterns

| Project type | Patterns |
| ------------ | ------------------------------------------------------- |
| Java/Kotlin | `*Test.java`, `*Tests.java`, `*IT.java`, `*Test.kt` |
| npm/TS | `*.test.ts`, `*.spec.ts`, `*.test.vue`, `__tests__/*` |
| Python | `test_*.py`, `*_test.py` |
| Go | `*_test.go` |
| Cargo | `tests/*.rs`, `*_test.rs` |

Exclude: `node_modules`, `target`, `build`, `dist`, `.git`, `coverage`.

## Build and test commands

| Stack | Build | Test | Coverage (when present) |
| ----- | ----- | ---- | ------------------------- |
| Maven | `mvn -q clean package` | `mvn -q test` | `mvn -q test jacoco:report` or project script |
| npm | `npm run build` | `npm test` | `npm run test:coverage` or `npx vitest run --coverage` |
| Gradle | `./gradlew build` | `./gradlew test` | `./gradlew test jacocoTestReport` |
| Python | `pip install -e .` or `uv sync` | `pytest` | `pytest --cov` |
| Go | `go build ./...` | `go test ./...` | `go test -coverprofile=coverage.out ./...` |
| Cargo | `cargo build` | `cargo test` | `cargo llvm-cov` or project script |

Prefer repo-documented scripts in `package.json` / `Makefile` / `CONTRIBUTING.md` when they differ.

## No test framework

If no manifest with test support is found → report **"No test framework found"** and **hard stop** at pre-flight.

## Worker final gate timeout (fix)

**`test-endless-fix`** Phase B: default **900s** wall clock for combined **`build` + `test`**. Use **1200s** only when the repo documents a longer standard under **`REPO_ROOT`**. Never exceed documented cap + **300s**.

## Frontend framework (npm)

| Indicator | Framework |
| --------- | --------- |
| `nuxt.config.*` or `nuxt` dep | Nuxt |
| `vue` dep (no Nuxt) | Vue |
| `react` dep | React |
| `next` dep | Next.js |

Load language tactics from **`skills/rr-builder/rr-tester/refs/*-test.md`** during assess/fix.
