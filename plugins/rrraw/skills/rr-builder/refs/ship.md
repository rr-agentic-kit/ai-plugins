# Ship stage (planned mid-slice / task ship)

**Audience:** `rr-builder` orchestrate **ship** when the step plan’s **Ship** section is shippable and forge open is still needed. Forge create stays **rr-ci** — this stage resolves branch/base and hands off.

## When

| Plan `ship_after` | Trigger |
|-------------------|---------|
| `never` | Skip — do not enter **ship** (non-shippable; validate has no Forge/PR gate) |
| `step_validate` | When step-validate **Forge / PR** FAILs (or Goal/Verify green but no open PR yet) and `step_ship_done` ≠ `true` — **before** step-validate can PASS. After ship done-when → re-enter **step-validate** (do not advance `step_index`). Do **not** wait for step-validate PASS to ship. |
| `task_validate` | When task-validate **Forge / PR** FAILs for this Ship block (or equivalent forge miss) and task-scoped ship not done — **before** task-validate can PASS. After ship → re-enter **task-validate**. |

## Inputs

| Input | Source |
|-------|--------|
| Ship block | Current `{NNNN}-{step}.plan.md` **Ship** section ([plan-schema.md](plan-schema.md)) |
| Branch name | `Ship.branch` (must match settled feature-branch / HEAD — [feature-branch.md](feature-branch.md)) |
| Base policy | `Ship.base`: `default` \| `prior_open_pr` |
| `pr_group` | Active task frontmatter |

## Procedure

1. **Confirm branch** — `git branch --show-current` equals `Ship.branch` (or engineer Stay recorded in plan). Else stop: align branch before ship.
2. **Resolve base**
   - `default` → repo default branch (`main`/`master`).
   - `prior_open_pr` → tip of the **latest open** PR/MR whose head branch is in the same `pr_group` ship chain (prior step/task that already shipped and is still unmerged). If none open → fall back to `default`. **Probe:** list candidate open PRs; AskQuestion if >1 ambiguous tip (Delivery channels: text fallback OK).
3. **Persist** on `task-summary.md` frontmatter: `active_ship_branch`, `ship_base_branch` (resolved values).
4. **Handoff** — `Read` `skills/rr-ci/SKILL.md`; pass branch = `active_ship_branch`, base = `ship_base_branch`. Include dirty task sidecars under `artifact_root` / `docs/rr/tasks/` that belong to this step **or** prior orphaned validate/cursor docs marked carry-to-next ([task-validate.md](task-validate.md) Forge landing). Stop at rr-ci PR/MR done-when. **Do not** invent gh/glab flags here.
5. Set `step_ship_done: true` on `{NNNN}.md` (for `ship_after: step_validate`) or clear pending task-level ship marker after task ship.
6. **Return** — re-enter the matching validate stage (`step_validate` or `task_validate`); do not advance past validate on ship alone.

### Post-PASS landing (shippable)

When re-validate reaches overall **PASS** and an open PR still exists for the tip, hand off **rr-ci** again to push the validate report(s) + Verify checkbox flips + cursor frontmatter **before** advancing or stopping. Full tip resolution, final-step "both sidecars" rule, and carry-to-next SoT: [task-validate.md](task-validate.md) **Forge landing** — do not restate it here. After push → **pr-validate** ([pr-validate.md](pr-validate.md)); skip when carry-to-next / `never`.

### Isolation-cell exception (`auto` × `task` \| `slice`)

Under **Isolated step run** ([slice-pipeline.md](slice-pipeline.md)): **ship stays in parent**. When a step executor returns `needs_ship`, parent runs this stage → **rr-ci**, re-runs step-validate **inline** (assessment only), **commits** cursor/validate sidecars, then runs the dirty-tree gate before spawning the next step Task. Dirty-porcelain rules SoT: [task-validate.md](task-validate.md) Isolation-cell exception (carry-to-next does not waive the gate in this cell).

## Done-when

- Base resolved (default or prior open tip).
- Cursor ship fields persisted.
- **rr-ci** handoff completed or engineer declined (manual) / hard-stopped.
- `step_ship_done: true` when this was a step-scoped ship.
- Validate stage re-entered (or engineer declined continue).

## Stop / anti-trigger

- Do **not** open PR/MR inside builder without **rr-ci**.
- Do **not** invent branch names here — naming SoT is [feature-branch.md](feature-branch.md); Ship only records them.
- Do **not** ship when `ship_after: never`.
- Do **not** treat slice **delivered** as the only ship path — mid-slice ship is first-class when planned.
- Do **not** require validate PASS before ship when the forge gate is what blocks PASS.

## Non-goals

- Pipeline debug, review POST, deploy — **rr-ci** after handoff as needed.
- Squash/rebase onto base — **rr-git** if required before ship.
