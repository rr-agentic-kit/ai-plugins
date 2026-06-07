# Parallel agent instruction files

Some repos use instruction files alongside project `CLAUDE.md`:

| File pattern | Typical role |
|--------------|--------------|
| `AGENTS.md` | Repo-wide agent contract (many tools) |
| Path-scoped rules (e.g. `**/rules/*`, tool-specific dirs) | Scoped overrides; discover—do not assume vendor or layout |
| Legacy single-file rules | Note if present; do not auto-merge |

## On project design/review

1. If parallel instruction files exist, compare **Stack**, **Commands**, **Architecture** with project `CLAUDE.md`; report deltas to user.
2. User picks **one** source of truth (memory file vs parallel file)—no auto-merge.
3. Optional project bullet: “Parallel agent instructions: see `AGENTS.md`” (only if user wants a pointer).

## On user-global

Generally **do not** reference a single repo’s `AGENTS.md`. Exception: user names a personal template repo path explicitly.
