# execute-handoff

**Owner:** Slice freeze mint/fail and the compact `execute-slice.yaml` 5-field kernel for future Execute — pin-complete, obligation-citing, not PRD section coverage.

**Load when:** Freezing a selected slice (`--freeze-slice` / NL “freeze this slice”); reading handoff after Plan.

**Does not:** Implement `rr-execute`. Does not invent release/version bundling this pass. Does not treat draft architecture rev as “no architecture yet.”

## Success metric (north-star)

After freeze, a future Execute agent can start **fused code+test** without inventing stack, feature mechanism, or cost-driving UX shape — and RICE Effort that selected this slice was not inflated by Happy-Path Effort. Pass = Effort honesty + pin-complete kernel. Fail = section-coverage theater.

## Freeze unit

Primary Plan freeze = **selected story/phase slice**, not the whole PRD. Whole-PRD freeze = optional structure lock only.

## Mint (`execute-slice.yaml`)

Skill writes `refs/planning/output-formats.md` kernel:

| Kernel field | Meaning |
|--------------|---------|
| **Why** | Outcome justification for this slice |
| **Capabilities** | What this slice delivers |
| **Constraints** | Hard limits that **cite** spine/delta obligations (mechanism + UX-shape when UI-facing) — not only product goals |
| **Non-goals** | Explicit exclusions for this slice |
| **Success signal** | Observable pass/fail |

Plus **version stamps** (`track`, `docs`, `product` from Plan phase status at freeze) and **pins:** requirement ids, parents, `delta_paths` (existing files), `architecture_rev` (may be `draft`), AC refs.

Stamp `plan/status.yaml` `slice:` (`refs/planning/baselines.md`).

Execute starts fused code+test from this kernel — **no separate tech-planning step**. Obligation break → existing classify-the-change / unfreeze.

## Thin selection at freeze

Prefer a **buildable kernel** over a wide selected set that only looks complete on paper. Shorter Plan cycles are fine when:

- Selected leaves have Decision + Effort drivers (+ UX-shape when UI-facing)
- Deferred work stays on the full P1–P3 table (`_status_:`) and is named in **Non-goals**
- Kernel stays pin-complete — refuse **doc-only** slices that lack Decision / Effort drivers / UX-shape

Thin ≠ hollow. Narrow selection + honest defer beats breadth without mechanism.

## Fail freeze when

| Condition | Action |
|-----------|--------|
| Smell-fail AC without explicit hold | Refuse |
| Effort without architecture or without **Effort drivers** ([system-design.md](system-design.md)) | Refuse |
| UI-facing selected feature without **UX-shape** (pure backend must say `n/a` + reason) | Refuse |
| Selected capability with no spine/delta **Decision** + Effort drivers — **draft rev ≠ missing** | Refuse |
| Empty `delta_paths` for a selected capability that needs mechanism | Refuse |
| Constraints that only restate product goals (no delta/spine obligations) | Refuse |
| Slice shrinks/deletes the full requirement table | Refuse — selection is `_status_:` only |
| Doc-only / hollow thin slice (selected without Decision / Effort drivers / UX-shape) | Refuse — thin kernel must still be pin-complete |
| Product AC written as test code | Refuse — AC stays WWAS product pass/fail |
| Market re-debate | Route to `rr-discovery` |

## Draft ≠ missing

Architecture spine may be `architecture_rev: draft` on freeze. That does **not** mean “no architecture.” Block when selected capabilities lack Decision + Effort drivers (and UX-shape when UI-facing). Quiet unfreeze while refining standing layer is forbidden — use conscious unfreeze / lock-target paths.

## Next Up

Future **Execute** consumes the kernel. No Execute skill in this redesign. Future **release/version** grouping may reference frozen slices — not designed here.

## Done-when

- Kernel five fields + version stamps (`track` / `docs` / `product`) + pins present; `delta_paths` resolve to files
- Constraints cite delta/spine obligations (mechanism + UX-shape when UI-facing)
- `slice:` stamped; deferred requirements still on PRD
- Fail conditions not violated
