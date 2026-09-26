# input-resolution

**Owner:** Normalize raw flags and natural-language intent into a canonical payload before any agent invocation.

## Responsibilities

- Recognize primary action flags (exactly one per invocation, except `--init` exclusivity).
- Parse shared selectors: `--scope`, `--target`, `--output`, `--max-epochs`.
- Fall back to NL intent when no explicit action flag is present.
- Apply conflict matrix and precedence rules.
- Emit `NormalizedPayload` (see [contracts.md](contracts.md)) plus `resolution_trace`.

## Primary action flags

| Flag | `action` value |
|------|----------------|
| `--init` | `init` |
| `--assess` | `assess` |
| `--identify-missing` | `identify-missing` |
| `--identify-redundant-tests` | `identify-redundant` |
| `--write-tests` | `write` |
| `--complete-missing-tests` | `complete-missing` |
| `--generate-test-data` | `write-data` |
| `--write-parameterized-tests` | `write-parameterized` |
| `--plan-test-strategy` | `plan` |
| `--design-test-architecture` | `plan-architecture` |
| `--define-testing-pyramid` | `plan-pyramid` |
| `--audit-test-performance` | `perf-audit` |
| `--fix-broken-tests` | `fix-broken` |
| `--refactor-tests` | `refactor` |
| `--migrate-tests` | `migrate` |
| `--reduce-duplication` | `reduce-duplication` |
| `--diagnose-flaky` | `flaky` |
| `--debug-failing` | `debug` |

## Shared selectors

| Selector | Values | Default |
|----------|--------|---------|
| `--scope` | `repo`, `diff`, `uncommitted`, `paths:<csv>` | `diff` |
| `--target` | `frontend`, `backend`, `devops`, `scripts`, `auto` | `auto` |
| `--output` | `md`, `text`, `json`, `report` | `md` |
| `--max-epochs` | positive integer | `3` (multi-pass chains only) |

### Output mode notes

| Value | Behavior |
|-------|----------|
| `md` | Default — structured markdown tables with status column ([output-formats.md](output-formats.md)) |
| `text` | Concise plain-text bullets for quick chat glance |
| `json` | Full structured payload for CI/automation |
| `report` | **Deprecated alias** for `md` — normalize to `md` in `resolution_trace` |

### Scope normalization

1. Split `paths:<csv>` on commas; trim whitespace; dedupe; sort lexicographically.
2. Reject empty path lists after normalization.
3. One scope kind only per invocation.

## NL intent fallback

When no primary action flag is detected, map phrases (case-insensitive, first match wins):

| Intent signal | `action` |
|---------------|----------|
| init, bootstrap, discover stack, setup testing | `init` |
| assess, review tests, quality check | `assess` |
| missing tests, gaps, untested | `identify-missing` |
| redundant tests, duplicate coverage | `identify-redundant` |
| write tests, add tests, generate tests | `write` |
| complete missing, close gaps, full loop | `complete-missing` |
| plan strategy, test strategy | `plan` |
| fix tests, broken tests | `fix-broken` |
| migrate tests, port framework | `migrate` |
| flaky, intermittent failure | `flaky` |
| debug test, failing test | `debug` |
| slow tests, performance audit | `perf-audit` |

If multiple intent signals match with equal confidence → `AMBIGUOUS_ACTION`.

## Conflict matrix

| Dimension | Rule |
|-----------|------|
| Action | Exactly one primary action per invocation |
| `--init` | Mutually exclusive with all other primary actions |
| Scope | One scope kind only; `paths:` cannot combine with `repo`/`diff`/`uncommitted` |
| Target | Single value; `auto` resolves at assess/write time via stack detection |
| Output | Single value; `report` treated as `md` |

## Precedence

1. Explicit CLI flags beat NL intent.
2. Among explicit flags, left-to-right order in argv is tie-breaker for logging only; conflicts still error.
3. Defaults apply only after successful resolution (no error).

## Normalized payload schema

```json
{
  "action": "assess",
  "scope": { "kind": "diff", "paths": [] },
  "target": "auto",
  "output": "md",
  "max_epochs": 3,
  "chain": ["assess"],
  "write_mode": null,
  "resolution_trace": {
    "source": "flags",
    "flags_seen": ["--assess", "--scope", "diff"],
    "nl_matched": null,
    "errors": []
  }
}
```

### `write_mode` (write-family actions only)

| Action | `write_mode` |
|--------|--------------|
| `write` | `standard` |
| `write-data` | `test-data` |
| `write-parameterized` | `parameterized` |

### `chain` expansion (skill layer, not re-parsed here)

| `action` | Default `chain` |
|----------|-----------------|
| `complete-missing` | `["assess","identify-missing","plan","write","verify","assess"]` |
| `fix-broken` | `["fix","verify","assess"]` |
| `migrate` | `["migrate","verify","assess"]` |
| all others | single-agent name matching `action` or mapped agent |

## Deterministic errors

Stop immediately; do not invoke agents. Return `PhaseError` with code below.

| Code | Condition |
|------|-----------|
| `AMBIGUOUS_ACTION` | Zero or multiple primary actions after flag + NL resolution |
| `CONFLICTING_FLAGS` | Mutually exclusive flags (e.g. `--init` + `--assess`) |
| `INVALID_SCOPE_COMBINATION` | Multiple scope kinds or empty `paths:` list |
| `UNSUPPORTED_TARGET` | Target not in allowed set and not `auto` |

Error response shape: see [contracts.md](contracts.md) `PhaseError`.
