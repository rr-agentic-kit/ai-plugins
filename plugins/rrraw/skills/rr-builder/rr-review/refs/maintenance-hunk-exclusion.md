# Maintenance-hunk exclusion (heuristic)

**Audience:** Code lane assess; **rr-review** Challenge; inline POST Step 2c via **rr-ci**.

**Purpose:** Drop rules for project-local maintenance hunks and unmapped PR-process heuristics — **no row** when matched.

## Drop rules (deterministic)

Apply in order; **first match → drop**.

| # | Signal | Action |
|---|--------|--------|
| 1 | Changed hunk is **only** `.gitignore` lines for **local/build artifacts** — `node_modules/`, `dist/`, `target/`, `__pycache__/`, `*.log`, IDE caches | **Drop** |
| 2 | Commit subject matches `^chore: [Aa]pply project configuration$` touching `.gitignore` on reviewed paths | **Drop** for those hunks |
| 3 | Finding cites **PR-process heuristics** without literal **`CPNNN` Fail-if** — "orthogonal change," "split PR," "unrelated to feature" | **Drop** |

**Do not invent `CPNNN`** for commit hygiene.

## Security carve-out

Missing secret exclusions in `.gitignore` (`.env`, keys): coding lane **do not flag**; **rr-security-auditor** may flag per `secure.principles.md`.

## Disposition (Challenge)

`drop (FP)`; Reason `maintenance-hunk exclusion`. Sweep every row including **Suggestion** before `--ci` POST.
