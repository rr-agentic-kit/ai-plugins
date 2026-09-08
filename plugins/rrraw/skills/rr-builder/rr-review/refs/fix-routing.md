# Fix routing (hub handoff)

**Audience:** **rr-review** step 8 when **`outcome: fix`**.

## v1 execution (inline)

Parent session applies fixes — no `_oa-review-fix-agent` in rrraw.

| `lanes` includes | After assess + Challenge | **Read** next |
|------------------|--------------------------|---------------|
| `code` | yes | **rr-coder** — apply CP findings inline; re-read principles as needed |
| `test` | yes | **rr-tester** — use `agents/test/*` Task agents for write/fix when plan requires |
| `security` | — | report/ci only in v1 — no fix |

Multi-lane `--fix`: typically code then test unless user requests test-only.

## Plan artifact

When fix scope is large, write unified plan under `REVIEW_DIR/plans/trp-*.md` with step checkboxes (`- [ ]`, `- [executed]`, `- [verified]`).

## Worktrees

Destructive or parallel fix work: **`Read`** `skills/rr-git/refs/worktree-lifecycle.md` and `skills/rr-git/refs/safety.md`.

## `outcome: ci`

Not fix routing — **`Read`** `skills/rr-ci/SKILL.md` after Challenge for inline POST.
