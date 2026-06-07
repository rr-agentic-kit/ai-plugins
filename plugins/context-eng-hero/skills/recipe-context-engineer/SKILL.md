---
name: recipe-context-engineer
description: Classifies and designs agent context artifacts (skills, commands, rules, agents, workflows). Use when choosing artifact type, structuring definitions, auditing, fixing, or creating—not for ambient code review or repository-wide edits.
allowed-tools: Read, Write, Edit, Bash(python3 scripts/audit_static.py*)
---

# Context engineer

## Purpose

Make **skills, commands, rules, agents, and workflows** discoverable, bounded, and safe to reuse—without mixing judgment workflows with high-risk edits.

**This skill is the orchestrator.** It intake → classifies → advises → routes → acts → closes the loop. It never ends with "run a slash command next"—it asks, routes, and continues (or stops cleanly with **Next Up**).

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
| `refs/disambiguation.md` | Signal classification, default assumptions, retry caps—load at intake |
| `refs/advisory.md` | Hidden-requirements scan and tradeoff presentation—load before design actions |
| `refs/ui-brand.md` | Stage banners, status symbols, liveness, **Next Up** block |
| `refs/gate-prompts.md` | AskQuestion patterns for routing and post-action menus |
| `refs/questioning.md` | Graceful intake; never block on REQUIRED lists |
| `refs/chat-orchestration.md` | TodoWrite, Task, platform constraints for authors |

## Procedure

Every invocation follows this loop. Do not skip steps; compress only when the user message already satisfies them.

```
1. Intake   — read user message + open file/editor context; load disambiguation.md
2. Classify — if artifact type unclear → one AskQuestion (max); see Classify + questioning.md
3. Route    — if action unclear → action-routing gate (gate-prompts.md)
4. Advise   — surface hidden requirements + present tradeoffs (refs/advisory.md)
             Run for: create, design, extract, fix, redesign
             Skip for: audit, test, diff (diagnosis-only; no design decisions)
5. Act      — Read and execute refs/actions/<action-id>.md inline; TodoWrite step ids from that ref
6. Close    — post-action routing gate (gate-prompts.md) or Next Up block (ui-brand.md)
```

**Advise step rules:**

- Run hidden-requirements scan from `refs/advisory.md` for the detected artifact type
- For each gap: state it, explain why in 1 sentence, offer ≥2 options with one-line pros/cons each
- For design choices with no clear winner: present tradeoff table — do NOT default silently
- Flag scope problems (two unrelated outcomes, audience mismatch) before proceeding
- Cap: surface at most 3 advisory items per turn; critical and major gaps first
- Skip if user message already addresses all hidden requirements

**Intent seeding:** If the user message states an action ("audit this", "fix the skill", intent: audit), skip step 3 and jump to step 5.

**No deferral:** After step 6, if the user picks a follow-on option, re-enter the loop at step 5 for that action—do not tell them to type a command.

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

Before authoring, resolve in two phases (ordering fixed: gather what you want *before* surfacing what you may have missed):

### Gather

Use `questioning.md`—ask, do not block:

1. **Outcome** — what changes in the world when this succeeds?
2. **Audience** — which runtime/human applies this?
3. **Failure mode** — what bad behavior must this block?

Use **AskQuestion** when choices are enumerable. For multi-step **implementation** across files, use TodoWrite step ids from the active action ref.

### Advise

After Gather, run the advisory scan from `refs/advisory.md`:

- Surface hidden requirements and tradeoffs for the detected artifact type
- Present gaps and options before Act; do not proceed to authoring with unresolved critical gaps unless user explicitly defers
- Skip silently if the user message already addresses all hidden requirements (0 gaps)

## Disambiguation

Apply inline; full protocol in `refs/disambiguation.md` (loaded at Intake).

| Signal | Treatment |
|--------|-----------|
| **Missing** | `questioning.md` routing (unchanged) |
| **Ambiguous** | State assumption inline, proceed — do NOT ask |
| **Contradictory** | Name both signals → one AskQuestion → if unresolved, default to more conservative action (fix < redesign < create) and state it |
| **Unclear** | Reduce to enumerable set via AskQuestion; if non-enumerable, one open-text ask, then proceed |

Retry cap: 2 rounds max per ambiguity class; beyond cap → see Exit conditions.

## Exit conditions

Skill-level stops (visible at intake; action refs may add local rules):

| Condition | Exit behaviour |
|-----------|----------------|
| Path unresolvable after 2 AskQuestion rounds | Stop. "Cannot proceed without a target path." |
| Action type unresolvable after 1 AskQuestion | Default to design-assist only; state default |
| Contradiction unresolvable after 1 round | "Conflicting signals: [A] vs [B]. Rephrase and re-invoke." Stop. |
| Write gate FAIL after 2 revision cycles | Emit draft-only in chat; "Manual review required." Stop write. |
| Bash unavailable (`audit_static.py` missing) | Emit `STATIC SKIPPED` with reason; continue to judgment |
| Advisory produces 0 gaps | Skip Advise step silently; proceed to Act |

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

1. Run **Classify** + **Clarify** (Gather then Advise)
2. If action still unclear → **action-routing** gate
3. If they chose an action → execute that action ref

**Inline write:** When the user **explicitly requests writing a file** at an approved plugin-relative path this turn → **design** action (`refs/actions/design.md`), same write gates as create.

## Execution rules

- **Action ref is source of truth** for steps, Load list, and stop rules—do not invent steps outside the active ref.
- **TodoWrite:** On action execution, `merge: false` with one todo per step id in the action ref; mark `completed` before advancing.
- **Visual output:** Emit stage banner at action start (`ui-brand.md`); liveness before silent shell work.
- **Post-action:** Always run the matching post-*-routing gate or show **Next Up**—never end on a bare report.
