# Review parameters (canonical)

**Audience:** **rr-review** via **rr-builder**. Parse flags into this block before running review steps.

## Invoke context

| Context | How flags arrive |
|---------|------------------|
| **Handoff** | Parent `--review` plus nested `--code|--test|--security|--all|--fix|--ci|--scope|paths` |
| **Orchestrate (auto review stage)** | Builder **forces** `--fix --all` (report-only is not available on auto; use explicit `--review` without `--fix`) |

Top-level `--code` / `--test` / `--all` / `--fix` / `--ci` **without** `--review` are **not** valid builder routers (breaking — no compat aliases). Use `--review …` or `--auto`.

## Grammar

```
# Under rr-builder --review:
[--code] [--test] [--security] [--all] [--fix | --ci] [--scope MR|PR|all|full] [paths…]
```

## Lanes

| Flag | Param |
|------|-------|
| `--code` | `lanes: [code]` |
| `--test` | `lanes: [test]` |
| `--security` | `lanes: [security]` |
| `--all` | `lanes: [code, test, security]` |

**Default (no lane flags):** `--all`. **`--all` wins** over individual lane flags.

## Outcome

| Flag | Param |
|------|-------|
| (none) | `outcome: report` |
| `--fix` | `outcome: fix` |
| `--ci` | `outcome: ci` |
| Auto review stage | `outcome: fix` + `lanes: [code, test, security]` (forced) |

**`--fix` and `--ci` are incompatible** → stop: `incompatible flags: --fix and --ci`.

Security + `--fix`: assess only (no security apply).

## Scope

| Flag | Param |
|------|-------|
| `--scope MR` / `--scope PR` | `scope: MR` |
| `--scope all` / `--scope full` | `scope: all` |

**Default:** `scope: MR`.

**MR recipe (report/fix):** `git merge-base HEAD '@{upstream}'`; on failure `origin/main` or `origin/master`; `git diff --name-only "$MERGE_BASE"..HEAD`. Positional paths narrow further.

**`--ci` scope:** Only `--scope MR` or `--scope PR`. Full-repo `--ci` → stop: `ci requires MR scope`. Use **rr-ci** preflight for diff refs and `READ_REF`.

## Parsed block

```yaml
lanes: [code, test, security]
outcome: report | fix | ci
scope: MR | all
paths: []
```

## Optional tuning (strip before parse)

| Token | Meaning |
|-------|---------|
| `inner_max=<n>` | Code fix inner loops (default 5) |
| `--max-epochs <n>` | Test fix outer loops (default 3) |
