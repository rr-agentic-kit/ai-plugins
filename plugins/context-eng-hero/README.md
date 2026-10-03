# context-eng-hero

**Version:** 0.0.2  
**License:** Unlicense (see repo root `LICENSE`)

Design and validate **skills**, **commands**, **rules**, **agents**, and **workflows**—and author **project / user-global agent instruction packs** (project: `AGENTS.md` + optional `.agents/` packs + Claude `CLAUDE.md` pointer; user-global: shared `~/.agents/AGENTS.md` + thin multi-harness adapters).

## Skills (recipe-* convention)

| Skill | Path | Role |
|-------|------|------|
| **recipe-context-engineer** | `skills/recipe-context-engineer/SKILL.md` | Plugin artifacts: classify, clarify, actions (create, audit, fix, …) |
| **recipe-static-memory** | `skills/recipe-static-memory/SKILL.md` | Project (default) / user-global multi-harness `AGENTS.md` packs (design, review, fix) |

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
| Auto-learn hooks | `hooks/` + `scripts/auto_learn.sh` | Dual-runtime drift detector → Stop inject `--auto-learn` |

## Auto-learn (Stop-hook drift detector)

When a session Reads a **local source** skill (`plugins/.../skills/.../SKILL.md` or project `.claude/skills` / `.agents/skills` under the workspace — **not** `~/.claude/plugins/cache/**` or `~/.cursor/plugins/cache/**`) and drift signals fire (thrash, reread, fail-retry, bash discovery loop, correction+thrash), the **Stop** hook may inject:

`Run /recipe-context-engineer --auto-learn on <absorb-into SKILL.md> …`

| Mode | Behaviour |
|------|-----------|
| `--learn` | Interactive: AskQuestion + **post-learn-routing** |
| `--learn --auto` ≡ `--auto-learn` | Silent learn steps 1–4, then auto-start absorb (fix/redesign) on plugin source; **Next Up**; no second loop |

**SessionEnd is not the learn trigger** — cleanup of `.ai/learning/ce-auto-learn/<session_id>/` only. Fail-open: missing Python / mkdir / below-threshold → silent exit 0, no inject. Cursor `stop` uses `loop_limit: 1`; evidence is marked **consumed** after inject.

Dual-runtime: `hooks/hooks.json` (Claude) + `hooks/cursor.json` (via `.cursor-plugin/plugin.json` `"hooks"`).

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
| `/static-memory-design` | `/context-eng-hero:static-memory-design` | Full pack from scratch; default scope=project (`AGENTS.md` + `CLAUDE.md`); user-global → `~/.agents/AGENTS.md` + adapters |
| `/static-memory-review` | `/context-eng-hero:static-memory-review` | Section walkthrough; may delete low-leverage; optional packs/overlays |
| `/static-memory-fix` | `/context-eng-hero:static-memory-fix` | Symptom-led minimal patch |

### Static memory layout (project default)

```text
CLAUDE.md          # @AGENTS.md (+ optional @.agents/local.md)
AGENTS.md          # Always-on: ~90%-leverage only (inclusion bar)
.agents/{group}.md # Optional situational packs — names derived per repo; never @-imported
.agents/local.md   # Gitignored personal override (sole .agents @ exception)
```

### Static memory layout (user-global opt-in)

```text
~/.agents/AGENTS.md                 # Shared SoT (cross-harness)
~/.agents/{HARNESS}.specific.md     # Optional harness overlays
~/.claude/CLAUDE.md                 # Thin @ adapter → SoT (+ overlay)
~/.cursor/rules/user-global.mdc     # Thin alwaysApply Read-forcing stub
~/.codex/AGENTS.md                  # Thin Read-forcing stub
~/.copilot/copilot-instructions.md  # Thin Read-forcing stub
```

**Inclusion bar:** agent contract, not project bible—pointer to README/CONTRIBUTING over paste. Zero packs is valid. Adapters never mirror SoT body. Detail: `skills/recipe-static-memory/refs/user-global-multi-harness.md`.

### Static memory routing

| Situation | Slash |
|-----------|-------|
| No file / full rewrite | `/static-memory-design` |
| File exists; systematic audit | `/static-memory-review` |
| Agent misbehaved (symptom + path) | `/static-memory-fix` |
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
- Use `/static-memory-*` for project (default) or user-global instruction packs—not for files under `plugins/`.
- **Audit** verdict is **PASS** only when every static and judgment check passes—no numeric score.
- **Write** paths for plugin artifacts run **pre-write reflection** after static and before pre-ship. Memory-file writes use **confirm-before-write** in static action refs.

The skill descriptions intentionally avoid ambient audit/fix triggers; use the matching slash when you mean that verb.

## Manifests

- Cursor: `.cursor-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json`

Both use `name: context-eng-hero` matching the directory name under `plugins/`.
