# context-eng-hero

**Version:** 0.0.1  
**License:** Unlicense (see repo root `LICENSE`)

Design and validate **skills**, **commands**, **rules**, **agents**, and **workflows**—and author **user-global / project CLAUDE.md** static memory.

## Skills (recipe-* convention)

| Skill | Path | Role |
|-------|------|------|
| **recipe-context-engineer** | `skills/recipe-context-engineer/SKILL.md` | Plugin artifacts: classify, clarify, actions (create, audit, fix, …) |
| **recipe-static-memory** | `skills/recipe-static-memory/SKILL.md` | User-global and project `CLAUDE.md` (design, review, fix) |

### Skill vs command

| Layer | Responsibility |
|-------|----------------|
| **Skill** | Harness precedence, **Action** API, routing; loads `refs/actions/*` only via **Run:** when an Action runs |
| **Commands** | Slash **contracts**: **Progress** (Execute **Action** first, then TodoWrite step ids), required inputs, output—no `refs/` paths in command bodies |

**Orchestration:** plugin commands **cannot chain** on the platform; the umbrella `/context-engineer` command ends with **Next step (user)** pointing to an action slash. See `skills/recipe-context-engineer/refs/chat-orchestration.md`.

## Components

| Kind | Path | Role |
|------|------|------|
| Skills | `skills/recipe-context-engineer/`, `skills/recipe-static-memory/` | Public API per skill |
| Commands | `commands/*.md` | Design assist + plugin verbs + static memory verbs |
| Static audit | `scripts/audit_static.py` | Reproducible schema/section/link checks |

## Commands — plugin artifacts (context-engineer)

| Slash (Cursor) | Claude Code | Purpose |
|----------------|-------------|---------|
| `/context-engineer` | `/context-eng-hero:context-engineer` | Classify + clarify → **Next step (user)**; inline write uses same gates as create |
| `/context-engineer-create` | `/context-eng-hero:context-engineer-create` | New artifact from template + static + pre-write reflection + pre-ship |
| `/context-engineer-extract` | `/context-eng-hero:context-engineer-extract` | Draft + provenance from notes/chat |
| `/context-engineer-audit` | `/context-eng-hero:context-engineer-audit` | Static script + severity rubric (no edits) |
| `/context-engineer-fix` | `/context-eng-hero:context-engineer-fix` | Match existing intent; all FAILs + static + reflection + pre-ship |
| `/context-engineer-redesign` | `/context-eng-hero:context-engineer-redesign` | Change outcome/scope + static + reflection + pre-ship |
| `/context-engineer-test` | `/context-eng-hero:context-engineer-test` | Behavior probe report |
| `/context-engineer-diff` | `/context-eng-hero:context-engineer-diff` | Two-path tradeoff report |

## Commands — static memory

| Slash (Cursor) | Claude Code | Purpose |
|----------------|-------------|---------|
| `/static-memory-design` | `/context-eng-hero:static-memory-design` | Full CLAUDE.md from scratch (exhaustive comm+role for user-global) |
| `/static-memory-review` | `/context-eng-hero:static-memory-review` | Section walkthrough: accept / edit / deep-dive |
| `/static-memory-fix` | `/context-eng-hero:static-memory-fix` | Symptom-led minimal patch |

### Static memory routing

| Situation | Slash |
|-----------|-------|
| No file / full rewrite | `/static-memory-design` |
| File exists; systematic audit | `/static-memory-review` |
| Claude misbehaved (symptom + path) | `/static-memory-fix` |
| Plugin skill/command authoring | `/context-engineer` or `/context-engineer-create` |

Full routing: `skills/recipe-static-memory/SKILL.md` **Routing**.

## Fix vs redesign (plugin artifacts)

| Intent | Slash |
|--------|-------|
| Audit/test FAILs, typos, same contract | `/context-engineer-fix` |
| Change outcome, audience, or capabilities | `/context-engineer-redesign` |

Design assist (`/context-engineer`) routes using one AskQuestion when ambiguous. Full matrix: `skills/recipe-context-engineer/SKILL.md` **Routing**.

## Python runtime

Prefer **CPython 3.14+** for `scripts/audit_static.py`. Bootstrap and invocation: [`CLAUDE.md`](CLAUDE.md) **Python runtime**.

Monorepo contributors: see repo-root [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Static audit (local)

From this directory (plugin root), after installing deps per `CLAUDE.md`:

```bash
python3 scripts/audit_static.py . skills/recipe-context-engineer/SKILL.md
python3 scripts/audit_static.py . skills/recipe-static-memory/SKILL.md
```

## Install

### Cursor

1. Ensure the **ai-plugins** marketplace is added and points at this repository’s **root** (not only the plugin folder).
2. Install plugin **context-eng-hero** from that marketplace.

### Claude Code

1. `/plugin marketplace add <repo-root-url-or-path>`
2. `/plugin install context-eng-hero@ai-plugins`

### Local plugin dir (Claude Code)

```bash
claude --plugin-dir ./plugins/context-eng-hero
```

(Run from the **ai-plugins** repo root, or pass an absolute path to `plugins/context-eng-hero`.)

## Usage

- Give action commands a **REQUIRED** path or goal per the command file. If missing, ask once.
- Use `/context-engineer` when you need type choice + clarify gates before picking an action slash.
- Use `/static-memory-*` for user-global or project `CLAUDE.md`—not for files under `plugins/`.
- **Audit** verdict is **PASS** only when every static and judgment check passes—no numeric score.
- **Write** paths for plugin artifacts run **pre-write reflection** after static and before pre-ship. User `CLAUDE.md` writes use **confirm-before-write** in static action refs.

The skill descriptions intentionally avoid ambient audit/fix triggers; use the matching slash when you mean that verb.

## Manifests

- Cursor: `.cursor-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json`

Both use `name: context-eng-hero` matching the directory name under `plugins/`.
