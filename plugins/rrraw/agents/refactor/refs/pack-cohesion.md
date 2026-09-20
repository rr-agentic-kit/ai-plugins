# Pack: cohesion (phase 4)

**Band:** `cohesion` · **Phase:** 4 · **Mandatory LLM** (tool emptiness ≠ skip)

## Load (only if not already in session)

1. `skills/rr-builder/rr-coder/refs/srp-cohesion.md` — red/green/gray + new-vs-live
2. `skills/rr-builder/rr-coder/refs/compliance-rubric.md` — **CP015**, **CP023**
3. `skills/rr-builder/rr-coder/refs/testability.md` — when pure logic is mixed with I/O

## Checklist

- [ ] Classify each scoped type: **red** / **green** / **gray** per `srp-cohesion.md`
- [ ] Green → no row
- [ ] Red (fat CP015 / domain god-object, **not** LOC-only) → finding + `disposition: fix`
- [ ] Gray → new → `fix`; live → `clarify` or `escalate_human` (short cost/clarity in `description`)
- [ ] Method mixes deterministic rules with I/O in one body → note `testability: extract-pure-core` or `introduce-port` in `description` when behavior-preserving refactor is viable
- [ ] Cite **CP023** or **CP015**
- [ ] **Exclude** size-only `god_class` (LOC/fan-out) — Phase **3** only
- [ ] Do not auto-split small non-duplicating types
- [ ] Empty array valid only after a real Phase 4 pass (all green)

## Disposition (required on every finding)

`fix` | `clarify` | `escalate_human`

## Output shape

`{file, line, phase: 4, type: "mixed_responsibility", description, disposition}`
