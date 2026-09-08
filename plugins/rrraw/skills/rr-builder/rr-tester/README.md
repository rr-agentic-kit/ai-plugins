# rr-tester

Flag-driven test excellence for **rr-builder**. Former **`rr-test`** flags route here via the parent skill.

**Runtime:** [SKILL.md](SKILL.md) · **Policies:** [refs/](refs/)

## Goals

Normalize test flags, delegate to `agents/test/*` phase agents, and emit structured assess/write/fix/migrate/flaky output with exhaustive per-epoch scope coverage.

## Scope / limits

- Test excellence only — production standards → **rr-coder**; security → **rr-security-auditor**
- Skill owns routing and epoch loops; agents execute one phase each
- Selector defaults and conflict rules live in [refs/input-resolution.md](refs/input-resolution.md)

## Audience

Agents loaded by **rr-builder** or **rr-review** test lane when test flags are set.

## When to use

`--init`, `--assess`, `--complete-missing-tests`, `--fix-broken-tests`, `--migrate-tests`, `--diagnose-flaky`, and other primary action flags (see [SKILL.md](SKILL.md)).

## Philosophy

- **High-signal tests** — Fail when protected behavior breaks (oracle validation).
- **Non-testable → exclude** — Type-only, generated, and barrel files get coverage exclusion.
- **Determinism** — Same inputs → same scope, ordering, routing.
- **Exhaustive per-epoch** — Every file in scope assessed; residuals at epoch cap → `partial`.

## How to run

Invoke via **rr-builder** or load this skill directly when test flags are set.

| Selector | Values | Default |
|----------|--------|---------|
| `--scope` | `repo`, `diff`, `uncommitted`, `paths:<csv>` | `diff` |
| `--target` | `frontend`, `backend`, `devops`, `scripts`, `auto` | `auto` |
| `--output` | `md`, `text`, `json`, `report` (alias `md`) | `md` |
| `--max-epochs` | integer | `3` |

## Common flows

```
rr-builder --init
rr-builder --assess --scope diff
rr-builder --complete-missing-tests --scope diff --max-epochs 3
rr-builder --diagnose-flaky --scope paths:tests/foo/BarTest.java
```

## Language refs

Load on demand when stack is identified: [java-test.md](refs/java-test.md), [python-test.md](refs/python-test.md), [react-test.md](refs/react-test.md), [vue-test.md](refs/vue-test.md), [playwright.md](refs/playwright.md).

## Further reading

| Topic | Owner |
|-------|-------|
| Routing and phase chains | [SKILL.md](SKILL.md) |
| Flag parsing | [refs/input-resolution.md](refs/input-resolution.md) |
| Test pyramid | [refs/test-types.md](refs/test-types.md) |
| Verdict heuristics | [refs/shared-heuristics.md](refs/shared-heuristics.md) |
