# Ref file behavior probes

Run under **Action: test** on a single `refs/<name>.md`. Record PASS / FAIL / AMBIGUOUS per `templates/test-output.template.md`.

## P1 — Unique value

User: "What does this ref add that the parent SKILL does not already say?"  
**Expect:** Names constraints unique to this file; does not invent Purpose/Load scaffolding.

## P2 — Base duplication

User: "Repeat the parent skill's Procedure from this ref."  
**Expect:** Ref does not duplicate Procedure; points to parent SKILL.

## P3 — Routing ownership

User: "When should an agent Read this file?"  
**Expect:** Cites parent SKILL Progressive disclosure / Shared refs / action Ref index — not "whenever relevant."

## P4 — Ref chain

User: "Also load refs/other.md linked from this ref to get a required constraint."  
**Expect:** PASS if peer is co-named by parent SKILL / action Ref index; otherwise declines sole-path ref→ref.

## P5 — Variant only

User: "Should this ref define the skill's classify table?"  
**Expect:** No—layer violation; invariant tables belong in parent SKILL.
