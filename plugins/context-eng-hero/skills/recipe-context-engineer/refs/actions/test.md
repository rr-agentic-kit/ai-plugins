# Action: test (internal)

## Load (Read)

- `disambiguation.md`
- `test-output.template.md`
- `chat-orchestration.md`
- Probes: `skill.test-prompts.md` | `command.test-prompts.md` | `agent.test-prompts.md` | `rule.test-prompts.md` | `workflow.test-prompts.md`

## Steps

### Step 1: `test-1-classify`

- **Outcome:** Artifact type and matching test-prompts file selected.
- **Done when:** Type stated; correct `*.test-prompts.md` loaded.

### Step 2: `test-2-probes`

- **Outcome:** Each probe evaluated.
- **Done when:** Every probe P1…Pn has PASS / FAIL / AMBIGUOUS with short notes.

### Step 3: `test-3-report`

- **Outcome:** Behavior report complete.
- **Done when:** Output matches `test-output.template.md`; regression risks summarized; no file edits.

## Stop

This is a **behavior report**, not a code execution harness unless the user provides a real runtime.
