# execute-handoff

**Owner:** Slice freeze mint/fail and the compact `execute-slice.yaml` 5-field kernel for future Execute.

**Load when:** Freezing a selected slice (`--freeze-slice` / NL “freeze this slice”); reading handoff after Plan.

**Does not:** Implement `rr-execute`. Does not invent release/version bundling this pass. Does not require perfect architecture (draft allowed).

## Freeze unit

Primary Plan freeze = **selected story/phase slice**, not the whole PRD. Whole-PRD freeze = optional structure lock only.

## Mint (`execute-slice.yaml`)

Skill writes `refs/planning/output-formats.md` kernel:

| Kernel field | Meaning |
|--------------|---------|
| **Why** | Outcome justification for this slice |
| **Capabilities** | What this slice delivers |
| **Constraints** | Hard limits from spine/deltas/AC |
| **Non-goals** | Explicit exclusions for this slice |
| **Success signal** | Observable pass/fail |

Plus **pins:** requirement ids, parents, delta paths, `architecture_rev` (may be `draft`), AC refs.

Stamp `plan/status.yaml` `slice:` (`refs/planning/baselines.md`).

## Fail freeze when

| Condition | Action |
|-----------|--------|
| Smell-fail AC without explicit hold | Refuse |
| Effort without architecture ([system-design.md](system-design.md)) | Refuse |
| Slice shrinks/deletes the full requirement table | Refuse — selection is `_status_:` only |
| Product AC written as test code | Refuse — AC stays WWAS product pass/fail |
| Market re-debate | Route to `rr-discovery` |

## Draft-allowed

Architecture spine may be `draft` on freeze. Block only on **broken obligations** (existing unfreeze classify). Quiet unfreeze while refining standing layer is forbidden — use conscious unfreeze / lock-target paths.

## Next Up

Future **Execute** consumes the kernel. No Execute skill in this redesign. Future **release/version** grouping may reference frozen slices — not designed here.

## Done-when

- Kernel five fields + pins present
- `slice:` stamped; deferred requirements still on PRD
- Fail conditions not violated
