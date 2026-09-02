# Skill behavior probes

Run under **Action: test**. For each probe, record PASS / FAIL / AMBIGUOUS in `templates/test-output.template.md`.

## P1 — Type classification

User: “Should this be a skill or a command? I have a checklist run on every PR.”  
**Expect:** Narrow recommendation + one reason tied to invocation pattern.

## P2 — Anti-trigger

User: “Refactor my Java service” (skill is about markdown artifact design only).  
**Expect:** Decline or redirect; cites when not to use / scope.

## P3 — Ambiguous target

User: “Make it better.”  
**Expect:** One clarifying question or AskQuestion-style options—not a full redesign.

## P4 — Procedure order

User: “Apply this skill to tune log levels in production.”  
**Expect:** States missing artifact path/type; does not invent file edits.

## P5 — Progressive disclosure

User: “List only the steps you’d load from refs for an audit.”  
**Expect:** Mentions rubric + output template + target file read—no full rubric dump unless asked.
