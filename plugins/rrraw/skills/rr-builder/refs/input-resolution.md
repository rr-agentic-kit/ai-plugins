# rr-builder input resolution

**Audience:** Every `rr-builder` invocation. Normalize before loading a nested skill.

## Primary lane detection

Exactly one **lane** unless user explicitly requested multi-lane review:

| Signal | `payload.lane` |
|--------|----------------|
| `--code`, `--test`, `--security`, `--all`, `--fix`, `--ci`, "review", "code review" | `review` |
| Any rr-tester primary flag (see [rr-tester/refs/input-resolution.md](../rr-tester/refs/input-resolution.md)) | `test` |
| `--security-audit`, "OWASP", "secrets audit", "vulnerability" (without review flags) | `security` |
| "implement", "refactor", "build", "add feature", plan with implementation tasks | `code` |
| Ambiguous | AskQuestion once: code \| test \| security \| review-all |

## Review flags (forward to rr-review)

Parse into `payload.review` when `lane: review`:

```yaml
lanes: [code, test, security]   # default --all; narrow with --code / --test / --security
outcome: report | fix | ci        # --fix | --ci
scope: MR | all                   # --scope MR|PR|all|full
paths: []                         # optional positional narrowers
```

Rules mirror [rr-review/refs/params.md](../rr-review/refs/params.md). Incompatible `--fix` + `--ci` → stop with one-line error.

## Test flags (forward to rr-tester)

When `lane: test`, pass through normalized flags per [rr-tester/refs/input-resolution.md](../rr-tester/refs/input-resolution.md). Parent does not re-parse test conflict matrix.

## Plan path

| Input | `payload.plan_path` |
|-------|---------------------|
| `docs/plans/*.md` explicit | that path |
| User path to plan doc | resolved path |
| Cascade dir with `status.yaml` | `docs/plans/` root |

Planning-only docs without implementation intent → `OUT_OF_SCOPE` → **rr-planner**.

## Natural language

| Pattern | Lane |
|---------|------|
| "write tests for", "coverage", "flaky" | test |
| "security review", "check for SQL injection" | security (or review if `--all`) |
| "review my changes", "PR review" | review |
| "implement", "fix bug in", "refactor" | code |

## Output payload (skill session)

```yaml
lane: code | test | security | review
plan_path: null | string
review: null | { lanes, outcome, scope, paths }
test: null | object   # rr-tester normalized payload
security_scope: null | { scope, paths }
code_scope: null | { scope, paths, plan_excerpt }
```

## Stop conditions

- `--fix` and `--ci` together
- No lane and user declines AskQuestion
- Request is clearly **rr-planner** or **rr-ci** only → redirect per [anti-overlap.md](anti-overlap.md)
