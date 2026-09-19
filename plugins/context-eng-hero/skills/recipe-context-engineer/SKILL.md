---
name: recipe-context-engineer
description: Hardens scoped skills, commands, rules, agents, and workflows via gated design and write loops—slash or explicit Read only.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash(python3 scripts/audit_static.py*), Bash(python3 scripts/render_ce_report.py*), Task, AskQuestion, TodoWrite
---

# Context engineer

## Purpose

Make **skills, commands, rules, agents, and workflows** discoverable, bounded, and safe to reuse—without mixing judgment workflows with high-risk edits.

## When to use

- Picking or narrowing **artifact type** (including Skill+Ref and ref file)
- **Auditing**, **improving** (compliance + opportunities + absorb), **fixing**, **creating**, **extracting**, **testing**, **comparing**, or **learning from a live run miss (patch or friction)** on a scoped artifact file
- **Clarifying** outcome, audience, and failure modes before authoring

## When not to use

- Ad-hoc **production code review** with no artifact path
- **Ambient** "audit everything" or "improve this skill" without a declared target file or live miss
- Repo-wide exploration without a scoped question

## Procedure

Every invocation follows this loop. Compress steps only when the user message already satisfies them.

```
1. Intake   — read user message + editor context; Read `refs/disambiguation.md`
            Done when: disambiguation loaded; path resolved or Exit stop fired
2. Classify — if type unclear → one AskQuestion; see `refs/classify.md`
            Done when: type stated (or assumption noted once)
3. Route    — if action unclear → `refs/gate-prompts.md` action-routing
            Done when: action id known (or design-assist default stated)
4. Advise   — `refs/advisory.md` for create, design, extract, fix, redesign; skip audit, audit-redesign, improve, test, diff, learn
            Done when: gaps listed or Advise skipped per action table
5. Act      — Read and execute `refs/actions/<action-id>.md`; TodoWrite step ids from that ref (or single-shot N/A when action allows)
            Done when: action ref steps complete per that ref's Stop/Done when
6. Close    — `refs/close-contract.md` + gate or `refs/ui-brand.md` Next Up
            Done when: matching post-*-routing gate or Next Up emitted
```

**Intent seeding:** User states an action ("audit this", "fix the skill", "learn from this miss", `--improve` / "improve this `<path>`") → skip step 3, go to step 5. `--improve` / improve-this still requires a declared path.

**No deferral:** After step 6, if the user picks a follow-on, re-enter at step 5—do not tell them to type a command.

## Ref index

Draft/gates/probes/templates/rubrics load only from the **action** Ref index (`refs/actions/<id>.md`)—that table is SoT for staged Reads. Do **not** treat the Authoring table below as always-on.

### Orchestration (always)

| Ref | Read when |
|-----|-----------|
| `refs/classify.md` | Step 2; action classify steps |
| `refs/disambiguation.md` | Step 1 |
| `refs/questioning.md` | Intake gaps; clarify steps (incl. skill-UX gate); **Delivery channels** |
| `refs/advisory.md` | Step 4 |
| `refs/gate-prompts.md` | Routing, skill-ux-delivery, and post-action gates |
| `refs/ui-brand.md` | Action banners and Next Up |
| `refs/close-contract.md` | Step 6; template follow-ups |

### Authoring (action Ref index only)

Load these only when the active action Ref index names them (create/design/extract/fix/redesign draft paths)—not on audit / improve / test / learn / diff alone.

| Ref | Read when |
|-----|-----------|
| `refs/chat-orchestration.md` | Authoring workflows/commands |
| `refs/design/design-core.md` | Draft/plan: shared principles + type picker |
| `refs/design/skill.md` | Authoring skills (invoke + allowed-tools) |
| `refs/design/command.md` | Authoring commands |
| `refs/design/agent.md` | Authoring plugin agents |
| `refs/frontmatter-schemas.md` | Frontmatter field SoT (draft/gates) |
| `refs/readme-spec.md` | Skill folder README (bidirectional spec) |
| `refs/lexicon-spec.md` | Plugin/skill ACRONYMS + GLOSSARY companions |
| `refs/helper-cli.md` | Target has `scripts/` |
| `refs/template-required-map.md` | Drafting; reflection evidence |

## Exit conditions

| Condition | Exit behaviour |
|-----------|----------------|
| Path unresolvable after 2 AskQuestion rounds | Stop. "Cannot proceed without a target path." |
| Action type unresolvable after 1 AskQuestion | Default to design-assist; state default |
| Contradiction unresolvable after 1 round | "Conflicting signals: [A] vs [B]. Rephrase and re-invoke." Stop. |
| Write gate FAIL after 2 revision cycles | Draft-only in chat; "Manual review required." Stop write. |
| Bash unavailable (`audit_static.py` missing) | **Audit:** `STATIC SKIPPED`; continue judgment. **Write paths:** block until static PASS or user accepts draft-only. |
| Advisory produces 0 gaps | Skip Advise silently |
| No matching ref for a required Load | Use SKILL invariant + this Exit table; do **not** invent a ref. Stop if the action cannot proceed without that ref. |

## Actions

| Action id | Outcome | Run |
|-----------|---------|-----|
| create | New artifact from template + write gates | `refs/actions/create.md` |
| extract | Draft + provenance from context | `refs/actions/extract.md` |
| audit | Static + rubric report (no edits) | `refs/actions/audit.md` |
| audit-redesign | Ranked improvement opportunities (no edits) | `refs/actions/audit-redesign.md` |
| improve | Parallel audits → merge → fix then redesign under write gates | `refs/actions/improve.md` |
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
- **TodoWrite:** `merge: false`; one todo per step id; mark `completed` before advancing. **Single-shot N/A** (one line) allowed for `audit`, `audit-redesign`, `diff`, and `test`; required for write paths and `improve`. Under **improve** nested apply: only `improve-1…6` todos — do not spawn nested `fix-*` / `redesign-*` lists (`actions/improve.md` Stop).
- **Visual output:** Stage banner at action start (`ui-brand.md`).
- **Post-action:** `close-contract.md`—never end on a bare report.
- **Question delivery:** Prefer AskQuestion; text-mode same options (no stall) — SoT `refs/questioning.md` **Delivery channels**.
- **Skill UX clarify:** On create/design skills, resolve **skill-ux-delivery** after invoke mode; draft wires authored Delivery channels (or one-line N/A) into the new artifact — maintain contract for dogfooded skills.
- **Authored Delivery channels:** When this skill authors skills/commands/workflows that use AskQuestion, those artifacts must include the same fallback rule (`design/design-core.md`).
