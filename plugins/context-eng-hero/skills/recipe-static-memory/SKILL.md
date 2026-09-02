---
name: recipe-static-memory
description: Authors or repairs user-global and project CLAUDE.md static memory. Use when designing, reviewing, or fixing memory files—not plugin skills or commands.
---

# Static memory (CLAUDE.md)

## Purpose

Author or repair **user-global** (Claude Code user config `CLAUDE.md`) and **project** (`CLAUDE.md` or `.claude/CLAUDE.md` in the repo) static memory—persistent instructions loaded every session. Not plugin artifacts (**recipe-context-engineer**).

## When to use

- Creating **from scratch** a user-global or project memory file
- **Section-by-section** review of an existing CLAUDE.md
- **Symptom-led** minimal fixes when Claude behavior diverges from stated preferences

## Procedure

1. If the user message is a plugin command for verb V: read the action **Run** ref, execute **Action: V**, honor command **Progress** TodoWrite ids.
2. If ambient (no slash): apply **Routing**; end with **Next step (user)** to one slash—no user-file write.
3. Parse the initial prompt to pre-fill questionnaires; do not re-ask captured preferences.
4. Load shared refs only via the active action **Load** list—never invent steps outside that ref.
5. User CLAUDE.md writes require explicit confirm-before-write per the action ref.

## When not to use

- Plugin **skills**, **commands**, **rules**, or **workflows** under `plugins/` → **recipe-context-engineer**
- One-off task prompts with no durable memory file
- Enterprise policy paths (out of scope)

## Harness precedence

- **Plugin command prompt** wins for **Progress**, **REQUIRED** inputs, and **Output** this turn.
- **Action** + **Run:** is the only path to load `refs/actions/*` and section-specific refs—do not invent steps outside the active action ref.
- **Ambient invoke** (no slash): route per **Routing**; end with **Next step (user)**; no TodoWrite unless user chose an action slash this turn.
- User CLAUDE.md writes use **confirm-before-write** in action refs—not plugin `shared-write-gates.md`.

## Actions

| Action id | User slash (Cursor) | One-line outcome | Run |
|-----------|---------------------|------------------|-----|
| design | `/static-memory-design` | Full draft from scratch (gather → confirm → write) | `refs/actions/design.md` |
| review | `/static-memory-review` | Section walkthrough; accept / edit / deep-dive | `refs/actions/review.md` |
| fix | `/static-memory-fix` | Symptom-led minimal patch | `refs/actions/fix.md` |

Read and execute the **Run** ref for the active action; contracts live there—not in this table.

## Routing

| Situation | Next slash |
|-----------|------------|
| No file / empty / user wants full rewrite | `/static-memory-design` |
| File exists; systematic section audit | `/static-memory-review` |
| Something went wrong (symptom + path) | `/static-memory-fix` |
| Target exists; user did not confirm rewrite on **design** | `/static-memory-review` or `/static-memory-fix` |
| Fix symptom = totally different persona or outcome | `/static-memory-design` (not fix) |

When ambiguous, one **AskQuestion**: “No file / section walkthrough / fix a problem?”

**Parse initial prompt** on all verbs to pre-fill answers; avoid re-asking captured preferences.

## Communication + Role (user-global design)

On **design** for **user** scope: **Communication contract** and **Role framing** are **mandatory** and **exhaustive**—load `communication-role-exhaustive.md` (checkpoint groups A/B; resumable). **Tooling & agents** (§6) uses `tooling-orchestration.md` (checkpoint C). No whole-section skip; per-dimension N/A only with reason. See action **design** ref.

Project scope: usually **omit** comm/role (point to user-global); project sections stay ≤200 lines.

## Shared refs

| Ref | Role |
|-----|------|
| `memory-hierarchy.md` | Scopes, load order, imports |
| `communication-role-exhaustive.md` | Mandatory questionnaires for comm + role (checkpoint A/B) |
| `tooling-orchestration.md` | Situation → capability triggers for §6 (checkpoint C) |
| `user-global-synthesis.md` | Global vs project buckets; synthesis rules |
| `user-sections-template.md` | User-global section order (review + design) |
| `project-init-flow.md` | Project **design**: explore codebase |
| `project-sections-template.md` | Project section order |
| `effective-writing.md` | Testable bullets, line budgets, stale detection |
| `agents-md-bridge.md` | Parallel instruction files (`AGENTS.md`, path-scoped rules) |
| `fix-intake.md` | Symptom → section mapping; scope guard |

## Orchestration

Commands **cannot chain** on the platform. Point users to the right slash—do not auto-invoke another command.

## Plugin commands (human map)

| Cursor | Claude Code |
|--------|-------------|
| `/static-memory-design` | `/context-eng-hero:static-memory-design` |
| `/static-memory-review` | `/context-eng-hero:static-memory-review` |
| `/static-memory-fix` | `/context-eng-hero:static-memory-fix` |

## Invocation

- **Cursor:** `/static-memory-*` as installed from the plugin.
- **Claude Code:** `/context-eng-hero:static-memory-*`.
