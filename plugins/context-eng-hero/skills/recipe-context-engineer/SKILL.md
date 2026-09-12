---
name: recipe-context-engineer
description: Use when designing, auditing, fixing, or creating skills, commands, rules, agents, or workflows—not ambient code review.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash(python3 scripts/audit_static.py*)
---

# Context engineer

## Purpose

Make **skills, commands, rules, agents, and workflows** discoverable, bounded, and safe to reuse—without mixing judgment workflows with high-risk edits.

## When to use

- Picking or narrowing **artifact type** (including Skill+Ref and ref file)
- **Auditing**, **fixing**, **creating**, **extracting**, **testing**, **comparing**, or **learning from a live run miss (patch or friction)** on a scoped artifact file
- **Clarifying** outcome, audience, and failure modes before authoring

## When not to use

- Ad-hoc **production code review** with no artifact path
- **Ambient** "audit everything" or "improve this skill" without a declared target file or live miss
- Repo-wide exploration without a scoped question

## Procedure

Every invocation follows this loop. Compress steps only when the user message already satisfies them.

```
1. Intake   — read user message + editor context; Read `refs/disambiguation.md`
2. Classify — if type unclear → one AskQuestion; see `refs/classify.md`
3. Route    — if action unclear → `refs/gate-prompts.md` action-routing
4. Advise   — `refs/advisory.md` for create, design, extract, fix, redesign; skip audit, test, diff, learn
5. Act      — Read and execute `refs/actions/<action-id>.md`; TodoWrite step ids from that ref
6. Close    — `refs/close-contract.md` + gate or `refs/ui-brand.md` Next Up
```

**Intent seeding:** User states an action ("audit this", "fix the skill", "learn from this miss") → skip step 3, go to step 5.

**No deferral:** After step 6, if the user picks a follow-on, re-enter at step 5—do not tell them to type a command.

## Ref index

| Ref | Read when |
|-----|-----------|
| `refs/classify.md` | Step 2; action classify steps |
| `refs/disambiguation.md` | Step 1 |
| `refs/questioning.md` | Intake gaps; clarify steps |
| `refs/advisory.md` | Step 4 |
| `refs/gate-prompts.md` | Routing and post-action gates |
| `refs/ui-brand.md` | Action banners and Next Up |
| `refs/close-contract.md` | Step 6; template follow-ups |
| `refs/chat-orchestration.md` | Authoring workflows/commands |
| `refs/skill-invocation.md` | Authoring skills |
| `refs/readme-spec.md` | Skill folder README (bidirectional spec) |
| `refs/templates/readme.template.md` | Extract/create skill README |
| `refs/lexicon-spec.md` | Plugin/skill ACRONYMS + GLOSSARY companions |
| `refs/templates/acronyms.template.md` | Create/harvest ACRONYMS.md |
| `refs/templates/glossary.template.md` | Create/harvest GLOSSARY.md |
| `refs/helper-cli.md` | Target has `scripts/` |
| `refs/template-required-map.md` | Drafting; reflection evidence |
| `refs/rubrics/` | Type judgment rubrics (audit, reflection) |
| `refs/templates/` | Artifact and output templates |
| `refs/prompts/` | Behavior probe prompts (test action) |

## Exit conditions

| Condition | Exit behaviour |
|-----------|----------------|
| Path unresolvable after 2 AskQuestion rounds | Stop. "Cannot proceed without a target path." |
| Action type unresolvable after 1 AskQuestion | Default to design-assist; state default |
| Contradiction unresolvable after 1 round | "Conflicting signals: [A] vs [B]. Rephrase and re-invoke." Stop. |
| Write gate FAIL after 2 revision cycles | Draft-only in chat; "Manual review required." Stop write. |
| Bash unavailable (`audit_static.py` missing) | **Audit:** `STATIC SKIPPED`; continue judgment. **Write paths:** block until static PASS or user accepts draft-only. |
| Advisory produces 0 gaps | Skip Advise silently |

## Actions

| Action id | Outcome | Run |
|-----------|---------|-----|
| create | New artifact from template + write gates | `refs/actions/create.md` |
| extract | Draft + provenance from context | `refs/actions/extract.md` |
| audit | Static + rubric report (no edits) | `refs/actions/audit.md` |
| fix | Minimal edits for existing intent | `refs/actions/fix.md` |
| redesign | Change outcome/scope + write gates | `refs/actions/redesign.md` |
| learn | Approved gap package from a live run miss—patch or friction (no skill edits) | `refs/actions/learn.md` |
| test | Behavior probe report | `refs/actions/test.md` |
| diff | Two-path tradeoff summary | `refs/actions/diff.md` |
| design | Inline write from classify/clarify | `refs/actions/design.md` |

**Routing (fix vs redesign):** `refs/classify.md` **Routing** section.

**README ↔ SKILL routing:** `refs/classify.md` **README routing** section.

**Design assist:** Classify + Clarify until user requests file write → **design** action.

## Execution rules

- **Action ref is source of truth** for steps, staged Reads, and stop rules.
- **TodoWrite:** `merge: false`; one todo per step id; mark `completed` before advancing.
- **Visual output:** Stage banner at action start (`ui-brand.md`).
- **Post-action:** `close-contract.md`—never end on a bare report.
