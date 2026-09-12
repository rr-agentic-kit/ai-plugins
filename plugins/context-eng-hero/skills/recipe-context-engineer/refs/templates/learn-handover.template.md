# Learn handover template

Emit at **learn-4-handover** from **approved** topics only. Write under the **user project** (prefer `docs/rr/LEARN-HANDOVER.<skill-name>.md` when `docs/rr/` exists, else project-root `LEARN-HANDOVER.<skill-name>.md`). Ephemeral—do not marketplace-ship; delete from the **user project** after absorb into **plugin source**.

**Anti-trigger:** Do **not** write beside runtime/cache `SKILL.md` (`~/.claude/plugins/cache/**` or installed copies).

```markdown
# LEARN-HANDOVER

## Target
- Path: `<plugin-source absolute or repo-relative/SKILL.md>` (**plugin source** — not cache)
- Type: skill | Skill+Ref
- Runtime/cache copies: **read-only** — never write or absorb there

## Miss
<≤3 sentences: what failed, what the human covered manually, and/or run friction (serial tools/Reads, invent-vs-procedure)>

## Approved topics

| Id | Locus | Absorb-as | Evidence |
|----|-------|-----------|----------|
| T1 | <path#step or section> | step \| stop-rule \| ref \| anti-trigger \| probe \| readme-when \| batch \| read-budget | <one-liner> |

## Rejected / deferred
- <id or topic>: <reason>

## Non-goals
- No project-domain rules (generic skill behavior only)
- <what learn/absorb must not change>
- Do not edit `~/.claude/plugins/cache/**` copies

## Incorporate hint
- Mode: **fix** | **redesign**
- Touch list: `<plugin-source paths to edit>`

---
Ephemeral. Written in user project. Delete after fix/redesign absorb into **plugin source**.
```

**Rules:** No full chat paste. No essay rationale sections. Approved table only—dropped classes stay out unless user forced them in. Handover file lives in the **user project**; absorb edits land only in **plugin source**.
