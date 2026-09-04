# cascade

**Owner:** Top-down discovery level order (executive-summary → MRD → BRD), inheritance/narrowing, freeze/remap, per-level gates, and BRD → business-case handoff.

## Pre-cascade: project posture

Before executive-summary, run [project-posture.md](project-posture.md). Done: that ref's persist condition.

## Ideation gate

If the problem space has no concrete idea yet → run [ideation.md](ideation.md) before L1 compose. Else skip. Persist conditional artifacts when produced.

## Level order

Fixed sequence — never skip a level in `standard`/`deep` depth (`shallow` trims per [input-resolution.md](input-resolution.md)):

```
1. executive-summary  — posture, vision, problem, why, North Star
2. mrd                — market context
3. brd                — business requirements → freeze + business-case
```

PRD is **Plan** (`rr-planner`) — not this cascade. Item identity: [doc-standards/item-schema.md](../../../refs/planning/doc-standards/item-schema.md). Mechanism overflow → `tech.md` ([output-formats.md](../../../refs/planning/output-formats.md)).

```mermaid
flowchart TD
  ES["ES-n"] --> MRD["MRD-n.m"]
  MRD --> BRD["BRD-n.m"]
  BRD --> BC["business-case.yaml"]
```

## Inheritance model

| Level | Inherits from | Narrows to |
|-------|---------------|------------|
| executive-summary | user input, conversation, confirmed `project_posture` | strategic vision, problem framing, posture, metrics, defensibility |
| mrd | executive-summary | market segments, competition, dual-method sizing, Kano needs |
| brd | executive-summary + mrd | business objectives, Power×Interest stakeholders, capabilities/deps |

### Inheritance rules

1. **No contradiction** — child facts align with parent facts. Conflict → [goal-anchor.md](goal-anchor.md).
2. **No orphan items** — [doc-standards/item-schema.md](../../../refs/planning/doc-standards/item-schema.md); verified by `validate_planning.sh`.
3. **Explicit narrowing** — record narrowing as a decision in `session-state.json`.
4. **Unknown vs off-level** — [note-sessions.md](note-sessions.md). Feature/RICE detail → Plan notes, not Discover Musts.

## Per-level discovery flow (skill-inline)

For each level in `cascade_levels`:

1. Load `doc-standards/<level>.md` and [doc-standards/item-schema.md](../../../refs/planning/doc-standards/item-schema.md).
2. On level entry: re-decision sweep ([decision-ledger.md](../../../refs/planning/decision-ledger.md)); sidecar load ([note-sessions.md](note-sessions.md)).
3. Load [goal-anchor.md](goal-anchor.md) for the entire discovery pass.
4. Present inherited facts. **Executive-summary only:** premise test ([expert-panel.md](expert-panel.md)).
5. Ask for gaps. Mint ledger rationales for ranked leaves ([decision-ledger.md](../../../refs/planning/decision-ledger.md)).
6. After every Q&A: [note-sessions.md](note-sessions.md) + `raw-history`. On reflect → [proactivity.md](proactivity.md). Strategy/GTM on demand: [strategy-lenses.md](strategy-lenses.md), [gtm-framing.md](gtm-framing.md).
7. Accumulate `level_facts`. Invoke compose ([contracts.md](../../../refs/planning/contracts.md)).
8. **Humanize** — after compose draft receipt, run [compose-prose.md](compose-prose.md) before treating persist complete. Prune notes after final write. Dirty challenge attestation if needed ([baselines.md](../../../refs/planning/baselines.md)).
9. Clarification loop ([contracts.md](../../../refs/planning/contracts.md)).
10. Refresh `item_registry` from `items.json`. Gate 3 static ([success-criteria.md](../../../refs/planning/success-criteria.md)).
11. Gate 6 then Gate 7. On Gate pass: **freeze** this level. After **BRD** freeze: [business-case-handoff.md](business-case-handoff.md).

## Stop and resume

User may stop ("stop", "pause", "done for now"):

1. Leave composed files on disk (drafts until freeze). Do not run pre-save.
2. Checkpoint `session-state.json` ([output-formats.md](../../../refs/planning/output-formats.md)).
3. Set `checkpoint.status: paused` with `current_level`.

Resume: `rr-discovery --resume --output-dir <same-dir>`. Load checkpoint; sweep; continue.

## Per-level completion gates

| Gate | Owner | Done when |
|------|-------|-----------|
| 1 Section coverage | this file | Every required section has a resolved fact or explicit assumption `blocking: false` |
| 2 Goal anchor | [goal-anchor.md](goal-anchor.md) | That ref's level-complete conditions |
| 3 Inheritance integrity | [success-criteria.md](../../../refs/planning/success-criteria.md) | Static script + judgment list |
| 4 Compose acceptance | [contracts.md](../../../refs/planning/contracts.md) + doc-standard + [compose-prose.md](compose-prose.md) | Compose ok/accepted partial **and** humanize claim check passed |
| 5 Proactivity | [proactivity.md](proactivity.md) | `standard`/`deep` discovery-time stop |
| 6 Stage-exit | [blind-spots.md](blind-spots.md) | ES/MRD/BRD row only (`in_scope` + `inherit_check`) |
| 7 Viability | [expert-panel.md](expert-panel.md) | Binding at ES/MRD; advisory at BRD |

## Freeze and remap

| Event | Rule |
|-------|------|
| First compose of a level | Dense sibling IDs. Frontmatter `doc_rev: "?"`. |
| Cascade gates pass | Add level to `frozen_levels`. Mint `status.yaml` per [baselines.md](../../../refs/planning/baselines.md). Freeze does **not** wait on challenge-clean. |
| BRD gates pass (`proceed` / `proceed-with-conditions`) | Run [business-case-handoff.md](business-case-handoff.md): write `business-case.yaml`, stamp `discovery_complete: true`. |
| Gate 7 `hold` / `pivot` / `kill` | Do **not** mint `discovery_complete`. Follow expert-panel ladder. |
| Later insert on frozen level | Append next integer. |
| Explicit re-compose of frozen level | Allowed; humanize via rewrite path; remap children. |
| `--resume` | Continue from `item_registry` / checkpoint. |
| `--change` | Section + target; skill classifies patch vs redirect. |

## Advancing vs stopping

| Condition | Action |
|-----------|--------|
| All gates pass; queue empty | Freeze; mint docs patch; advance (or handoff after BRD) |
| Pending clarifications / gate gaps | Surface question → re-discover / re-compose |
| Gate 7 `hold` / `pivot` / `kill` | Verdict ladder — no discovery_complete |
| Open re-decision queue | Drain before freeze |
| User pause | Checkpoint; skip pre-save |

## Session state

Persist schema: [output-formats.md](../../../refs/planning/output-formats.md). Skill updates `level_facts`, `item_registry`, `frozen_levels`, `project_posture`, `viability[]`, `note_sessions`, `discovery_complete`, `composed_docs`. Compose writes draft cascade docs + `items.json`; skill finalizes prose via [compose-prose.md](compose-prose.md). Skill writes ledger, status, and `business-case.yaml`.
