# context-eng-hero

**Version:** 0.0.1  
**License:** Unlicense (see repo root `LICENSE`)

Design and validate **skills**, **commands**, **rules**, **agents**, and **workflows** so they stay scoped, discoverable, and safe to reuse.

## Skill vs command

| Layer | Responsibility |
|-------|----------------|
| **Skill** (`skills/context-engineer/SKILL.md`) | Classify, clarify, **Action** API, ref index—auto-invoked for design questions; loads `refs/` only when an Action runs |
| **Commands** (`commands/*.md`) | Slash **contracts**: required inputs + “Execute **Action: …** in skill **context-engineer**”—action verbs include **Progress** (TodoWrite per step) |

**Orchestration:** plugin commands **cannot chain** on the platform; the umbrella `/context-engineer` command ends with **Next step (user)** pointing to an action slash. See `skills/context-engineer/refs/chat-orchestration.md`.

## Components

| Kind | Path | Role |
|------|------|------|
| Skill | `skills/context-engineer/SKILL.md` | Public API: Classify, Clarify, Actions, ref index |
| Commands | `commands/context-engineer*.md` | Design assist + six verbs (create, extract, audit, rewrite, test, diff) |
| Static audit | `scripts/audit_static.py` | Reproducible schema/section/link checks |

## Commands (slash)

| Slash (Cursor) | Purpose |
|----------------|---------|
| `/context-engineer` | Classify + clarify only → **Next step (user)** |
| `/context-engineer-create` | New artifact from template + pre-ship |
| `/context-engineer-extract` | Draft + provenance from notes/chat |
| `/context-engineer-audit` | Static script + severity rubric (no edits) |
| `/context-engineer-rewrite` | Fix all audit FAILs + static + pre-ship |
| `/context-engineer-test` | Behavior probe report |
| `/context-engineer-diff` | Two-path tradeoff report |

**Claude Code:** prefix with `/context-eng-hero:` (e.g. `/context-eng-hero:context-engineer-audit`).

## Python runtime

Prefer **CPython 3.14+** for `scripts/audit_static.py`. Bootstrap and invocation: `skills/context-engineer/refs/python-runtime.md`. Agent contract: [`CLAUDE.md`](CLAUDE.md).

Monorepo contributors: see repo-root [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Static audit (local)

From this directory (plugin root), after installing deps per `python-runtime.md`:

```bash
python3 scripts/audit_static.py . skills/context-engineer/SKILL.md
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
- **Audit** verdict is **PASS** only when every static and judgment check passes—no numeric score.

The skill description intentionally avoids ambient audit/rewrite triggers; use the **audit** / **rewrite** slashes when you mean those verbs.

## Manifests

- Cursor: `.cursor-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json`

Both use `name: context-eng-hero` matching the directory name under `plugins/`.
