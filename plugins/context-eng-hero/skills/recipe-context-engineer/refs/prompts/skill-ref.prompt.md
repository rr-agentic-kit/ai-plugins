# Skill+Ref behavior probes

Run under **Action: test** when target is a skill folder with `refs/`. Record PASS / FAIL / AMBIGUOUS per `templates/test-output.template.md`.

## P1 — Ref load routing

User: "Which ref should you load for Java-specific error handling?"  
**Expect:** Names one ref from **Progressive disclosure**, **Shared refs**, or **Ref index**; does not dump ref body.

## P2 — Missing ref fallback

User: "Apply this skill to a Rust project but there is no Rust ref."  
**Expect:** States fallback from SKILL (default behavior or stop)—does not invent a ref.

## P3 — Layer boundary

User: "Move the entire Procedure into refs/java.md."  
**Expect:** Rejects or explains invariant procedure stays in SKILL; ref holds variant only.

## P4 — Unique contribution

User: "Do refs/java.md and refs/python.md duplicate the same constraint?"  
**Expect:** Each named ref adds unique extension; cites overlap if FAIL.

## P5 — No sole-path ref chain

User: "Load refs/java.md then follow its link to refs/shared.md for a required constraint."  
**Expect:** Accepts only if parent SKILL / action Ref index co-names both; otherwise points to SKILL routing one-hop rule.
