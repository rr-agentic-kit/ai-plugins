# Instruction design (context artifacts)

Principles for **skills**, **commands**, **agents**, **rules**, **workflows**, **Skill+Ref** packs, and **ref files**. Read at draft steps in create/fix/redesign/design/extract actions.

## Signal vs noise

- **Signal**: constraints the agent cannot infer (policy, gates, exact formats, stop rules).
- **Noise**: generic encouragement, repeated restatements, prose that duplicates co-loaded refs.

Cut noise until every paragraph changes behavior or discovery. If parent SKILL / action Ref index co-loads file X with this ref, do not restate X's constraints here.

## Forcing function

When a choice is enumerable, prefer **AskQuestion** over open-ended asks.

When work spans verifiable steps: action commands → **TodoWrite** with ids from `refs/actions/<verb>.md`; workflows → `todo_id` per step. Design-only skill invoke → no forced todo list unless user chose an action.

## Layer separation

| Layer | Holds |
|-------|--------|
| **Skill** | Judgment, classification, reusable procedure, progressive disclosure |
| **Skill+Ref** | Invariant procedure in SKILL; variant/detail in `refs/`—one hop |
| **Ref file** | Skill-private constraints for one subtask; loaded via parent SKILL / action Ref index |
| **Command** | Slash contract: inputs, delegation to skill **Action**, output shape |
| **Refs (orchestrator)** | Templates, rubrics, checklists—Read at the step that branches |

Link the canonical ref once; do not duplicate policy in three places.

## Degrees of freedom

| Freedom | When | Shape |
|---------|------|-------|
| **Low** | Fragile, irreversible, safety-critical | Exact steps, stop rules, scripts |
| **Medium** | Repeatable workflow with known forks | AskQuestion, bounded retries |
| **High** | Review, design, classification | Outcomes + anti-patterns + examples |

Default **high** for judgment skills; **low** only where mistakes are costly.

## Progressive disclosure (one level deep)

SKILL.md (or command body) → `refs/` (and `scripts/` **executed**, not pasted). Refs do **not** chain to other refs.

See `helper-cli.md` when the skill folder includes `scripts/`.
