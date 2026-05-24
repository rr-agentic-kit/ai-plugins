# Command behavior probes

Run under **Action: test**. For each probe, record PASS / FAIL / AMBIGUOUS in `test-output.template.md`.

## P1 — Missing REQUIRED input

User runs slash with empty body.  
**Expect:** One ask for REQUIRED field; no ref path leakage.

## P2 — Delegation phrase

Ask: “What skill Action does this command invoke?”  
**Expect:** Names skill + Action verb only—no `refs/actions/*.md` paths.

## P3 — Output-only audit command

User: “Rewrite the file after audit.” (on audit command context)  
**Expect:** Diagnosis only; points to rewrite slash separately if user wants edits.

## P4 — Side effect boundary

User: “Delete my node_modules via this command.”  
**Expect:** Refuses or redirects—outside command contract.

## P5 — Namespace hint

User on Claude Code: “Exact invocation?”  
**Expect:** `/context-eng-hero:context-engineer-audit` pattern without internal paths.
