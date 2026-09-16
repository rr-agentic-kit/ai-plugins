# Agent audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`—do not re-score manually unless script skipped.

Judgment companion: `design/agent.md`. Field SoT: `frontmatter-schemas.md`.

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.stop.conditions` | critical | **Stop conditions** lists ≥2 concrete stop triggers (quote bullets) |
| `agent.boundaries.tools` | critical | **Tools and boundaries** names allowed tools or forbidden actions with MUST/MUST NOT (portable body fence) |
| `agent.routing.no-chain-only` | critical | Procedure does not rely solely on chaining plugin commands without owned agent steps |
| `agent.fence.body-required` | critical | Body tool fence present; tools are not claimed **only** in frontmatter without body MUST/MUST NOT |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.role.domain` | major | **Role** states domain boundary in ≤3 sentences (quote) |
| `agent.description.recommended-length` | major | `description` ≤160 characters one sentence, or user explicitly accepted over-budget |
| `agent.description.invoke-fit` | major | `description` states purpose + when without delegation chains or internal agent IDs |
| `agent.inputs` | major | **Inputs** states what invoker must supply or “none” with reason |
| `agent.outputs.format` | major | **Outputs** names format (markdown table, JSON fields, file list, etc.) |
| `agent.consistency` | major | **Role**, boundaries, and stops do not contradict (cite if FAIL) |
| `agent.fm.no-false-security` | major | Plugin-shipped agents do not set `permissionMode` / `hooks` / `mcpServers` as if they enforce security (ignored in plugins) |
| `agent.fm.tools-align-body` | major | If frontmatter `tools` / `disallowedTools` present, they do not contradict the body fence |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.orchestration.subagents` | minor | **Orchestration** documents Task/subagent use when multi-step, or one-line N/A for single-shot |
| `agent.noise.signal-ratio` | minor | No generic filler without testable constraints |
| `agent.refs.load-efficiency` | minor | Files in this artifact's **Load** list do not duplicate each other's content; no ref is a strict subset of another co-loaded ref |
| `agent.access.portable-default` | minor | Marketplace default is `name`+`description` only unless a runtime extra is justified; Cursor `readonly` / Claude `maxTurns` set only when useful and honored |
