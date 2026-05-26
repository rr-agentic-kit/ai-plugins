---
name: recipe-context-engineer
description: Classifies and designs agent context artifacts (skills, commands, rules, agents, workflows). Use when choosing artifact type, structuring definitions, or clarifying scope—not for ambient code review or repository-wide edits.
---

# Context engineer

## Purpose

Make **skills, commands, rules, agents, and workflows** discoverable, bounded, and safe to reuse—without mixing judgment workflows with high-risk edits.

## When to use

- Picking or narrowing **artifact type**
- **Clarifying** outcome, audience, and failure modes before authoring
- Designing **contracts** (inputs, outputs, stop rules) and **progressive disclosure** (refs)
- Pointing authors to the right **slash action** (audit, fix, redesign, test, diff, create, extract)

## When not to use

- Ad-hoc **production code review** with no artifact path
- **Ambient** “audit everything” without a declared target file
- Tasks that need **repo-wide** exploration without a scoped question—use a explore subagent at the user’s direction first

## Classify

Pick the **narrowest** artifact type:

| Type | When |
|------|------|
| **Skill** | Reusable procedure, policy, or checklist invoked across tasks |
| **Command** | Named slash entry with a **fixed** input/output contract |
| **Agent** | Role with tools, boundaries, and **stop conditions** |
| **Rule** | Always-on constraint for paths/globs |
| **Workflow** | Multi-step orchestration with **delegation** and per-step outputs |

Do not merge types (e.g. a skill is not a command unless both files exist for a reason).

## Clarify

Before authoring, resolve (ask if missing):

1. **Outcome** — what changes in the world when this succeeds?
2. **Audience** — which runtime/human applies this?
3. **Failure mode** — what bad behavior must this block?

Use **AskQuestion** when choices are enumerable. For multi-step **implementation** across files, prefer a user **action slash** (tracked todos)—see `chat-orchestration.md`. This skill does not auto-spawn TodoWrite on ambient invoke.

## Procedure

1. Run **Classify** and **Clarify** for design tasks.
2. If the user message is a plugin command for verb V: execute **Action: V** (Read **Run:** ref first), then honor that command’s **Progress** TodoWrite ids. Otherwise route per **Routing**—no write actions without an explicit slash or approved write branch.
3. Do **not** chain commands as automation—commands cannot invoke each other on the platform.

Rubrics, templates, and step-by-step procedures stay under `refs/`; load via each action’s **Run:** ref. Refs are loaded via action **Load** sections; see `refs/` directory.

## Harness precedence

- **Plugin command prompt** wins for **Progress**, **REQUIRED** inputs, and **Output** this turn.
- **Action** + **Run:** is the only path to load `refs/actions/*` and write gates—do not invent steps outside the active action ref.
- **Ambient invoke** (no slash): **Classify** + **Clarify** + **Routing**; end with **Next step (user)**; no TodoWrite unless the user chose the `/context-engineer` write branch.
- When the user message includes a command **Progress** block, do not skip **TodoWrite** step tracking.

## Actions

| Action id | User slash (Cursor) | One-line outcome | Run |
|-----------|---------------------|------------------|-----|
| create | `/context-engineer-create` | New artifact from template + static + reflection + pre-ship | `refs/actions/create.md` |
| extract | `/context-engineer-extract` | Draft artifact + provenance from context | `refs/actions/extract.md` |
| audit | `/context-engineer-audit` | Static script + severity rubric (no edits) | `refs/actions/audit.md` |
| fix | `/context-engineer-fix` | Match existing intent; all FAILs + static + reflection + pre-ship | `refs/actions/fix.md` |
| redesign | `/context-engineer-redesign` | Change outcome/scope + static + reflection + pre-ship; re-audit after | `refs/actions/redesign.md` |
| test | `/context-engineer-test` | Behavior probe report | `refs/actions/test.md` |
| diff | `/context-engineer-diff` | Two-path tradeoff summary | `refs/actions/diff.md` |

Read and execute the **Run** ref for the active action; contracts (purpose, inputs, output, stop) live there—not in this table.

## Routing (fix vs redesign)

| Signal | Next slash |
|--------|------------|
| Audit verdict FAIL | `/context-engineer-fix` + report |
| Test probe FAIL, same contract | `/context-engineer-fix` + test report |
| Test FAIL / user story = wrong capability or outcome | `/context-engineer-redesign` |
| User: add step, remove gate, change audience | `/context-engineer-redesign` |
| User: wording, typo, violates own stop rule | `/context-engineer-fix` |
| Extract → production with **resolved** open questions | `/context-engineer-redesign` (first ship) or `/context-engineer-fix` (polish only) |

When ambiguous, one **AskQuestion**: “Changing what it does?” → redesign if yes, else fix.

## Design assist (`/context-engineer`)

- **Default:** **Classify** + **Clarify** only; end with **Next step (user)** to one action slash—no file write.
- **If writing this turn:** user explicitly requests a file at an approved plugin-relative path → Read and execute `refs/actions/design.md` (same gates as create).

## Orchestration

Commands **cannot chain** on the platform. **Action slash commands** own **TodoWrite** step tracking. Skills and workflows **describe** todo mapping for authors and executors—see `chat-orchestration.md`.

## Plugin commands (human map)

Design assist: `/context-engineer` → **Classify** + **Clarify**; **Next step (user)** unless user requests inline write (then `refs/actions/design.md`).  
Actions: see **Actions** table above—each command file is a black box that names this skill + Action id only.

## Invocation

- **Cursor:** `/context-engineer` and `/context-engineer-*` as installed from the plugin.
- **Claude Code:** `/context-eng-hero:context-engineer` and `/context-eng-hero:context-engineer-*`.
