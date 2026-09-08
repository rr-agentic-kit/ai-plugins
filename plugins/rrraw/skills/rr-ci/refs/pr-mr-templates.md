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
