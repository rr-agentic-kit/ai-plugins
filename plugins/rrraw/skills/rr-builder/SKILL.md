---
name: rr-builder
description: Router for implement, test, security audit, and multi-lane review. Resolves flags or plan input, then Read exactly one nested skill (rr-coder, rr-tester, rr-security-auditor, rr-review). Use for production code, tests, OWASP audit, or --code/--test/--security review — not cascade planning (rr-planner) or PR/CI ship (rr-ci).
---

# rr-builder

**Human overview:** [README.md](README.md)

## Purpose

Given a plan (`docs/plans/`), flags, or natural language, **classify** the work lane and **`Read` only the matching nested `SKILL.md`**. Do not load every nested skill on one prompt. Artifacts for review live under **`.rr-builder/<runId>/`**, not `.ai/review/`.

## When to use

- Implement or refactor production code
- Test assess/write/fix/migrate/flaky flows (former `rr-test` flags)
- OWASP / secrets / vulnerability audit
- Multi-lane review (`--code`, `--test`, `--security`, `--all`) with optional `--fix` or `--ci`

## When not to use

| Need | Use instead |
|------|-------------|
| Cascade planning (exec-summary → PRD) | **rr-planner** |
| PR/MR create, pipeline debug, inline POST mechanics | **rr-ci** (after review `--ci` handoff) |
| Local git only (rebase, worktree, squash) | **rr-git** |
| Docs humanization | **rr-humanize** |

See [refs/anti-overlap.md](refs/anti-overlap.md).

## Procedure

TodoWrite `merge: false` with ids `resolve`, `classify`, `load`, `execute` when routing spans 3+ steps; omit for a single unambiguous nested skill.

1. **resolve** — Load [refs/input-resolution.md](refs/input-resolution.md). Normalize flags, plan path, or NL into `payload.lane` and optional `payload.nested_flags`. Done: payload emitted or one AskQuestion.
2. **classify** — If `payload.lane` is ambiguous, AskQuestion once: code | test | security | review-all. Done: exactly one lane.
3. **load** — **`Read`** the nested skill from [refs/routing.md](refs/routing.md). Do not preload other nested skills.
4. **execute** — Follow the nested skill until its done-when. If outcome is review `--ci`, after findings **`Read`** `skills/rr-ci/SKILL.md` for forge POST. Stop; do not continue into rr-ci unless `--ci` or user asked to ship.

## Nested skills (path-loaded only)

| Lane | Path | Listed in plugin.json |
|------|------|------------------------|
| Code | [rr-coder/SKILL.md](rr-coder/SKILL.md) | no |
| Test | [rr-tester/SKILL.md](rr-tester/SKILL.md) | no |
| Security | [rr-security-auditor/SKILL.md](rr-security-auditor/SKILL.md) | no |
| Review hub | [rr-review/SKILL.md](rr-review/SKILL.md) | no |

Nested skills set `disable-model-invocation: true` and `user-invocable: false`.

## Shared refs

| Ref | When |
|-----|------|
| [refs/input-resolution.md](refs/input-resolution.md) | Every invocation |
| [refs/routing.md](refs/routing.md) | After resolve |
| [refs/anti-overlap.md](refs/anti-overlap.md) | Boundary disputes |
