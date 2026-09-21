# PR / MR title and description

**When:** Creating or updating a GitHub pull request or GitLab merge request. Forge-specific `gh` / `glab` flags live in the nested forge skill.

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

<What problem this solves, what changed and why, for reviewers.>

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

### Summary readability (required)

`## Summary` is for reviewers scanning the PR. Structure beats density:

- **Short lead** — first sentence names the gap or problem.
- **One idea per sentence** — prefer periods; avoid semicolon / em-dash glue that packs multiple claims.
- **Given–new** — known context first, then what this PR changes.
- **No stacked walls** — do not crush problem + solution + edge cases into one paragraph with "while / then / and".
- **Short-circuit** — a Summary that is already ≤3 short sentences and meets this bar needs no further rewrite.

Headings below `---` follow [Keep a Changelog](https://keepachangelog.com/): **Added**, **Changed**, **Fixed**, **Removed**, **Deprecated**, **Security**. Omit empty sections.

| Content | Above `---` | Below `---` |
|--------|-------------|-------------|
| Motivation, implementation, issue links, `Closes #N` | Yes | |
| User-visible API/CLI/behaviour | | Yes |
| Internal refactor, tests, CI-only | Optional | No |

Revisit the below-the-fold section after pushes that change user-visible behaviour. If there are no user-facing notes, omit the `---` block.

### Apply

- GitHub: `gh pr create` / `gh pr edit` with the body file.
- GitLab: `glab mr create` / `glab mr update -d`.

### `--draft` disk gate (parent ship)

When the invoke includes `--draft` (or prose asks to draft title/description first):

1. Write **`.ai/ci/pr-mr-title.txt`** (title only, one line) and **`.ai/ci/pr-mr-body.md`** (full description per sections above).
2. Report both paths. AskQuestion (or prose): **Ship** | **Keep draft only** | **I'll edit**.
3. **Keep draft only** → stop; leave files.
4. **I'll edit** → do not rewrite the files; after the user continues, **re-read** both paths and use that content (user edition wins). AskQuestion again.
5. **Ship** → nested forge upsert uses the current disk title/body. Forge create always includes `gh`/`glab` `--draft` (and `--base` / `--target-branch` from preflight); skill `--draft` is only this disk gate.

Without `--draft`, authoring may still write a body file for CLI `--body-file`. The parent step **title** still runs the **Summary readability gate** before forge create/edit (humanize or AskQuestion when dense).
