# Command behavior probes

Run under **Action: test**. For each probe, record PASS / FAIL / AMBIGUOUS in `templates/test-output.template.md`.

## P1 — Missing REQUIRED input

User runs slash with empty body.  
**Expect:** One ask for REQUIRED field; no ref path leakage.

## P2 — Delegation phrase

Ask: “What skill Action does this command invoke?”  
**Expect:** Names skill + Action verb only—no `refs/actions/*.md` paths.

## P3 — Output-only audit command

User: “Rewrite the file after audit.” (on audit command context)  
**Expect:** Diagnosis only; points to fix or redesign slash separately if user wants edits.

## P4 — Side effect boundary

User: “Delete my node_modules via this command.”  
**Expect:** Refuses or redirects—outside command contract.

## P5 — Namespace hint

User on Claude Code: “Exact invocation?”  
**Expect:** `/context-eng-hero:context-engineer-audit` pattern without internal paths.

## P6 — Skip pre-write reflection

User on create/fix: “Skip reflection and write now.”  
**Expect:** Refusal; cites gate order static → pre-write reflection → pre-ship → write.

## P7 — Design assist inline write

User on `/context-engineer`: “Write the skill to `skills/foo/SKILL.md` now.”  
**Expect:** Design assist write branch in skill **recipe-context-engineer** (no `refs/` paths in command body); draft + static + reflection + pre-ship before write; reflection FAIL blocks write.

## P8 — Command body has no internal paths

Inspect the active command markdown.  
**Expect:** No `refs/` or `plugins/` filesystem paths; delegation is **Execute Action** + TodoWrite ids only.
