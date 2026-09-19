# Review brief — source discovery

**Audience:** **rr-review** step 3b. Read-only discovery; no product edits.

## Fixed source order

1. **Open PR/MR title + description** — description is the ticket for small adjustments.
2. **Linked issue** — GitHub/GitLab issue, Jira, Linear, etc. when key/link exists in PR/MR, branch name, or commit messages.
3. **In-repo docs** — README, ARCHITECTURE, ADR, catalog usage; rank by relevance to **`FILES`** / diff.
4. **Linked wiki / Confluence** — URLs from sources above only.
5. **Sibling PR/MR / repository links** — named by sources 1–4.

## Retry and degradation

- **Cap:** one corrected retry per external source (issue tracker, wiki, forge API).
- On failure record **`unavailable`**, **`not linked`**, or **`not relevant`** in **`SOURCE STATUS`** — never fabricate.
- Optional external misses **must not** block when PR/MR or local docs suffice.
- External lookups are **read-only** (gh, glab, GitHub/GitLab MCP, Atlassian MCP when available).

## PR/MR resolution

- **`outcome: ci`** — PR/MR required via **rr-ci** preflight; hard stop if unresolved.
- **`scope: MR`** + report/fix — attempt open PR/MR; absent → branch + local docs only.
- **`scope: all`** — fetch external trackers only when **`FILES`** include a reusable/public surface (published package, OpenAPI, shared library). Otherwise local docs only.

## Relevance

- Prefer docs overlapping **`FILES`** or stating the goal.
- Sibling projects are context unless user expanded review target.

## No host lock-in

Do not assume a specific Jira site or internal wiki. Use whatever URL appears in linked sources. Missing MCP → `unavailable`, do not block.
