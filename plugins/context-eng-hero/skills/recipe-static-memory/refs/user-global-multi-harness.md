# User-global multi-harness layout

**Load for:** user-global **design** (mandatory after scope); **review** / **fix** when discovering adapters, overlays, or Claude-only legacy packs.

Shared always-on SoT is `~/.agents/AGENTS.md` (cross-harness; 90% bar unchanged). Project-scope layout is unchanged—see `agents-md-bridge.md`.

## Target shape

```text
~/.agents/AGENTS.md                 # Shared SoT (comm/role/git/security/env/tooling/non-goals)
~/.agents/CLAUDE.specific.md        # Claude-only (optional)
~/.agents/CURSOR.specific.md        # Cursor-only (optional)
~/.agents/CODEX.specific.md         # Codex-only (optional)
~/.agents/COPILOT.specific.md       # Copilot-only (optional)

# Adapters (entry points — thin; never duplicate SoT body)
~/.claude/CLAUDE.md                 # @~/.agents/AGENTS.md + @~/.agents/CLAUDE.specific.md
~/.cursor/rules/user-global.mdc     # alwaysApply thin Read-forcing stub → SoT + CURSOR.specific
~/.codex/AGENTS.md                  # thin Read-forcing stub → SoT + CODEX.specific
~/.copilot/copilot-instructions.md  # thin Read-forcing stub → SoT + COPILOT.specific
```

Respect harness home overrides when present (e.g. `CODEX_HOME` for Codex). First-class harnesses only: Claude Code, Cursor, Codex, Copilot. Other tools: document the adapter pattern in chat; do not invent first-class paths.

## Capability matrix

| Harness | Adapter path | Load mechanism | Overlay |
|---------|--------------|----------------|---------|
| Claude Code | `~/.claude/CLAUDE.md` | Native `@` expand | `CLAUDE.specific.md` via `@` |
| Cursor | `~/.cursor/rules/user-global.mdc` (`alwaysApply: true`) | Thin stub + Read force (no native home `AGENTS.md`) | `CURSOR.specific.md` via Read force |
| Codex | `~/.codex/AGENTS.md` (respect `CODEX_HOME`) | Thin stub + Read force (global is single-file; no `@`) | `CODEX.specific.md` via Read force |
| Copilot | `~/.copilot/copilot-instructions.md` | Thin stub + Read force | `COPILOT.specific.md` via Read force; optional path-specific under `~/.copilot/instructions/` only if justified |

**Why not symlink for Codex/Copilot:** global slot is one file; symlink to SoT drops overlay. Thin stub keeps one SoT + optional overlay without concat sync jobs.

## What belongs where

| Layer | Content |
|-------|---------|
| **Shared SoT** (`~/.agents/AGENTS.md`) | Communication, role, git/security/env, cross-harness tooling triggers, non-goals |
| **`*.specific.md`** | Harness-only: default models, sub-agent/Task spawn policy, harness-native skills/MCP quirks, runtime mode prefs |
| **Adapter** | Include/`@`/Read paths only (+ 2–5 line forcing function). No policy body. |

Anti-patterns: mirroring SoT into `.mdc` or other adapters; putting model/subagent tables in shared SoT; project leaks in any user-global file.

## Overlay inclusion bar

Write `HARNESS.specific.md` only when constraints are **harness-native** and still pass the 90% bar for sessions **in that harness**. Examples that belong in overlay: Cursor Task spawn defaults; Claude-only `@` import quirks; Codex single-file globals; Copilot instruction path layout.

Do **not** put cross-harness tone/role/git/security in overlays—those stay in shared SoT. Empty overlay → omit the file; adapter may still point only at SoT.

## Harness interview (design, scope=user)

After agreeing `scope=user` and SoT path (`~/.agents/AGENTS.md` default), **AskQuestion** which adapters to write this pass:

> Which harnesses should get adapters now?
> - Claude Code (`~/.claude/CLAUDE.md`)
> - Cursor (`~/.cursor/rules/user-global.mdc`)
> - Codex (`~/.codex/AGENTS.md`)
> - Copilot (`~/.copilot/copilot-instructions.md`)
> - SoT only — adapters later

For each selected harness: ask whether an overlay is needed (or defer with “overlay later / N/A”). Draft SoT + selected adapters + overlays; confirm-before-write covers the **whole set**.

## Adapter templates

### Claude Code (`~/.claude/CLAUDE.md`)

```markdown
@~/.agents/AGENTS.md
@~/.agents/CLAUDE.specific.md
```

Omit the overlay `@` line when no `CLAUDE.specific.md` exists. No policy bullets in the adapter.

### Cursor (`~/.cursor/rules/user-global.mdc`)

```markdown
---
description: User-global agent contract — Read shared SoT before substantive work
alwaysApply: true
---

# User-global (Cursor adapter)

Before substantive work, if not already in context: **Read** `~/.agents/AGENTS.md` and `~/.agents/CURSOR.specific.md` (skip overlay if missing). Do not mirror their bodies here.
```

Hard rule: **no body mirror** of SoT into the `.mdc`.

### Codex (`~/.codex/AGENTS.md`)

```markdown
# User-global (Codex adapter)

Before substantive work, if not already in context: **Read** `~/.agents/AGENTS.md` and `~/.agents/CODEX.specific.md` (skip overlay if missing). Do not paste policy here.
```

### Copilot (`~/.copilot/copilot-instructions.md`)

```markdown
# User-global (Copilot adapter)

Before substantive work, if not already in context: **Read** `~/.agents/AGENTS.md` and `~/.agents/COPILOT.specific.md` (skip overlay if missing). Do not paste policy here.
```

## Drift / anti-mirror rules

- Adapters **never** hold policy (comm, role, git, security, tooling tables).
- If design/review finds an existing Cursor (or other) **mirror** of SoT body (e.g. full `user-global-agents.mdc` duplicate): **challenge** → propose replace with thin stub; write only after user confirm.
- Do not invent auto-sync scripts/hooks in this skill—manual thin stubs only.
- Other harnesses (Windsurf, Aider, Continue, Gemini, …): same pattern (thin entry → Read SoT + optional overlay); no first-class paths in this skill.

## Migration (Claude-centric → multi-harness)

Legacy packs often treat `~/.claude/CLAUDE.md` (or a large `@`-imported file under `~/.claude/`) as the only SoT.

| Step | Action |
|------|--------|
| 1 | Identify always-on body that passes the 90% bar → move/copy into `~/.agents/AGENTS.md` |
| 2 | Split harness-only bullets (models, Task/subagent policy, Claude-native quirks) into `CLAUDE.specific.md` (and other overlays as needed) |
| 3 | Replace `~/.claude/CLAUDE.md` with thin `@` adapter to SoT (+ overlay) |
| 4 | Add Cursor/Codex/Copilot thin stubs only for harnesses the user selected |
| 5 | Delete or empty mirrored policy from old adapter paths after user confirm |

Breaking change stance: **partial** — project layout unchanged; user-global paths/adapters change; design/review must migrate Claude-only packs when found.
