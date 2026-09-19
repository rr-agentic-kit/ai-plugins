---
name: recipe-static-memory
description: Authors or repairs project/user AGENTS.md instruction packs. Use when designing, reviewing, or fixing memory files—not plugin skills or commands.
---

# Static memory (agent instruction packs)

## Purpose

Author or repair **agent instruction packs**—persistent instructions that improve agent results. Default **scope = project**. User-global only when the user says so.

| Scope | Always-on SoT | Claude Code pointer | Optional depth |
|-------|---------------|---------------------|----------------|
| **Project** (default) | `AGENTS.md` | `CLAUDE.md` → `@AGENTS.md` | `.agents/{group}.md` |
| **User** (opt-in) | Same shape under user config | User `CLAUDE.md` → `@` always-on | Same pack rules |

**Inclusion bar (non-negotiable):** Not a project bible. Not “everything the user asked for.” Keep only constraints that improve or prevent mistakes in **~90%+** of chats. Prefer pointers to README / CONTRIBUTING / ADRs / plugin docs over absorbing them.

Not plugin artifacts (**recipe-context-engineer**).

## When to use

- Creating **from scratch** project (default) or user-global instruction packs
- **Section-by-section** review of existing always-on / situational files
- **Symptom-led** minimal fixes when agent behavior diverges from stated preferences

## Procedure

1. If the user message is a plugin command for verb V: read the action **Run** ref, execute **Action: V**, honor command **Progress** TodoWrite ids.
2. If ambient (no slash): apply **Routing**; end with **Next step (user)** to one slash—no user-file write.
3. Parse the initial prompt to pre-fill questionnaires; do not re-ask captured preferences.
4. Load shared refs only via the active action **Load** list—never invent steps outside that ref.
5. Default `scope=project` unless user explicitly names user-global / `~/.claude/`.
6. Memory-file writes require explicit confirm-before-write per the action ref.

## When not to use

- Plugin **skills**, **commands**, **rules**, or **workflows** under `plugins/` → **recipe-context-engineer**
- One-off task prompts with no durable memory file
- Dumping README / CONTRIBUTING / product narrative into agent memory “for completeness”
- Enterprise policy paths (out of scope)

## Harness precedence

- **Plugin command prompt** wins for **Progress**, **REQUIRED** inputs, and **Output** this turn.
- **Action** + **Run:** is the only path to load `refs/actions/*` and section-specific refs—do not invent steps outside the active action ref.
- **Ambient invoke** (no slash): route per **Routing**; end with **Next step (user)**; no TodoWrite unless user chose an action slash this turn.
- Memory-file writes use **confirm-before-write** in action refs—not plugin `shared-write-gates.md`.

## Actions

| Action id | User slash (Cursor) | One-line outcome | Run |
|-----------|---------------------|------------------|-----|
| design | `/static-memory-design` | Full draft from scratch (gather → confirm → write) | `refs/actions/design.md` |
| review | `/static-memory-review` | Section walkthrough; accept / edit / deep-dive; may delete low-leverage | `refs/actions/review.md` |
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

On design/review/fix: **challenge** user requests that fail the 90% bar—route to docs, skills, or situational packs only when the miss is real and recurring.

## Communication + Role (user-global design)

On **design** for **user** scope: **Communication contract** and **Role framing** are **mandatory** and **exhaustive**—load `communication-role-exhaustive.md` (checkpoint groups A/B; resumable). **Tooling & agents** (§6) uses `tooling-orchestration.md` (checkpoint C). No whole-section skip; per-dimension N/A only with reason. See action **design** ref.

Project scope: usually **omit** comm/role (point to user-global); always-on stays lean per `effective-writing.md`.

## Shared refs

| Ref | Role |
|-----|------|
| `memory-hierarchy.md` | Scopes, load order, `@` vs backtick |
| `agents-md-bridge.md` | Canonical layout, load semantics, docs boundary |
| `situation-groups.md` | Derive situational pack names; anti-catalog; when not to pack |
| `communication-role-exhaustive.md` | Mandatory questionnaires for comm + role (checkpoint A/B) |
| `tooling-orchestration.md` | Situation → capability triggers for §6 (checkpoint C) |
| `user-global-synthesis.md` | Global vs project buckets; synthesis rules |
| `user-sections-template.md` | User-global section order (review + design) |
| `project-init-flow.md` | Project **design**: explore codebase |
| `project-sections-template.md` | Always-on sections shaped by leverage |
| `effective-writing.md` | 90% filter, budgets, pointer-over-paste, no `@` packs |
| `fix-intake.md` | Symptom → always-on vs trigger vs docs |

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
