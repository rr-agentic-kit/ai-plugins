# Memory hierarchy

Reference: [Claude Code memory](https://code.claude.com/docs/en/memory). User-global multi-harness detail: `user-global-multi-harness.md`.

## Scopes (narrowest wins for conflicts)

| Scope | Always-on SoT | Entry / pointer | Loaded when |
|-------|---------------|-----------------|-------------|
| **User-global** (opt-in) | `~/.agents/AGENTS.md` | Per-harness **adapter** (thin; see multi-harness ref) | Every session, all projects (when that harness loads its adapter) |
| **Project** (default) | `./AGENTS.md` | `./CLAUDE.md` → `@AGENTS.md` (Claude); Cursor loads `AGENTS.md` | Sessions in that repo |
| **Local override** | — | `./.agents/local.md` (gitignored) | Same as project; personal experiments |
| **Situational** | — | `.agents/{group}.md` via backtick + Read trigger | Only when `AGENTS.md` trigger matches |

Default **scope = project**. User-global only when the user explicitly requests it.

## Project vs user-global (do not conflate)

| | **Project** | **User-global** |
|--|-------------|-----------------|
| SoT | `./AGENTS.md` | `~/.agents/AGENTS.md` |
| Shape | Unchanged: `CLAUDE.md` + `AGENTS.md` + optional `.agents/` packs | Shared SoT + optional `*.specific.md` overlays + thin harness adapters |
| Claude entry | `./CLAUDE.md` → `@AGENTS.md` | `~/.claude/CLAUDE.md` → `@~/.agents/AGENTS.md` (+ optional overlay `@`) |
| Other harnesses | N/A (repo files) | Cursor `.mdc` / Codex / Copilot thin Read-forcing stubs — **not** “same shape under `~/.claude/`” |

## Runtime split (project)

| Runtime | Always-on entry | Shared body |
|---------|-----------------|-------------|
| **Cursor** | `AGENTS.md` | Same file |
| **Claude Code** | `CLAUDE.md` with `@AGENTS.md` | Same `AGENTS.md` |

Optional Claude-only bullets may live under project `CLAUDE.md` after the `@` import—keep them rare and high-leverage.

## Runtime split (user-global)

| Runtime | Adapter | Shared body | Overlay |
|---------|---------|-------------|---------|
| **Claude Code** | `~/.claude/CLAUDE.md` (`@` expand) | `~/.agents/AGENTS.md` | `CLAUDE.specific.md` via `@` |
| **Cursor** | `~/.cursor/rules/user-global.mdc` (alwaysApply thin stub) | Same SoT via Read force | `CURSOR.specific.md` via Read force |
| **Codex** | `~/.codex/AGENTS.md` (thin stub; respect `CODEX_HOME`) | Same SoT via Read force | `CODEX.specific.md` via Read force |
| **Copilot** | `~/.copilot/copilot-instructions.md` | Same SoT via Read force | `COPILOT.specific.md` via Read force |

Adapters never duplicate SoT body. Full templates + migration: `user-global-multi-harness.md`.

## Load order (conceptual)

1. User-global instructions (if present)—SoT via harness adapter; then optional harness overlay
2. Project always-on (`AGENTS.md`, via Cursor load or Claude `@` import)
3. Other approved `@` imports of **always-on** splits only
4. Situational packs — **not** auto-imported; agent Reads when trigger fires

## What belongs where

| User-global SoT | Harness overlay (`*.specific.md`) | Project always-on | Situational pack | Outside (docs) |
|-----------------|-----------------------------------|-------------------|------------------|----------------|
| Communication, role, language, cross-repo tooling prefs | Models, Task/subagent policy, harness-native quirks | Hard rules, stack, essential commands, short where-to-look, non-goals | Depth that fails always-on budget but still matters often enough | README, CONTRIBUTING, ADRs, plugin READMEs |
| Security habits you always want | Runtime mode prefs for one harness | Domain boundaries for *this* codebase | Clustered constraints idle in most chats | Long procedures, narrative product docs |
| Environment quirks (Nix, proxies) | — | Copy-paste commands agents need every session | — | Full quality matrices |

## `@` vs backtick vs Read force

| Form | Example | Rule |
|------|---------|------|
| `@` import | `@AGENTS.md` in project `CLAUDE.md`; `@~/.agents/AGENTS.md` in user Claude adapter | Always-on only; expands at Claude Code launch |
| `@` local | `@.agents/local.md` in project `CLAUDE.md` | Sole `.agents/` `@` exception — gitignored personal override |
| Read force (adapter stub) | Cursor `.mdc` / Codex / Copilot: “Read SoT (+ overlay) before substantive work” | When harness has no native `@` home expand; **no** SoT body in the stub |
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
- Treating `~/.claude/` alone as user-global SoT (migrate to `~/.agents/AGENTS.md` + adapters)
- Mirroring SoT body into Cursor `.mdc` or other adapters (thin stub only)
