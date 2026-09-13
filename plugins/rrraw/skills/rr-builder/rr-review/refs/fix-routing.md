# Fix routing (hub handoff)

**Audience:** **rr-review** step 8 when **`outcome: fix`**.

## Inline execution

Parent session applies fixes.

| `lanes` includes | After assess + Challenge | **Read** next |
|------------------|--------------------------|---------------|
| `code` | yes | **rr-coder** — apply CP findings inline; re-read principles as needed |
| `test` | yes | **rr-tester** — use `agents/test/*` Task agents for write/fix when plan requires |
| `security` | — | report/ci only — no fix |

Multi-lane `--fix`: typically code then test unless user requests test-only.

## Plan artifact

When fix scope is large, write **`REVIEW_DIR/fixing-plan.md`** (see [artifacts.md](artifacts.md)).

```markdown
# Fixing plan

| Step | Lane | Action | Status |
|------|------|--------|--------|
| 1 | code | <concrete change> | - [ ] |
| 2 | test | <concrete change> | - [ ] |
```

Checkbox states only: `- [ ]`, `- [executed]`, `- [verified]`.

## Worktrees

Destructive or parallel fix work: **`Read`** `skills/rr-git/refs/worktree-lifecycle.md` and `skills/rr-git/refs/safety.md`.

## `outcome: ci`

Not fix routing — **`Read`** `skills/rr-ci/SKILL.md` after Challenge for inline POST.
