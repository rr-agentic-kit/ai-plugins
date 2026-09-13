# Memory hierarchy

Reference: [Claude Code memory](https://code.claude.com/docs/en/memory).

## Scopes (narrowest wins for conflicts)

| Scope | Always-on SoT | Claude pointer | Loaded when |
|-------|---------------|----------------|-------------|
| **User-global** (opt-in) | User always-on file (often `@`-imported from user `CLAUDE.md`) | `~/.claude/CLAUDE.md` | Every session, all projects |
| **Project** (default) | `./AGENTS.md` | `./CLAUDE.md` → `@AGENTS.md` | Sessions in that repo |
| **Local override** | — | `./.agents/local.md` (gitignored) | Same as project; personal experiments |
| **Situational** | — | `.agents/{group}.md` via backtick + Read trigger | Only when `AGENTS.md` trigger matches |

Default **scope = project**. User-global only when the user explicitly requests it.

## Runtime split

| Runtime | Always-on entry | Shared body |
|---------|-----------------|-------------|
| **Cursor** | `AGENTS.md` | Same file |
| **Claude Code** | `CLAUDE.md` with `@AGENTS.md` | Same `AGENTS.md` |

Optional Claude-only bullets may live under `CLAUDE.md` after the `@` import—keep them rare and high-leverage.

## Load order (conceptual)

1. User-global instructions (if present)
2. Project always-on (`AGENTS.md`, via Cursor load or Claude `@` import)
3. Other approved `@` imports of **always-on** splits only
4. Situational packs — **not** auto-imported; agent Reads when trigger fires

## What belongs where

| User-global | Project always-on | Situational pack | Outside (docs) |
|-------------|-------------------|------------------|----------------|
| Communication, role, language, cross-repo tooling prefs | Hard rules, stack, essential commands, short where-to-look, non-goals | Depth that fails always-on budget but still matters often enough | README, CONTRIBUTING, ADRs, plugin READMEs |
| Security habits you always want | Domain boundaries for *this* codebase | Clustered constraints idle in most chats | Long procedures, narrative product docs |
| Environment quirks (Nix, proxies) | Copy-paste commands agents need every session | — | Full quality matrices |

## `@` vs backtick

| Form | Example | Rule |
|------|---------|------|
| `@` import | `@AGENTS.md` in `CLAUDE.md` | Always-on only; expands at Claude Code launch |
| `@` local | `@.agents/local.md` in `CLAUDE.md` | Sole `.agents/` `@` exception — gitignored personal override |
| Backtick + trigger | “When &lt;situation&gt;, Read `.agents/{derived-group}.md`” | Shared situational packs only; **never** `@` those |

Imports of always-on splits must be **approved by user** before write. Keep `AGENTS.md` scannable. Ensure `.agents/local.md` is in `.gitignore`.

## Anti-patterns

- Project-specific API names in user-global (stale, leaks context)
- Duplicate comm/role in project when user-global already defines them
- Secrets or credentials in any memory file
- `@`-importing shared situational packs (burns tokens every session)
- Committing `.agents/local.md` (must stay gitignored)
- Absorbing CONTRIBUTING into `AGENTS.md` “for completeness”
- Fixed catalog of `.agents/*.md` filenames (derive from this project—see `situation-groups.md`; `local.md` is the reserved personal override name)
