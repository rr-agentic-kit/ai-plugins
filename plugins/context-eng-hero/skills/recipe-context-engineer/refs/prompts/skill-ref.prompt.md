# Skill+Ref behavior probes

Run under **Action: test** when target is a skill folder with `refs/`. Record PASS / FAIL / AMBIGUOUS per `templates/test-output.template.md`.

## P1 — Ref load routing

User: "Which ref should you load for Java-specific error handling?"  
**Expect:** Names one ref from **Progressive disclosure**; does not dump ref body.

## P2 — Missing ref fallback

User: "Apply this skill to a Rust project but there is no Rust ref."  
**Expect:** States fallback from SKILL (default behavior or stop)—does not invent a ref.

## P3 — Layer boundary

User: "Move the entire Procedure into refs/java.md."  
**Expect:** Rejects or explains invariant procedure stays in SKILL; ref holds variant only.

## P4 — Ref standalone

User: "Summarize refs/java.md without reading SKILL.md."  
**Expect:** Possible only if ref is standalone; otherwise cites missing parent context once.

## P5 — No ref chain

User: "Load refs/java.md then follow its link to refs/shared.md."  
**Expect:** Declines ref→ref chain; points to SKILL progressive disclosure one-hop rule.
