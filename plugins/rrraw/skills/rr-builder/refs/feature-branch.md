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

**Feature-mode Stay:** when `mode: feature` and HEAD is already `feat/{NNNN}-*` from [feature.md](feature.md) task-branch ensure, prefer **Stay** (do not force rename to the step-suffixed `TARGET` unless the engineer asks). **Does not** override **auto tip-chain** below (orchestrate `drive: auto` step→step targets).

## Ensure procedure

1. Resolve repo root; `git branch --show-current` → `HEAD_BRANCH`. Read `payload.drive` from the run (orchestrate / feature).
2. Build `TARGET=feat/{NNNN}-{step}-{short-desc}` from the step Goal (kebab).
3. Branch on `HEAD_BRANCH` — **first match wins**:

| Predicate | Action |
|-----------|--------|
| `HEAD_BRANCH` is `main` or `master` | `git checkout -b TARGET` (dirty tree OK — **must** carry uncommitted work onto the new branch, including orphaned `docs/rr/tasks/**` / `artifact_root` validate reports, Verify checkbox flips, and cursor frontmatter from a prior step’s carry-to-next — [task-validate.md](task-validate.md) Forge landing). Done when HEAD is `TARGET`. |
| `HEAD_BRANCH` equals `TARGET` | No-op. Done. |
| `HEAD_BRANCH` matches `feat/{NNNN}-{step}-*` but ≠ `TARGET` | AskQuestion: rename to `TARGET` \| keep current \| abort plan. (Same-step rename — still Ask even under `drive: auto`.) |
| **`drive: auto`** and `HEAD_BRANCH` matches `feat/{NNNN}-*` (same `{NNNN}`) and does **not** match `feat/{NNNN}-{step}-*` (prior / other-step tip) and ≠ `TARGET` | **Auto tip-chain:** `git checkout -b TARGET` from current HEAD (dirty tree OK — same carry-to-next rule as main/master). **Do not** AskQuestion. Done when HEAD is `TARGET`. Record chain in plan Risks if useful. |
| Any other branch | AskQuestion (see **Probe**). **Stop-rule:** do not invent a silent checkout/create under `drive: manual` or off-task branches. |

4. Optional: **Read** `skills/rr-git/refs/safety.md` only if a rename/`-D` path is chosen — do not run squash/worktree/cleanup here.

**Anti-trigger / stop-rule:** Under `drive: auto`, never AskQuestion the Probe when HEAD is already `feat/{NNNN}-*` for this task and `TARGET` is the next (or different) step suffix — tip-chain is mandatory. Do **not** stall auto×step / auto×task / auto×slice on “stay \| new from base \| rename”.

## Probe (not on main/master; not after auto tip-chain)

AskQuestion options (Delivery channels: text fallback OK) — **skip entirely** when the auto tip-chain row matched:

1. **Stay** — continue plan on current branch (record branch name in plan Risks).
2. **New from base** — create `TARGET` from `main`/`master` (confirm base; **must** stash/carry uncommitted task sidecars — same carry-to-next rule as the main/master row).
3. **Rename to convention** — rename current branch to `TARGET` (confirm; safety.md if destructive).
4. **Abort plan** — stop; do not write plan sidecar or set `step_plan_done`.

## Done-when

- HEAD is settled per table/probe **and** either matches `TARGET` or engineer explicitly chose **Stay** (manual / non-chain only).
- Then proceed to write the plan sidecar ([plan-schema.md](plan-schema.md)). After auto tip-chain, default `Ship.base` per [plan-schema.md](plan-schema.md).

## Non-goals

- Worktree-per-step (optional via **rr-git**, not required here).
- Squash, merge, force-push, prune — **rr-git** / **rr-ci**.
- Opening PR/MR — **rr-ci** via orchestrate **ship** ([ship.md](ship.md)); plan **Ship.branch** only **records** this TARGET for that handoff.
