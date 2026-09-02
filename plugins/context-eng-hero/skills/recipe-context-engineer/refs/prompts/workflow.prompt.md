# Workflow behavior probes

Run under **Action: test**. For each probe, record PASS / FAIL / AMBIGUOUS in `templates/test-output.template.md`.

## P1 — Step ownership

User: “Who owns step 2?”  
**Expect:** Points to delegation table row—no vague “the agent”.

## P2 — Exit condition

User: “When do we stop if CI is red?”  
**Expect:** Cites Exit/failure section behavior.

## P3 — Unbounded loop

Workflow text implies repeating until subjective “good”.  
**Expect:** FAIL probe unless exit is added—author should fix workflow.

## P4 — Branching

User picks a branch not in Preconditions.  
**Expect:** Asks for declared branch or updates preconditions—does not invent.

## P5 — Chain-only risk

Workflow says only “run /a then /b” with no outputs.  
**Expect:** Identifies chain-only gap (audit finding), suggests owned steps.
