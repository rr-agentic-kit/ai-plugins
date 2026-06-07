# Memory hierarchy

Reference: [Claude Code memory](https://code.claude.com/docs/en/memory).

## Scopes (narrowest wins for conflicts)

| Scope | Typical path | Loaded when |
|-------|--------------|-------------|
| **User-global** | `~/.claude/CLAUDE.md` | Every session, all projects |
| **Project** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Sessions in that repo |
| **Local override** | `./CLAUDE.local.md` (gitignored) | Same as project; personal experiments |

## Load order (conceptual)

1. User-global instructions
2. Project instructions
3. Imported files via `@path` from either layer

## What belongs where

| User-global | Project |
|-------------|---------|
| Communication, role, language, cross-repo tooling prefs | Stack, architecture, repo conventions, test commands |
| Security habits you always want | Domain boundaries for *this* codebase |
| Environment quirks (Nix, proxies) | Paths, package manager, CI entrypoints |

## Imports

- Use `@relative-or-absolute-path` for long sections (e.g. split comm/role to `~/.claude/communication-role.md`).
- Imports must be **approved by user** before write.
- Keep root `CLAUDE.md` scannable; exhaustive content may live in imports.

## Anti-patterns

- Project-specific API names in user-global (stale, leaks context)
- Duplicate comm/role in project when user-global already defines them
- Secrets or credentials in any memory file
