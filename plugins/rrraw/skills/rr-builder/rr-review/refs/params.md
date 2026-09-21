# Review parameters (canonical)

**Audience:** **rr-review** via **rr-builder**. Parse flags into this block before running review steps.

## Invoke context

| Context | How flags arrive |
|---------|------------------|
| **Handoff** | Parent `--review` plus nested `--code|--test|--security|--all|--fix|--ci|--endless|--scope|paths` |
| **Orchestrate (auto review stage)** | Builder **forces** `--fix --all --endless` (report-only is not available on auto; use explicit `--review` without `--fix`) |

Top-level `--code` / `--test` / `--all` / `--fix` / `--ci` **without** `--review` are **not** valid builder routers (breaking — no compat aliases). Use `--review …` or orchestrate.

## Grammar

```
# Under rr-builder --review:
[--code] [--test] [--security] [--all] [--fix | --ci] [--endless] [--max-epochs <n>] [--scope MR|PR|all|full] [paths…]
```

## Lanes

| Flag | Param |
|------|-------|
| `--code` | `lanes: [code]` |
| `--test` | `lanes: [test]` |
| `--security` | `lanes: [security]` |
| `--all` | `lanes: [code, test, security]` |

**Default (no lane flags):** `--all` — including when only `--fix` or report-only (no `--code`/`--test`/`--security`/`--all`) is set; lanes inherit `[code, test, security]`. **`--all` wins** over individual lane flags.

## Outcome

| Flag | Param |
|------|-------|
| (none) | `outcome: report` |
| `--fix` | `outcome: fix` + `endless: true` (forced — loop until clear) |
| `--ci` | `outcome: ci` |
| Auto review stage | `outcome: fix` + `lanes: [code, test, security]` + `endless: true` (forced) |

**`--fix` and `--ci` are incompatible** → stop: `incompatible flags: --fix and --ci`.

Security + `--fix`: assess only (no security apply).

## Endless

| Flag / condition | Param |
|------------------|-------|
| (none) and `outcome: report` | `endless: false` |
| `--endless` | `endless: true` |
| `outcome: fix` (handoff `--fix` **or** auto review) | `endless: true` (**forced** — omit `--endless` still loops) |
| Auto review stage | `endless: true` (forced) |
| `--max-epochs <n>` | `max_epochs: <n>` (default **5** when endless) |

**Incompatibilities:**

| Pair | Action |
|------|--------|
| `--endless` + `--ci` | stop: `incompatible flags: --endless and --ci` |
| `--endless` without `--fix` (handoff) | stop or force `outcome: fix` (which also forces `endless: true`) |

Report-only (`outcome: report`) stays single-shot. Fix mode always endless until clear / warnings / epoch cap — [endless.md](endless.md).

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
endless: false | true
max_epochs: 5
scope: MR | all
paths: []
```

## Optional tuning (strip before parse)

| Token | Meaning |
|-------|---------|
| `inner_max=<n>` | Code fix inner loops (default 5) |
| `--max-epochs <n>` | Endless outer epochs (default **5**); also used historically for test-fix outer loops when not endless (default 3) |
