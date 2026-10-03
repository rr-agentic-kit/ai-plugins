# intake-absorb (planner)

**Audience:** `rr-planner` when `payload.action: intake`. Wrapper over shared `refs/planning/intake.md` for stages **1–4** only.

**Does not:** Code; mint execute beyond stub sync; run `--feature` / `--adhoc`; `Read` builder `refs/*`; waive stage 3 cohesion/challenge.

## Flow

```
Read refs/planning/intake.md
  → situate (stage 1)
  → docs absorb (stage 2)
  → challenge / impact if needed (stage 3)
  → select / slice posture (stage 4)
  → sync open-task stubs (registry / thin {NNNN} placeholders when selection minted)
  → stop before code; Next Up builder stages 5–7
```

## Stages

| Stage | Planner work |
|-------|----------------|
| **1 Situate** | Match class + evidence; report stage reached / first block |
| **2 Docs absorb** | PRD (± WWAS) + feature-delta when mechanism/Effort/UX-shape required; selection `_status_`. Prefer `--change` / dual-lens paths already owned by Plan when Effort sitting needed. |
| **3 Challenge / impact** | If not cohesive with frozen Discover or standing constitution/ADR → cheaper-first + challenge / Discover reopen / baselines Ask / risk-accept. **Block** advance until resolved. Mark downstream impact per `refs/planning/baselines.md`. |
| **4 Select / slice** | Requirement selected or open-slice posture consistent; no shrink-table. |

## Open-task sync

After stages 2–4 PASS (or when docs already covered and only stubs lag):

- Ensure selected leaves map to open-slice task stubs under `docs/rr/tasks/{slice_id}/` when a slice exists (thin Goal citing PRD/delta ids — not full prepare L2 unless user asks).
- Do **not** invent a phantom slice or run prepare/coder.
- Do **not** treat cascade gaps as “builder will put it in the task body.”
- Do **not** load builder `refs/feature.md` / `adhoc.md` — peer-invoke builder SKILL when execute readiness needs mint/detail/code.

## Peer invoke (builder work)

When task situate / mint/detail / code readiness is needed beyond stub sync: **Invoke** `skills/rr-builder/SKILL.md` with purpose (`--intake` for situate/5–6, or `--feature` / `--adhoc` when ready) via **Task** sub-agent **or** parent-inline `Read` of that **SKILL.md** + purpose. Let builder Procedure resolve its refs. Shared law only: `refs/planning/intake.md`.

## Next Up

| Outcome | Offer |
|---------|-------|
| Docs/challenge/select still blocked | Legal pipeline moves only (`refs/planning/intake.md` Next Up table) |
| Stages 1–4 PASS; task missing or thin | peer `rr-builder --intake` or `--feature` (builder owns 5–7) |
| Stages 1–4 PASS; task ready | peer `rr-builder --feature` (default) or `--adhoc` (urgent) or orchestrate `--task` |

**Anti-flip:** Never auto-code. Never AskQuestion “skip to implement.” Never `Read` builder refs to perform execute work.

## Done-when

- Situate report emitted
- Stages 2–4 complete or first blocking stage named with Next Up
- Open-task stubs synced when applicable
- No application source edits; no `--feature` / `--adhoc` run inside planner

## Non-goals

- Stages 5–7 (builder via peer SKILL)
- Silent unfreeze / invent Discover parents
- non_rr `docs/rr/` invent (route builder collapsed pipeline instead)
