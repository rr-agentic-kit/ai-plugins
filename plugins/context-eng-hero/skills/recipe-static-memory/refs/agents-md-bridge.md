# Canonical agent instruction layout

Project (default) and user-global (opt-in) use the same shape.

## Target layout

```text
CLAUDE.md                 # Claude Code: @AGENTS.md (+ optional @.agents/local.md)
AGENTS.md                 # Always-on: 90%-leverage only
.agents/{group}.md        # Optional situational packs — names derived from THIS project
.agents/local.md          # Gitignored personal override (not a shared pack)
```

**Cursor** loads `AGENTS.md` as the always-on agent contract. **Claude Code** loads `CLAUDE.md`; keep it a thin `@AGENTS.md` pointer so both runtimes share one SoT.

## Load semantics (hard rule — token win)

| Mechanism | Expands when | Use for |
|-----------|--------------|---------|
| `@path` | Claude Code launch (imports expand into context) | Always-on: `CLAUDE.md` → `@AGENTS.md`; optional `@.agents/local.md`; other approved always-on splits |
| Backticked path + when-to-Read trigger | On demand (agent Reads when trigger matches) | Situational packs: `` `.agents/{group}.md` `` |

**Never** `@`-import shared situational packs from `CLAUDE.md` or `AGENTS.md`. Sole `.agents/` `@` exception: gitignored `.agents/local.md` (personal always-on).

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

On project design/review: if parallel instruction files conflict with `AGENTS.md`, report deltas; user picks one SoT.

## User-global

Same shape when `scope=user` is explicit. Still apply the 90% bar (cross-repo prefs that almost always help)—not a preference dump. Do not reference a single repo’s packs unless the user names a personal template path.
