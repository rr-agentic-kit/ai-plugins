# rr-builder

One entry point that classifies build/review work and loads exactly one nested lane skill.

## Why

Agents and humans need a single router for implement, test, security audit, and multi-lane review without preloading every rubric. Done when `payload.lane` is set and the matching nested `SKILL.md` has been **Read**.

## What

Owns flag/plan/NL normalization, lane classification, and on-demand load of `rr-coder`, `rr-tester`, `rr-security-auditor`, or `rr-review`. Review artifacts land under `.ai/review/<runId>/`.

**Out of scope:** cascade planning, forge POST mechanics (except `--ci` handoff), standalone git ops, README tone rewrites.

## Actions

| id | outcome | pick when |
|----|---------|-----------|
| `code` | Production implement/refactor via rr-coder | Implement, refactor, plan with code tasks |
| `test` | Test excellence via rr-tester | Test primary flags / test NL |
| `security` | OWASP audit via rr-security-auditor | Security audit without review flags |
| `review` | Multi-lane assess → report/fix/ci via rr-review | `--code`/`--test`/`--security`/`--all`/`--fix`/`--ci` or "review" |

## When

### Use when

- Implement or refactor production code from a plan or NL
- Test assess/write/fix/migrate/flaky flows
- OWASP / secrets / vulnerability audit
- Multi-lane review (`--code`, `--test`, `--security`, `--all`) with optional `--fix` or `--ci`

### Avoid when

- Cascade planning (exec-summary → PRD) → **rr-planner**
- PR/MR create, pipeline debug, or forge POST alone → **rr-ci**
- Local git only (rebase, worktree, squash) → **rr-git**
- Docs humanization → **rr-humanize**

## Philosophy

- **One nested skill per turn** — never preload all four lanes
- **Host-agnostic** — no employer nouns; parent session + nested skill Read; artifacts under `.ai/review/`
- **Review before ship** — `--ci` runs after findings; do not skip to rr-ci for local-only review

## UX

### Invoke

`rr-builder` with flags, plan path, or clear NL; nested skills are path-loaded only.

### Intake

Normalize via input-resolution into `payload.lane` (+ optional review/test payloads).

### Clarify

Ambiguous lane → AskQuestion once: code | test | security | review-all. Incompatible `--fix` + `--ci` → stop with one-line error.

### Output

Nested skill owns artifacts; review runs write under `.ai/review/<runId>/`.

### Close

Stop at nested done-when. Load **rr-ci** only after review `--ci` or explicit ship request.

## Constraints

- Exactly one lane unless user requested multi-lane review
- Nested skills are not listed in `plugin.json` — parent **Read**s them
- `--fix` and `--ci` are mutually exclusive
- Planning-only docs without implementation intent → redirect to **rr-planner**

## Notes

Nested lane skills intentionally fail context-engineer `static.name.path-match` — they are path-loaded children of `rr-builder`, not top-level `skills/<name>/` entries.

Layout: `refs/` (router), `rr-coder/`, `rr-tester/`, `rr-security-auditor/`, `rr-review/`.
