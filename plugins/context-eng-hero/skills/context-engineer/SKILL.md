---
name: context-engineer
description: Classifies and designs agent context artifacts (skills, commands, rules, agents, workflows). Use when choosing artifact type, structuring definitions, or clarifying scope—not for ambient code review or repository-wide edits.
---

# Context engineer

## Purpose

Make **skills, commands, rules, agents, and workflows** discoverable, bounded, and safe to reuse—without mixing judgment workflows with high-risk edits.

## When to use

- Picking or narrowing **artifact type**
- **Clarifying** outcome, audience, and failure modes before authoring
- Designing **contracts** (inputs, outputs, stop rules) and **progressive disclosure** (refs)
- Pointing authors to the right **slash action** (audit, rewrite, test, diff, create, extract)

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
2. For **verbs** (create, extract, audit, rewrite, test, diff), the user runs the matching **plugin command**; the command delegates to the **Action** section below—then **Read** the listed internal procedure file.
3. Do **not** chain commands as automation—commands cannot invoke each other on the platform.

Rubrics, templates, and step-by-step procedures stay under `refs/` (see **Ref index**); this file keeps the stable **Action** contracts only.

## Actions

| Action id | User slash (Cursor) | One-line outcome |
|-----------|---------------------|------------------|
| create | `/context-engineer-create` | New artifact file from template + pre-ship |
| extract | `/context-engineer-extract` | Draft artifact + provenance from context |
| audit | `/context-engineer-audit` | Static script + severity rubric (no edits) |
| rewrite | `/context-engineer-rewrite` | Fix all audit FAILs + static + pre-ship |
| test | `/context-engineer-test` | Behavior probe report |
| diff | `/context-engineer-diff` | Two-path tradeoff summary |

Claude Code: prefix slashes with `/context-eng-hero:` (e.g. `/context-eng-hero:context-engineer-audit`).

## Action: create

- **Purpose:** Author one new definition from template.
- **Required input:** One-line goal; artifact type (or agree via classify); target relative path inside the plugin.
- **Output:** Written file **or** `PRE-SHIP FAILED` report (draft in chat only).
- **Stop:** No write on any pre-ship FAIL.
- **Run:** Read and execute `refs/actions/create.md`.

## Action: extract

- **Purpose:** Turn chat/workflow notes into a typed draft.
- **Required input:** Source context (pasted or summarized); target type if known.
- **Output:** Draft + **provenance** (source, assumptions, open questions).
- **Stop:** Do not claim production-ready with open questions unanswered.
- **Run:** Read and execute `refs/actions/extract.md`.

## Action: audit

- **Purpose:** Static + judgment quality diagnosis.
- **Required input:** Path to definition file (plugin-relative).
- **Output:** Report per `refs/audit-output.template.md`—verdict **PASS** only if all checks pass; severity summaries; no numeric score.
- **Stop:** No edits.
- **Run:** Read and execute `refs/actions/audit.md`. Static: `python3 scripts/audit_static.py . <path>` from plugin root after PyYAML bootstrap (`refs/python-runtime.md`). Monorepo contributors: repo-root `CONTRIBUTING.md` (not in the installed plugin).

## Action: rewrite

- **Purpose:** Apply minimal fixes; prefer prior audit report.
- **Required input:** Path; audit report with FAIL ids (preferred).
- **Output:** Patch or file write **or** `PRE-SHIP FAILED`.
- **Stop:** Fix **every** FAIL (all severities); rerun static script + pre-ship before write.
- **Run:** Read and execute `refs/actions/rewrite.md`.

## Action: test

- **Purpose:** Simulate behavior against fixed probes.
- **Required input:** Path to definition file.
- **Output:** Report per `refs/test-output.template.md`.
- **Stop:** No file edits.
- **Run:** Read and execute `refs/actions/test.md`.

## Action: diff

- **Purpose:** Compare two definitions for intent and contracts.
- **Required input:** Two plugin-relative paths **A** and **B**.
- **Output:** Report per `refs/diff-output.template.md`.
- **Stop:** No file edits.
- **Run:** Read and execute `refs/actions/diff.md`.

## Orchestration

Commands **cannot chain** on the platform. **Action slash commands** own **TodoWrite** step tracking. Skills and workflows **describe** todo mapping for authors and executors—see `chat-orchestration.md`.

## Ref index (skill-relative)

| Path | Role |
|------|------|
| `refs/frontmatter-schemas.md` | Required YAML + naming |
| `refs/python-runtime.md` | Python 3.14+ and `audit_static.py` invocation |
| `refs/pre-ship-checklist.md` | Binary gate before create/rewrite writes |
| `refs/instruction-design.md` | Signal vs noise, layers |
| `refs/failure-patterns.md` | Audit finding taxonomy |
| `refs/extract.md` | Extract notes |
| `refs/chat-orchestration.md` | Tool and slash patterns |
| `refs/skill.template.md` | Skill skeleton |
| `refs/command.template.md` | Command skeleton |
| `refs/agent.template.md` | Agent skeleton |
| `refs/rule.template.md` | Rule skeleton |
| `refs/workflow.template.md` | Workflow skeleton |
| `refs/*.audit-rubric.md` | Per-type static + judgment rubrics |
| `refs/*.test-prompts.md` | Per-type probes |
| `refs/audit-output.template.md` | Audit report shape |
| `refs/test-output.template.md` | Test report shape |
| `refs/diff-output.template.md` | Diff report shape |
| `refs/actions/*.md` | Internal procedures per Action |

## Plugin commands (human map)

Design assist: `/context-engineer` → **Classify** + **Clarify** only; ends with **Next step (user):** pointing to one action slash.  
Actions: see **Actions** table above—each command file is a black box that names this skill + Action id only.

## Invocation

- **Cursor:** `/context-engineer` and `/context-engineer-*` as installed from the plugin.
- **Claude Code:** `/context-eng-hero:context-engineer` and `/context-eng-hero:context-engineer-*`.
