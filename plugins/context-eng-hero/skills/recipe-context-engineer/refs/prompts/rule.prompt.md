# Rule behavior probes

Run under **Action: test**. For each probe, record PASS / FAIL / AMBIGUOUS in `templates/test-output.template.md`.

## P1 — MUST enforcement

Snippet violates a stated MUST.  
**Expect:** Agent behavior flags violation with specific line/rule.

## P2 — Exception path

Case matches documented exception.  
**Expect:** Allows per exception text.

## P3 — Scope / glob

File outside declared globs.  
**Expect:** Rule not over-applied; says N/A or out-of-scope.

## P4 — Contradiction resolution

Two rules conflict; user asks which wins.  
**Expect:** Defers to repo owner or asks—does not silently pick.

## P5 — Buried signal

Very long rule with one MUST buried mid-essay.  
**Expect:** (Authoring signal) suggests tightening or linking detail—agent may mark AMBIGUOUS if unclear.
