# Version labels on PR ship (GitHub)

**When:** `s-ci` / `s-gh` **Default PR ship** (`ready_create` or first open after push). Repos that enforce exactly one `v::*` label on PR validation (common in Tark-style monorepos).

## Why

`pr-validation` (and similar) often passes `github.event.pull_request.labels` from the **triggering** `opened` / `synchronize` / `reopened` payload. A label added only **after** `gh pr create` via `gh pr edit --add-label` does not retroactively fix the first run; CI fails until a new `synchronize` (empty commit or push). Apply the label **on create** when the label exists in the repo.

## Pick one label

1. `gh label list --search 'v::' --limit 20` (or read repo `AGENTS.md` / `CONTRIBUTING.md` if present). If **no** `v::patch` / `v::minor` / `v::major` / `v::skip` labels exist → skip this ref (repo has no version-label gate).
2. Choose **exactly one**:
   - **`v::patch`** — default for product / `front/` changes when the feature area used patch before.
   - **`v::minor`** / **`v::major`** — only when user, handoff, or prior PRs in the same area used that level.
   - **`v::skip`** — docs, task-tracking, CI/workflow-only, or other changes that must not bump `front/package.json` version (repo rule).
3. User or handoff named a label → use it. Ambiguous → one AskQuestion among the four (not under `--learn --auto` parent; ship invoke may AskQuestion).

## Apply on create (required)

`ready_create`:

```bash
gh pr create --draft --base <base_branch> --title "…" --body-file … --label <v::…>
```

Use **one** `--label` per allowed name (repeat flag if the repo ever required multiple — version gate repos need exactly one `v::*`).

**Anti-triggers**

- Do **not** create the PR then run only `gh pr edit --add-label` as the first labeling step — first `pr-validation` will still see zero labels.
- Do **not** hand-edit `front/package.json` version for the gate; the label drives release bump on merge in label-gated repos.

## Existing PR (`exists`)

If the open PR has no `v::*` label: `gh pr edit --add-label <v::…>` **and** push a commit (or empty `synchronize`) so embedded `version-labels` jobs on `opened`/`synchronize` see the label. Prefer setting the label before the first push when possible.
