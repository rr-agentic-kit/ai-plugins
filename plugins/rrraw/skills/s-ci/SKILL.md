---
name: s-ci
description: s-ci — forge router; detect remote and delegate to s-gh or s-glab; --fix, ship, issue, publish, deploy shapes.
disable-model-invocation: true
---

# s-ci

**Human overview:** [README.md](README.md)

**Scripts:** JSON envelope CLI — [scripts/README.md](scripts/README.md); frozen surface [SCRIPTS-SPEC.md](SCRIPTS-SPEC.md).

## Purpose

Forge **router**: classify task shape, detect GitHub vs GitLab (`detect-remote` / `parse-ci-url`), **delegate apply** to **s-gh** | **s-glab** | **s-publish** | **s-deploy**. No forge CLI syntax here. Shared `refs/ci/**` policy is co-loaded by the forge skill — not by this router.

## When to use

- Forge unknown — start here (invoke **s-ci**)
- Same invoke shapes as **s-gh** / **s-glab**: ship routes (`--create-pr` / `--create-mr` / …), `--draft`, `--fix`, `--fix --sonar`, `--pull-dependabot`, issue, CI/review, publish, deploy

## When not to use

- Forge known and GitHub-only → **s-gh** direct; GitLab-only → **s-glab** direct
- Local git only → **s-git**
- General implement/refactor → **rr-builder** (exceptions: Sonar-only under `--fix --sonar`; current-PR review threads per `refs/ci/review-comment-triage.md`)

## Shared policy (SoT index)

Router loads only `refs/ci/task-shapes.md` for classify. Forge skills co-load the rest per task-shape:

| Need | Path |
|------|------|
| Shapes / TodoWrite | `refs/ci/task-shapes.md` |
| PR/MR title/body | `refs/ci/pr-mr-templates.md` |
| Pipeline fix | `refs/ci/fix/pipeline-fix.md` + `refs/ci/fix/pipeline-fix-rules.md` |
| Sonar fix | `refs/ci/sonar-fix.md` |
| Pull Dependabot | `refs/ci/pull-dependabot.md` |
| Review threads | `refs/ci/review-comment-triage.md` |

## Procedure

1. **task-shape** — Classify per `refs/ci/task-shapes.md`. Run/job URL alone → **`--fix`**. Load shape-detail sections only when classify needs more than the shape id. Done: shape recorded.
2. **root** — `REPO_ROOT` via `skills/s-git/refs/repo-root.md`. Load `skills/s-git/refs/safety.md` only when history rewrite / discard possible.
3. **forge** — If invoke has a run/job URL: `rr-ci parse-ci-url <url>` → use `result.forge` / `owner` / `repo` (and ids); do **not** invent URL parse; skip `detect-remote` when `ok`. Else `rr-ci detect-remote`. If `unknown` → AskQuestion (GitHub | GitLab); Prefer AskQuestion; text-mode same options; no stall. **`--pull-dependabot`:** require GitHub.
4. **delegate** — Read matching skill: `skills/s-gh/SKILL.md` | `skills/s-glab/SKILL.md` | `skills/s-publish/SKILL.md` | `skills/s-deploy/SKILL.md`. Pass bound `REPO_ROOT` (+ forge context); forge skill **skips** its root step when `REPO_ROOT` already set. Forge skill owns title/load/execute, `gh`/`glab`, and CLI invoke.

TodoWrite ids: `refs/ci/task-shapes.md`.

Task agents: N/A — this skill does not spawn or inject Task agents.

## Invariants

- Shared policy lives in `refs/ci/**` only — do not restate here.
- Disk sidecars under **`.ai/ci/`** at repo root.
- Nested forge skills are path-loaded; do not wait for @-mention.
