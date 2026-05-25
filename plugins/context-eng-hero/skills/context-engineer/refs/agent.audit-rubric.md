# Agent audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`—do not re-score manually unless script skipped.

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.stop.conditions` | critical | **Stop conditions** lists ≥2 concrete stop triggers (quote bullets) |
| `agent.boundaries.tools` | critical | **Tools and boundaries** names allowed tools or forbidden actions with MUST/MUST NOT |
| `agent.routing.no-chain-only` | critical | Procedure does not rely solely on chaining plugin commands without owned agent steps |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.role.domain` | major | **Role** states domain boundary in ≤3 sentences (quote) |
| `agent.inputs` | major | **Inputs** states what invoker must supply or “none” with reason |
| `agent.outputs.format` | major | **Outputs** names format (markdown table, JSON fields, file list, etc.) |
| `agent.consistency` | major | **Role**, boundaries, and stops do not contradict (cite if FAIL) |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.orchestration.subagents` | minor | **Orchestration** documents Task/subagent use when multi-step, or one-line N/A for single-shot |
| `agent.noise.signal-ratio` | minor | No generic filler without testable constraints |
| `agent.refs.load-efficiency` | minor | Files in this artifact's **Load** list do not duplicate each other's content; no ref is a strict subset of another co-loaded ref |
