# Canonical agent instruction layout

**Project** (default) and **user-global** (opt-in) share the 90% inclusion bar and `@` vs Read-trigger rules—but **not** the same filesystem shape. User-global multi-harness: `user-global-multi-harness.md`.

## Project layout (default; unchanged)

```text
CLAUDE.md                 # Claude Code: @AGENTS.md (+ optional @.agents/local.md)
AGENTS.md                 # Always-on: 90%-leverage only
.agents/{group}.md        # Optional situational packs — names derived from THIS project
.agents/local.md          # Gitignored personal override (not a shared pack)
```

**Cursor** loads `AGENTS.md` as the always-on agent contract. **Claude Code** loads `CLAUDE.md`; keep it a thin `@AGENTS.md` pointer so both runtimes share one SoT.

## User-global layout (opt-in; multi-harness)

```text
~/.agents/AGENTS.md              # Shared SoT (cross-harness always-on)
~/.agents/{HARNESS}.specific.md  # Optional harness overlays (CLAUDE|CURSOR|CODEX|COPILOT)

# Thin adapters — entry points only; never duplicate SoT body
~/.claude/CLAUDE.md              # @ SoT (+ optional @ CLAUDE.specific)
~/.cursor/rules/user-global.mdc  # alwaysApply Read-forcing stub
~/.codex/AGENTS.md               # Read-forcing stub (respect CODEX_HOME)
~/.copilot/copilot-instructions.md
```

Do **not** treat “same shape under `~/.claude/`” as the user-global SoT. Claude’s home file is an **adapter**; the shared body is `~/.agents/AGENTS.md`.

## Load semantics (hard rule — token win)

| Mechanism | Expands when | Use for |
|-----------|--------------|---------|
| `@path` | Claude Code launch (imports expand into context) | Project: `CLAUDE.md` → `@AGENTS.md`; optional `@.agents/local.md`. User: Claude adapter → `@~/.agents/AGENTS.md` (+ optional overlay `@`) |
| Thin adapter + Read force | On demand when stub instructs (Cursor / Codex / Copilot) | User-global only: stub points at SoT + optional `*.specific.md`; **no** policy body in the stub |
| Backticked path + when-to-Read trigger | On demand (agent Reads when trigger matches) | Situational packs: `` `.agents/{group}.md` `` |

**Never** `@`-import shared situational packs from `CLAUDE.md` or `AGENTS.md`. Sole project `.agents/` `@` exception: gitignored `.agents/local.md` (personal always-on).

**Never** mirror SoT into Cursor `.mdc` or other adapters. On design/review, challenge existing mirrors → thin stub (user confirm).

## Namespace collision

Cursor uses `.agents/skills/` for Agent Skills. Instruction packs are **flat** `.agents/{group}.md` only—do not place packs under `.agents/skills/`.

## Docs boundary (not agent memory)

| Keep in agent memory | Defer / omit |
|----------------------|--------------|
| Improves results in ~90%+ of chats | Rare workflows, long procedures, narrative product docs |
| Prevents mistakes in ~90% of chats | Content already authoritative in README / CONTRIBUTING / ADRs / plugin READMEs |
| Short, testable constraints + copy-paste commands agents need every session | Duplicating docs “for completeness” |

**Pointer, don’t copy:** Prefer “see `CONTRIBUTING.md` / plugin `README.md` / `plugins/.../CLAUDE.md`” over absorbing those files. `AGENTS.md` is the **agent contract**, not the whole project doc set.

Zero situational packs is valid when always-on stays lean. Do **not** invent packs to mirror CONTRIBUTING.

## Parallel / legacy files

| Pattern | Role |
|---------|------|
| Path-scoped rules (e.g. `**/rules/*`) | Scoped overrides; discover—do not assume vendor or layout |
| Legacy single-file rules | Note if present; user picks SoT—no auto-merge |
| User-global Claude-only pack under `~/.claude/` | Migrate body → `~/.agents/AGENTS.md`; leave thin `@` adapter (see multi-harness migration) |
| User-global Cursor body mirror (e.g. full policy in `.mdc`) | Challenge → replace with thin Read-forcing stub |

On project design/review: if parallel instruction files conflict with `AGENTS.md`, report deltas; user picks one SoT.

## User-global scope rules

When `scope=user` is explicit: still apply the 90% bar (cross-repo prefs that almost always help)—not a preference dump. Ask which harness adapters to write; draft SoT + selected adapters + overlays together. Do not reference a single repo’s packs unless the user names a personal template path.
