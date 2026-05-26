# Communication contract + Role framing (exhaustive)

**Load for:** user-global **design** (full interview); **review** deep-dive on Communication or Role; **fix** when symptoms map to these sections (gap dimensions only).

**Policy:** No whole-section skip on **design**. Each dimension: resolved bullets **or** explicit “N/A — &lt;reason&gt;”. **Within-section pause** allowed via checkpoints (see below)—not one sitting required.

Use **AskQuestion** until each dimension below is settled. Pre-fill from the user’s initial prompt when possible.

---

## Session control (checkpoints)

**Exhaustive on design** means every dimension gets bullets or `N/A — reason` before write—but **not** necessarily in one sitting.

**Checkpoint groups:**

| Group | Covers |
|-------|--------|
| **A** | Communication contract table (all rows) |
| **B** | Role framing table (all rows) |

After each group, emit an **Interview state** block:

```text
scope: user
path: <agreed path>
group_done: A | B
dimensions_pending: [<dimension names>]
draft_bullets_so_far: <short summary>
```

**Resume:** user re-runs `/static-memory-design` with “resume static memory interview” or pastes the state block; continue **pending dimensions only**—do not restart settled groups.

**Pause offer:** after each group, **AskQuestion:** Continue now / Pause and resume later.

**Review/fix:** only implicated dimensions; no full re-interview unless deep-dive.

---

## Communication contract

| Dimension | Capture as imperative, testable bullets |
|-----------|----------------------------------------|
| **Response shape** | Lead with answer vs narrative; when to use headings/lists |
| **Length & density** | Terse vs thorough; max paragraphs; typical code snippet size |
| **Tone** | Peer / teacher / challenger; formality level (see **Pushback** for when to challenge) |
| **Hedging & confidence** | State uncertainty explicitly; ban fake confidence |
| **Pushback** | When to challenge framing vs execute as stated (cross-link **Directness**, **When user is wrong** in Role) |
| **Directness** | Blunt vs diplomatic; call out bad framing immediately vs after answer |
| **Context before action** | Execute prompt as stated vs read repo/docs/ask first; when to refuse “guess and code” |
| **Alternatives & initiative** | When to propose unprompted options vs single recommendation; max options per turn |
| **Questions** | When to AskQuestion vs assume; max clarifying questions per turn |
| **Prose quality** | Complete sentences; filler phrases to ban (user list) |
| **Formatting** | Code citations; bold/backtick rules; mermaid/diagrams when |
| **Engagement** | No sycophancy; no forced follow-ups at end of replies |
| **Language** | Primary language; jargon level; bilingual rules if any |

---

## Role framing

| Dimension | Capture as imperative, testable bullets |
|-----------|----------------------------------------|
| **Persona** | Title/expertise (e.g. principal architect) |
| **Relationship** | Senior to user vs collaborator (see **Interaction stance**) |
| **Interaction stance** | Teacher (explain why) vs technical lead (decide + tradeoffs) vs executor (follow rules/spec) |
| **Domain strengths** | Stacks/domains to lean on |
| **Decision style** | Tradeoffs A/B with costs; ownership cost |
| **Scope of advice** | Architecture vs implementation vs both |
| **Challenge & correction** | When user is wrong: stop vs redirect; challenge problem framing vs accept framing (cross-link **Pushback**, **Directness**) |
| **When user is wrong** | Call out immediately vs gentle redirect |
| **Non-goals of persona** | What this role does **not** do |
| **Seniority assumption** | Skip basics yes/no; what to never explain |

---

## Synthesis rules

1. Convert answers to **imperative, testable** bullets (micro-examples: `effective-writing.md`).
2. Prefer concrete negatives (“Do not open with Great question”) over vague positives (“be helpful”).
3. Deduplicate overlapping dimensions (tone vs pushback vs directness vs challenge)—one home per rule; cross-reference elsewhere.
4. If combined comm+role would exceed ~60 lines in root file, offer `@~/.claude/communication-role.md` import—user must approve; content stays exhaustive, root stays scannable.
5. Target ~100 lines total user-global **except** comm/role may use import split or ~60–80 lines inline with user opt-in.

---

## Review deep-dive triggers

Default **Deep-dive** (not Accept) when section is missing, &lt;3 testable bullets, or only vague one-liners (“be concise”, “act as expert”).
