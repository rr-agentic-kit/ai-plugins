---
name: recipe-context-engineer
description: Classifies and designs agent context artifacts (skills, commands, rules, agents, workflows). Use when choosing artifact type, structuring definitions, auditing, fixing, or creating—not for ambient code review or repository-wide edits.
---

# Context engineer

## Purpose

Make **skills, commands, rules, agents, and workflows** discoverable, bounded, and safe to reuse—without mixing judgment workflows with high-risk edits.

**This skill is the orchestrator.** It intake → classifies → routes → acts → closes the loop. It never ends with "run a slash command next"—it asks, routes, and continues (or stops cleanly with **Next Up**).

## When to use

- Picking or narrowing **artifact type**
- **Auditing**, **fixing**, **creating**, **extracting**, **testing**, or **comparing** a scoped artifact file
- **Clarifying** outcome, audience, and failure modes before authoring
- Designing **contracts** (inputs, outputs, stop rules) and **progressive disclosure** (refs)

## When not to use

- Ad-hoc **production code review** with no artifact path
- **Ambient** "audit everything" without a declared target file
- Tasks that need **repo-wide** exploration without a scoped question—use an explore subagent at the user's direction first

## Shared refs

Load as needed (not all every turn):

| Ref | Use |
|-----|-----|
| `refs/ui-brand.md` | Stage banners, status symbols, liveness, **Next Up** block |
| `refs/gate-prompts.md` | AskQuestion patterns for routing and post-action menus |
| `refs/questioning.md` | Graceful intake; never block on REQUIRED lists |
| `refs/chat-orchestration.md` | TodoWrite, Task, platform constraints for authors |

## Orchestration loop

Every invocation follows this loop. Do not skip steps; compress only when the user message already satisfies them.

```
1. Intake   — read user message + open file/editor context
2. Classify — if artifact type unclear → one AskQuestion (max); see Classify + questioning.md
3. Route    — if action unclear → action-routing gate (gate-prompts.md)
4. Act      — Read and execute refs/actions/<action-id>.md inline; TodoWrite step ids from that ref
5. Close    — post-action routing gate (gate-prompts.md) or Next Up block (ui-brand.md)
```

**Intent seeding:** If the user message states an action ("audit this", "fix the skill", intent: audit), skip step 3 and jump to step 4.

**No deferral:** After step 5, if the user picks a follow-on option, re-enter the loop at step 4 for that action—do not tell them to type a command.

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

Before authoring, resolve (use `questioning.md`—ask, do not block):

1. **Outcome** — what changes in the world when this succeeds?
2. **Audience** — which runtime/human applies this?
3. **Failure mode** — what bad behavior must this block?

Use **AskQuestion** when choices are enumerable. For multi-step **implementation** across files, use TodoWrite step ids from the active action ref.

## Actions

| Action id | One-line outcome | Run |
|-----------|------------------|-----|
| create | New artifact from template + static + reflection + pre-ship | `refs/actions/create.md` |
| extract | Draft artifact + provenance from context | `refs/actions/extract.md` |
| audit | Static script + severity rubric (no edits) | `refs/actions/audit.md` |
| fix | Match existing intent; all FAILs + static + reflection + pre-ship | `refs/actions/fix.md` |
| redesign | Change outcome/scope + static + reflection + pre-ship; re-audit after | `refs/actions/redesign.md` |
| test | Behavior probe report | `refs/actions/test.md` |
| diff | Two-path tradeoff summary | `refs/actions/diff.md` |
| design | Inline write from classify/clarify when user requests file this turn | `refs/actions/design.md` |

Read and execute the **Run** ref for the active action; contracts (purpose, inputs, output, stop) live there—not in this table.

## Routing (fix vs redesign)

| Signal | Action |
|--------|--------|
| Audit verdict FAIL | **fix** + audit report |
| Test probe FAIL, same contract | **fix** + test report |
| Test FAIL / user story = wrong capability or outcome | **redesign** |
| User: add step, remove gate, change audience | **redesign** |
| User: wording, typo, violates own stop rule | **fix** |
| Extract → production with **resolved** open questions | **redesign** (first ship) or **fix** (polish only) |

When ambiguous → **fix-vs-redesign** gate (`gate-prompts.md`).

## Design assist (classify + clarify only)

When the user has not picked an action and is not asking for a file write:

1. Run **Classify** + **Clarify**
2. If action still unclear → **action-routing** gate
3. If they chose an action → execute that action ref

**Inline write:** When the user **explicitly requests writing a file** at an approved plugin-relative path this turn → **design** action (`refs/actions/design.md`), same write gates as create.

## Execution rules

- **Action ref is source of truth** for steps, Load list, and stop rules—do not invent steps outside the active ref.
- **TodoWrite:** On action execution, `merge: false` with one todo per step id in the action ref; mark `completed` before advancing.
- **Visual output:** Emit stage banner at action start (`ui-brand.md`); liveness before silent shell work.
- **Post-action:** Always run the matching post-*-routing gate or show **Next Up**—never end on a bare report.
