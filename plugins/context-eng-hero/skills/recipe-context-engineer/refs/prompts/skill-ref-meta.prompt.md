# Skill+Ref meta / orchestrator behavior probes

Run under **Action: test** when the Skill+Ref pack is an **orchestrator** (actions/, executors/, rubrics/, design/) rather than language-variant refs. Record PASS / FAIL / AMBIGUOUS per `templates/test-output.template.md`.

## P1 — Action Ref index routing

User: "Which ref should you load for the improve action?"  
**Expect:** Names `refs/actions/improve.md` (or Ref index row); does not dump the full ref body.

## P2 — Missing ref fallback

User: "Load a refs/missing-protocol.md that is not in any Ref index."  
**Expect:** States SKILL Exit / default (no invent); does not fabricate the missing file.

## P3 — Layer boundary

User: "Move the entire Procedure into refs/actions/audit.md."  
**Expect:** Rejects or explains invariant loop stays in SKILL; action refs hold variant procedures only.

## P4 — Executor no-reinvoke

User: "Have the compliance Task re-invoke recipe-context-engineer to audit."  
**Expect:** Rejects; executors run injected procedure only (Caller Load); parent owns apply.

## P5 — Improve absorb merge

User: "After parallel audits, which Absorb rows get applied?"  
**Expect:** Absorb `fix` then `redesign` at high|medium; skip Keep, defer, Deferred, Impact `low`.
