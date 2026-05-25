# context-eng-hero

**Version:** 0.0.1  
**License:** Unlicense (see repo root `LICENSE`)

Design and validate **skills**, **commands**, **rules**, **agents**, and **workflows** so they stay scoped, discoverable, and safe to reuse.

## Skill vs command

| Layer | Responsibility |
|-------|----------------|
| **Skill** (`skills/context-engineer/SKILL.md`) | Classify, clarify, **Harness precedence**, **Action** API—auto-invoked for design questions; loads `refs/actions/*` only via **Run:** when an Action runs |
| **Commands** (`commands/*.md`) | Slash **contracts**: **Progress** (Execute **Action** first, then TodoWrite step ids), required inputs, output—no `refs/` paths in command bodies |

**Orchestration:** plugin commands **cannot chain** on the platform; the umbrella `/context-engineer` command ends with **Next step (user)** pointing to an action slash. See `skills/context-engineer/refs/chat-orchestration.md`.

## Components

| Kind | Path | Role |
|------|------|------|
| Skill | `skills/context-engineer/SKILL.md` | Public API: Classify, Clarify, Actions, routing |
| Commands | `commands/context-engineer*.md` | Design assist + seven verbs (create, extract, audit, fix, redesign, test, diff) |
| Static audit | `scripts/audit_static.py` | Reproducible schema/section/link checks |

## Commands (slash)

| Slash (Cursor) | Purpose |
|----------------|---------|
| `/context-engineer` | Classify + clarify → **Next step (user)**; inline write uses same gates as create |
| `/context-engineer-create` | New artifact from template + static + pre-write reflection + pre-ship |
| `/context-engineer-extract` | Draft + provenance from notes/chat |
| `/context-engineer-audit` | Static script + severity rubric (no edits) |
| `/context-engineer-fix` | Match existing intent; all FAILs + static + reflection + pre-ship |
| `/context-engineer-redesign` | Change outcome/scope + static + reflection + pre-ship; re-audit after |
| `/context-engineer-test` | Behavior probe report |
| `/context-engineer-diff` | Two-path tradeoff report |

## Fix vs redesign

| Intent | Slash |
|--------|-------|
| Audit/test FAILs, typos, same contract | `/context-engineer-fix` |
| Change outcome, audience, or capabilities | `/context-engineer-redesign` |

Design assist (`/context-engineer`) routes using one AskQuestion when ambiguous. Full matrix: `skills/context-engineer/SKILL.md` **Routing**.

## Python runtime

Prefer **CPython 3.14+** for `scripts/audit_static.py`. Bootstrap and invocation: [`CLAUDE.md`](CLAUDE.md) **Python runtime**.

Monorepo contributors: see repo-root [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Static audit (local)

From this directory (plugin root), after installing deps per `CLAUDE.md`:

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
- **Write** paths (create, fix, redesign, design-assist write) run **pre-write reflection** (judgment rubric + harness checks) after static and before pre-ship—no disk write on `PRE-WRITE REFLECTION FAILED`.

The skill description intentionally avoids ambient audit/fix triggers; use the **audit** / **fix** / **redesign** slashes when you mean those verbs.

## Manifests

- Cursor: `.cursor-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json`

Both use `name: context-eng-hero` matching the directory name under `plugins/`.
