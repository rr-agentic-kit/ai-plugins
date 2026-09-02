# Ref file behavior probes

Run under **Action: test** on a single `refs/<name>.md`. Record PASS / FAIL / AMBIGUOUS per `templates/test-output.template.md`.

## P1 — Standalone purpose

User: "What does this ref add?" (no parent SKILL in context)  
**Expect:** Answers from **Purpose** sentence; does not require parent Procedure.

## P2 — Base duplication

User: "Repeat the parent skill's Procedure from this ref."  
**Expect:** Ref does not duplicate Procedure; cites **Load** back to parent or declines.

## P3 — Load path

User: "When should an agent Read this file?"  
**Expect:** Cites **Load** section (parent step + path)—not "whenever relevant."

## P4 — Ref chain

User: "Also load refs/other.md linked from this ref."  
**Expect:** Declines ref→ref; parent SKILL owns disclosure.

## P5 — Variant only

User: "Should this ref define the skill's classify table?"  
**Expect:** No—layer violation; invariant tables belong in parent SKILL.
