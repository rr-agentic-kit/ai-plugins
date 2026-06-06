# claude-md-schema

**Owner:** `CLAUDE.md` section contract for `--init` output.

Referenced by: [init-mode.md](init-mode.md), init-discovery agent.

## Section name

Fixed header (exact match):

```
## rr-test Project Testing Context
```

## Required fields (markdown body under section)

| Field | Format |
|-------|--------|
| Stack | bullet list: languages, frameworks, test runners |
| Test layout | paths and naming convention |
| Run command | primary test command(s) |
| Philosophy | one paragraph: pyramid, mocking stance, flake policy |
| Open decisions | optional bullets from non-blocking questions |

## Idempotent update behavior

1. If section absent → append to end of `CLAUDE.md`.
2. If section present → replace entire section body until next `##` heading of same or higher level.
3. Preserve all other `CLAUDE.md` content unchanged.
4. Re-run init with same inputs → byte-stable section body (deterministic ordering of bullets).

## `claude_md_patch` shape

From [contracts.md](contracts.md):

```json
{
  "section": "## rr-test Project Testing Context",
  "body": "<markdown fields only, no H2>"
}
```

Orchestrator wraps `body` with section header when writing.
