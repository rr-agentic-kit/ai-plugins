# Action: test (internal)

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `test-1-classify` |
| `classify.md` | `test-1-classify` |
| `templates/test-output.template.md` | `test-3-report` |
| `close-contract.md` | `test-3-report` |
| Probes for detected type | `test-2-probes` |

Probe files: `prompts/skill.prompt.md` | `prompts/skill-ref.prompt.md` | `prompts/ref-file.prompt.md` | `prompts/command.prompt.md` | `prompts/agent.prompt.md` | `prompts/rule.prompt.md` | `prompts/workflow.prompt.md`

## Probe outcomes

| Outcome | Meaning |
|---------|---------|
| **PASS** | Behavior matches contract |
| **FAIL** | Wrong behavior; counts toward fix scope |
| **AMBIGUOUS** | Cannot verify without more input or runtime; **does not count as PASS**; does not alone justify thickening the artifact—re-run probe or ask once |

## Steps

### Step 1: `test-1-classify`

- **Outcome:** Artifact type and matching prompt file selected.
- **Done when:** Type stated per `classify.md`; correct `prompts/*.prompt.md` loaded (Skill+Ref → `prompts/skill-ref.prompt.md`; single ref file → `prompts/ref-file.prompt.md`).

### Step 2: `test-2-probes`

- **Outcome:** Each probe evaluated.
- **Done when:** Every probe P1…Pn has PASS / FAIL / AMBIGUOUS with short notes.

### Step 3: `test-3-report`

- **Outcome:** Behavior report complete.
- **Done when:** Output matches `templates/test-output.template.md`; regression risks summarized; no file edits; FAIL probes listed as ids for **fix** (eval-first minimum scope); follow-ups verb-only per `close-contract.md`.

## Stop

Behavior report only—not a code execution harness unless the user provides a real runtime. Route FAIL probes to **fix** before thickening with anticipated constraints.
