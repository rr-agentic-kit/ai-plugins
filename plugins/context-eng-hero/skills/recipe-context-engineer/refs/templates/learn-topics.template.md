# Learn topics template

Build at **`learn-3-topics`** (internal working set for handover; do **not** chat-emit full report). Cap **7** topics. Only `skill_gap` rows default-selected. No transcript dump.

```markdown
# Learn topics: <skill-name>

## Context
- Path: `<plugin-relative/SKILL.md>`
- Failed action(s): `<action-id(s)>`
- Miss: <1–2 sentences>

## Tool/read economy

Inventory from the missed run / problem statement (not extra skill Reads). Feed findings into Topics as `friction:` evidence or Auto-dropped “economy: no gap”.

- Tools used: `<list>`
- Files Read: `<list>`
- Necessary?: `yes` \| `over-read` \| `invent`
- Token cut?: `<one line → topic id or none>`
- Interaction cut?: `<one line → topic id or none>`

## Topics

| Id | Class | Evidence | Missing locus | Proposed absorb | Confidence |
|----|-------|----------|---------------|-----------------|------------|
| T1 | skill_gap | <patch\|friction>: <excerpt/pointer> | <SKILL/ref/step> | step \| stop-rule \| ref \| anti-trigger \| probe \| readme-when \| batch \| read-budget | high \| med \| low |

(Only rows with Class = skill_gap are **selected** by default. Max 7 rows.)

## Auto-dropped

| Id | Class | Why dropped |
|----|-------|-------------|
| D1 | already_covered \| preference_oneoff \| env_tool | <one line> |

## Checkpoint

**Adequacy probe (internal, before handover write):** Would absorb of *only* the selected topics still miss an operational nuance the founder/human named? If yes → add topic or Auto-drop with reason — do not ship philosophy-only as complete.
```

**Class values:** `skill_gap` \| `preference_oneoff` \| `env_tool` \| `already_covered`.

**Absorb shapes:** `step` \| `stop-rule` \| `ref` \| `anti-trigger` \| `probe` \| `readme-when` \| `batch` \| `read-budget`.

**Evidence Signal (optional prefix):** `patch` \| `friction`.
