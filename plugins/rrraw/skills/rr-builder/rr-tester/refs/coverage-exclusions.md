# coverage-exclusions

**Owner:** Non-testable taxonomy, stack exclusion patterns, verification rules, and single-source-of-truth guidance.

Referenced by: assess, identify-missing, plan, write, init-discovery.

## Non-testable taxonomy

Classify production files into one category before emitting `missing_test`. When matched, emit `non_testable` (assess) → `excluded[]` (identify-missing) → `exclude` track (plan) → `coverage_exclude` (write).

| Category | `category` value | Indicators |
|----------|------------------|------------|
| Type-only | `type_only` | Interfaces, type aliases, `*.d.ts`, sealed marker types with no behavior |
| Constants / enums | `constants` | `const` maps, enum declarations, config literals with no logic |
| Barrel re-exports | `barrel` | `index.ts` / `__init__.py` that only re-export symbols |
| Route / layout shells | `route_shell` | Framework route/layout files with no branch logic (Next.js layout, React Router shell) |
| Storybook / fixture-only | `fixture` | `*.stories.*`, `*.fixture.*`, test-only data builders not imported by production |
| Dev-only diagnostic | `dev_diagnostic` | Trace hooks, debug-only middleware, `__DEV__` gated utilities |
| Generated | `generated` | `*.generated.*`, `*_pb.go`, OpenAPI client stubs, `@Generated` / `// Code generated` markers |

**Rule:** `non_testable` and `missing_test` are mutually exclusive for the same production path. Low-risk heuristic (`trivial getters`, generated code, thin delegates) routes here when a non-testable category applies; otherwise `missing_test` with `risk: low`.

## Stack discovery patterns

Discover existing exclusion config during init and write. Prefer updating a shared list over duplicating paths per tool.

| Stack / tool | Config location | Pattern |
|--------------|-----------------|---------|
| Vitest | `vitest.config.*` | `coverage.exclude` glob array |
| Jest | `jest.config.*` | `collectCoverageFrom` negation or `coveragePathIgnorePatterns` |
| Istanbul / nyc | `package.json` or `.nycrc` | `exclude` array |
| JaCoCo | `pom.xml` / `build.gradle` | `<excludes>` / `jacocoTestCoverageVerification` excludes |
| SonarQube | `sonar-project.properties` / CI | `sonar.coverage.exclusions` |
| .NET coverlet | `*.csproj` / `Directory.Build.props` | `<Exclude>` / `[ExcludeFromCodeCoverage]` |
| pytest-cov | `pyproject.toml` / `setup.cfg` / CLI | `--cov-omit` or `[tool.coverage.run] omit` |

### Single source of truth

1. Prefer one shared exclusion list (e.g. `coverage-exclusions.json`, `coverage-exclude.txt`, or repo convention documented in CLAUDE.md).
2. Runner config and Sonar (when present) should reference the same paths/globs — write agent updates **all** configured targets in one exclude step.
3. When only one tool is configured, update that tool and document the shared-list recommendation in CLAUDE.md § Coverage exclusions.

## Verify step

After config edit in write `exclude` track:

1. Rerun the project's primary coverage command (from CLAUDE.md § Run command or discovered CI).
2. Assert each excluded production path is **absent** from lcov/html report file list (or Sonar shows exclusion effective).
3. Populate `coverage_verify` on write output:
   - `passed: true` + `paths_confirmed[]` when all paths verified
   - `passed: false` + `failures[]` with path and reason when any path still appears in coverage

### When no coverage tooling

- Apply config-only changes (shared list + CLAUDE.md documentation).
- Set `validation_pipeline.coverage_verify.skipped: true` with note `"no coverage runner configured"`.
- `coverage_verify.passed` may be `null`; status `excluded` still requires config written and documented.

## Tooling targets field

`excluded[].tooling_targets` and plan `exclude[].tooling` use detected runner keys: `vitest`, `jest`, `nyc`, `jacoco`, `sonar`, `coverlet`, `pytest`, `shared_list`.

Only include tools actually configured in the repo.
