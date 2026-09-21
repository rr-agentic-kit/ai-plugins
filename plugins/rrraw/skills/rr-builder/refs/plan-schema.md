# Plan-stage output schema

**Audience:** `rr-builder` orchestrate **plan** stage. **No** application source edits.

**Outcome:** Keep task + **build** context small — one step plan per file so build does not load every step’s plan.

## Persist path (canonical)

Write the six required sections to:

`{artifact_root}/{NNNN}-{step}.plan.md`

Default `artifact_root` = `docs/rr/tasks/{slice_id}/`. When `payload.feature.artifact_root` is set (feature / non_rr), use that root instead — see [slice-pipeline.md](slice-pipeline.md) Artifact root.

| Token | Meaning |
|-------|---------|
| `{NNNN}` | Zero-padded task id (same stem as `{NNNN}.md`) |
| `{step}` | **1-based** Steps list item (`step_index + 1`). Cursor `step_index` on `{NNNN}.md` stays **0-based**. |

After writing the sidecar, add a one-line pointer on that Steps item in `{NNNN}.md` (e.g. `→ plan: \`{NNNN}-{step}.plan.md\``). Do **not** paste the six sections into the task body.

Optional frontmatter on the plan file: `task_id`, `step`, `step_index`, `slice_id`.

## Required sections

| Section | Content |
|---------|---------|
| **Goal of step** | One observable outcome for this step only (prose OK) |
| **Approach** | Mechanism-bearing plan (files/symbols/seams); cite allowlist refs used (prose OK) |
| **Risks** | Residual risks / unknowns that could block build (prose OK) |
| **Verify hooks** | **Markdown checklist only** — each hook is `- [ ] …` (commands, assertions, AC ids). Not free-prose bullets. See checkbox contract below |
| **Non-goals** | Explicit exclusions for this step (prose OK) |
| **Ship** | Mid-slice / task ship intent — see table below (required; use `ship_after: never` when the step is **not shippable**) |

### Verify hooks (checkbox contract)

**Verify hooks** is the markable set for **step-validate**. Goal / Approach / Risks / Non-goals stay prose; only Verify is checkboxes.

```markdown
## Verify hooks

- [ ] `pytest tests/foo -q` exits 0
- [ ] AC-3.1: create returns 201 with body id
```

| Rule | Detail |
|------|--------|
| Shape | Each item `- [ ]` (unchecked) or `- [x]` (checked). No bare `-` bullets in this section |
| Who marks | **step-validate** flips matching items to `- [x]` on that item’s **PASS**; FAIL leaves `- [ ]` and records FAIL in the validate report ([task-validate.md](task-validate.md) — report is SoT for FAIL evidence) |
| Empty | At least one checkbox required; empty Verify section = plan incomplete |

### Ship (required)

Record after feature-branch ensure. Do **not** invent a second branch naming scheme — `branch` is the settled HEAD / `feat/{NNNN}-{step}-{short-desc}` from [feature-branch.md](feature-branch.md).

| Field | Values | Meaning |
|-------|--------|---------|
| `branch` | Exact branch name string | Feature branch this step builds on (and ships on when shippable) |
| `ship_after` | `step_validate` \| `task_validate` \| `never` | **Shippable** (`step_validate` / `task_validate`): forge open via **ship** before that validate can PASS. **`never`:** non-shippable — skip ship stage and Forge/PR gate; still run Goal/Verify |
| `base` | `default` \| `prior_open_pr` | PR/MR base: default branch, or tip of latest **still-open** PR in the same `pr_group` ship chain (ignored when `never`) |

**Ship-intent review (plan stage):** `never` is valid when this step will not open a PR. If Goal/Approach/pr_group clearly imply a forge open this step, AskQuestion once: keep `never` \| set `step_validate` or `task_validate` \| abort — do not silently coerce.

## Done-when

0. Feature branch settled per [feature-branch.md](feature-branch.md) (**before** writing the sidecar).
1. Sidecar `{NNNN}-{step}.plan.md` exists at the path above.
2. All **six** sections present and non-empty (Ship may set `ship_after: never`); assessment is enough for **build** to start without inventing scope.
3. `{NNNN}.md` Steps item has the pointer only (no inlined plan body).
4. **No** application source edits this stage (git branch create/checkout for the step is allowed — not application source).
5. Then set `step_plan_done: true` on `{NNNN}.md` (see [slice-pipeline.md](slice-pipeline.md) cursor persistence).

**Probe:** Do not set `step_plan_done: true` from prose inside `{NNNN}.md` alone — the sidecar must exist with the required sections **and** the feature-branch gate must have passed.

## Anti-patterns

- Dumping the six plan sections into `{NNNN}.md` body or an adjacent `### Plan` block (bloated task context)
- Pasting full language matrices or implement Procedures into the plan body
- Editing application source “to explore”
- Omitting **Verify hooks** or writing them as free prose instead of `- [ ]` checkboxes (pushes invent into build; breaks step-validate marking)
- Using 0-based `{step}` in the filename (filename step is always 1-based)
- Writing the plan (or setting `step_plan_done`) while still on `main`/`master` without creating `feat/{NNNN}-{step}-{short-desc}`
- Inventing non-conforming branch names (`feat/<prose>`, slice-only prefixes)
- Omitting **Ship** (or leaving `branch` / `ship_after` / `base` blank)
- Setting `Ship.branch` to something other than the settled feature-branch name
- Using `ship_after: never` for a step that is intended to open a PR this step (wrong non-shippable label)
- Requiring an open PR when `ship_after: never` was confirmed (inventing a forge gate for non-shippable work)
