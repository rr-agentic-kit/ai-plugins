# Project always-on section template

Use for **project** scope **design** and **review**. Default scope = project. Do **not** duplicate user-global comm/role unless user insists.

**Fill by leverage, not by checklist.** Omit sections with nothing that passes the 90% bar. Prefer pointers to README / CONTRIBUTING over absorbing them.

| # | Section | Keep when |
|---|---------|-----------|
| 1 | **Purpose** | One short paragraph improves orientation in most chats |
| 2 | **Hard rules** | Violations are costly / frequent without them |
| 3 | **Stack** | Languages, frameworks, versions agents need every session |
| 4 | **Commands** | Essential copy-paste commands (not full quality matrix) |
| 5 | **Where to look** | Short table → authoritative docs / plugin contracts |
| 6 | **Conventions** | Naming/patterns that prevent recurring mistakes |
| 7 | **Safety** | Repo-specific secrets paths, forbidden ops (if not covered elsewhere) |
| 8 | **Non-goals** | What agents must not treat as in-scope for this file |
| 9 | **Situational packs** | **Only if packs exist** — when-to-Read + backticked `.agents/{group}.md` |

## Situational packs

Derive names via `situation-groups.md`. Zero packs is valid. Never `@`-import packs.

## Docs boundary

Point to user-global for tone/role: “See `~/.claude/CLAUDE.md` Communication / Role.”  
Full contributor matrices → `CONTRIBUTING.md`. Product narrative → `README.md`.

## Claude pointer

Write thin `CLAUDE.md` with `@AGENTS.md` (+ rare Claude-only bullets). Always-on body lives in `AGENTS.md`.
