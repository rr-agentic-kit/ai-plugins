# PR / MR title and description

**When:** Creating or updating a GitHub pull request or GitLab merge request. Forge-specific create/edit flags live in the active forge skill.

## Title

Prefer an **outcome** phrase, not a dump of commit subjects.

```
{TICKET}: {main goal}
```

or, when no ticket applies:

```
{main goal}
```

- **`TICKET`:** Use a tracker key **only if** it is already on the branch name, an existing PR/MR, or the user supplied it. Never invent a key.
- If recent titles in the repo use `{KEY}:` prefixes and this branch has none, **ask once**. If the repo uses outcome-only titles, do not ask.
- After the optional colon: one concise outcome, not `fix bug` or `updates`.

### Examples

- `PAY-12: Reject expired webhooks without retrying forever`
- `Add timeout to checkout session create`

## Description (reviewers + release notes)

Use the same two-part structure for GitHub and GitLab so a later release job can parse below the fold.

```markdown
## Summary

<Help reviewers understand what they are reviewing — need, outcome, and why these choices; 3–6 short sentences.>

Closes #N

---

## Added
- <New capability>

## Changed
- <Changed behaviour>

## Fixed
- <Bug fix>

## Removed
- <Removed capability>
```

### Summary (reviewers) — content contract

**Goal:** a reviewer who has not read the ticket or plan can open the PR and know **what they are reviewing** — the problem, the intended effect, and the approach worth scrutinizing. Not a diff narration or plan paste. Write **3–6 short sentences** in plain English.

**Include:**

1. **Need** — gap or goal from the task/ticket (given–new lead): what problem or request this addresses.
2. **Outcome** — what changes after merge (user/system behaviour) so reviewers know what to validate, not a file inventory.
3. **Why these choices** — reasoning from the plan (tradeoff or rejected alternative when non-obvious) so reviewers know where to push back. One sentence is enough when the choice is obvious.

**Optional last beat:** only when material — risk, migration, or "watch this in review" in one plain sentence. No new heading.

**Exclude:**

- Diff narration ("added X.py, renamed Y, updated tests…")
- Symbol / API / path dumps (those live in the code)
- Pasting plan ADRs or task checklists wholesale
- Stacked walls of problem + solution + edge cases in one paragraph

**Bad vs good:**

- Bad: `Adds ci_url.py and updates github_backend to parse host from run URLs; tests cover GitHub and GitLab.`
- Good: `Reviewers were jumping between forge CLIs to open a failed run. This PR gives one URL helper so debug-pipeline can deep-link from either host. We kept parsing forge-agnostic so s-ci does not fork on URL shape.`

Headings below `---` follow [Keep a Changelog](https://keepachangelog.com/): **Added**, **Changed**, **Fixed**, **Removed**, **Deprecated**, **Security**. Omit empty sections.

| Content | Above `---` | Below `---` |
|--------|-------------|-------------|
| Motivation, choice rationale, issue links, `Closes #N` | Yes | |
| User-visible API/CLI/behaviour | | Yes |
| Internal refactor, tests, CI-only | Optional | No |

Revisit the below-the-fold section after pushes that change user-visible behaviour. If there are no user-facing notes, omit the `---` block.

### Summary humanize gate (required)

Before forge create/edit, run the Summary through **s-humanize** — mandatory, not optional when dense.

1. **Draft facts** from task + plan + diff (meaning lock — no invented tickets/metrics).
2. Load [`skills/s-humanize/SKILL.md`](../../skills/s-humanize/SKILL.md):
   - first body → **generate** (`refs/generate.md`)
   - update/edit existing body → **rewrite** (`refs/rewrite.md`)
   - always apply `refs/readability.md`
3. **CLI budget:** generate ≤1 `scan`; rewrite ≤2 (`scan`, optional `apply-safe`).
4. **Claim check:** every Summary sentence traces to task/plan/diff; changelog bullets stay factual and out of lexicon wipe.
5. If still dense / AI-tell heavy after one pass → AskQuestion before forge create/edit.

Defaults: `active` + `plain` (same as cascade prose).

### Apply

Forge upsert uses the active skill **Default PR ship** or **Default MR ship** row with title + body file from disk or context. Body must pass the **Summary humanize gate** above before ship.

### `--draft` disk gate (ship routes)

When the invoke includes `--draft` (or prose asks to draft title/description first):

1. Run the **Summary humanize gate**; then write **`.ai/ci/pr-mr-title.txt`** (title only, one line) and **`.ai/ci/pr-mr-body.md`** (full description per sections above).
2. Report both paths. AskQuestion (or prose): **Ship** | **Keep draft only** | **I'll edit**.
3. **Keep draft only** → stop; leave files.
4. **I'll edit** → do not rewrite the files; after the user continues, **re-read** both paths and use that content (user edition wins). AskQuestion again.
5. **Ship** → forge upsert uses the current disk title/body. Forge create always includes forge `--draft` (and `--base` / `--target-branch` from preflight); skill `--draft` is only this disk gate.

Without `--draft`, authoring may still write a body file for CLI `--body-file`. The ship step still runs the **Summary humanize gate** before forge create/edit.
