# s-test-endless input resolution

**Audience:** Parent **rr-builder** when `lane: add_endless_test`. Normalize flags into `payload.endless_test`.

## Flags (from parent `--add-endless-test`)

| Flag | Field | Default |
|------|-------|---------|
| `--max-epochs N` | `max_epochs` | **5** |
| `--max-parallel N` | `max_parallel` | `null` (unlimited) |
| `--start=fresh\|plan\|execute` | `start` | probe artifacts (see below) |
| `REVIEW_DIR=<repo-relative>` | `review_dir` | `.ai/review/<runId>/` (minted) |
| repo-relative paths | `scope.paths` | entire codebase |

## Scope

```yaml
scope:
  kind: repo | paths
  paths: []   # when kind=paths
```

- Path-only arguments → `kind: paths`, sorted deduped list.
- No paths → `kind: repo` (entire codebase).
- Conflicting scope text vs paths → AskQuestion once.

## Start probe (when `--start` omitted)

1. Mint or reuse **`REVIEW_DIR`** under `.ai/review/` (explicit **`REVIEW_DIR`** override wins when valid).
2. **Glob** `REVIEW_DIR/test/assess/tra-*.md` and `REVIEW_DIR/plans/trp-*.md`.
3. If any exist → AskQuestion once: **Fresh** / **Plan** / **Execute**.
4. If none → **`fresh`**.

Passing **`--start=`** skips the question.

## Validation

| Condition | Result |
|-----------|--------|
| Non-positive `--max-epochs` or `--max-parallel` | **Stopped:** `policy` |
| Invalid `--start` value | **Stopped:** `policy` |
| Non-existent path in scope | **Stopped:** `policy` |
| `REVIEW_DIR` override: dir missing, or `plans/` (and `test/assess/` when start≠fresh) absent | **Stopped:** `policy` |
| `--add-endless-test` + another lane flag | Parent stops: one lane only |

## Output block

```yaml
endless_test:
  max_epochs: 5
  max_parallel: null
  start: fresh | plan | execute
  scope:
    kind: repo | paths
    paths: []
```

Parent sets `payload.lane: add_endless_test` and ignores `drive` / `scope` orchestrate axes.
