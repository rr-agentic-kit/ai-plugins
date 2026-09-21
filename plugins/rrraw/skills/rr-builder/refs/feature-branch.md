# Feature branch for task-steps

**Audience:** `rr-builder` orchestrate **plan** stage (before writing the step plan). Naming SoT + ensure procedure.

## Name (SoT)

```
feat/{NNNN}-{step}-{short-desc}
```

| Token | Meaning |
|-------|---------|
| `{NNNN}` | Zero-padded task id (same as `{NNNN}.md` stem) |
| `{step}` | **1-based** Steps list item (`step_index + 1`) |
| `{short-desc}` | Kebab-case from the step’s Goal (≤6 words worth of tokens; no spaces) |

**Anti-trigger:** Do **not** invent alternate shapes (`feat/<prose>`, `feat/<slice>-…`, ticket-only names). Do **not** defer branch create to a human ask after build.

## When to run

At **plan** stage start — before writing `{NNNN}-{step}.plan.md`. Re-check is a no-op when HEAD already matches the convention for this task-step.

**Feature-mode Stay:** when HEAD is already `feat/{NNNN}-*` from [feature.md](feature.md) task-branch ensure, prefer **Stay** (do not force rename to the step-suffixed `TARGET` unless the engineer asks).
## Ensure procedure

1. Resolve repo root; `git branch --show-current` → `HEAD_BRANCH`.
2. Build `TARGET=feat/{NNNN}-{step}-{short-desc}` from the step Goal (kebab).
3. Branch on `HEAD_BRANCH`:

| Predicate | Action |
|-----------|--------|
| `HEAD_BRANCH` is `main` or `master` | `git checkout -b TARGET` (dirty tree OK — carry uncommitted work onto the new branch). Done when HEAD is `TARGET`. |
| `HEAD_BRANCH` equals `TARGET` | No-op. Done. |
| `HEAD_BRANCH` matches `feat/{NNNN}-{step}-*` but ≠ `TARGET` | AskQuestion: rename to `TARGET` \| keep current \| abort plan. |
| Any other branch | AskQuestion (see **Probe**). **Stop-rule:** do not invent a silent checkout/create. |

4. Optional: **Read** `skills/rr-git/refs/safety.md` only if a rename/`-D` path is chosen — do not run squash/worktree/cleanup here.

## Probe (not on main/master)

AskQuestion options (Delivery channels: text fallback OK):

1. **Stay** — continue plan on current branch (record branch name in plan Risks).
2. **New from base** — create `TARGET` from `main`/`master` (confirm base; warn if uncommitted work needs stash/carry).
3. **Rename to convention** — rename current branch to `TARGET` (confirm; safety.md if destructive).
4. **Abort plan** — stop; do not write plan sidecar or set `step_plan_done`.

## Done-when

- HEAD is settled per table/probe **and** either matches `TARGET` or engineer explicitly chose **Stay**.
- Then proceed to write the plan sidecar ([plan-schema.md](plan-schema.md)).

## Non-goals

- Worktree-per-step (optional via **rr-git**, not required here).
- Squash, merge, force-push, prune — **rr-git** / **rr-ci**.
- Opening PR/MR — **rr-ci** via orchestrate **ship** ([ship.md](ship.md)); plan **Ship.branch** only **records** this TARGET for that handoff.
