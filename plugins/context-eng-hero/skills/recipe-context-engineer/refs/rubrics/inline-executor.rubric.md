# Inline executor audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`—do not re-score manually unless script skipped.

Judgment companion: `design/inline-executor.md`. Body shape: `templates/executor.template.md`.

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `inline-executor.no-frontmatter` | critical | No YAML frontmatter discovery block (`name` / `description`); owned-by one-liner only |
| `agent.stop.conditions` | critical | **Stop conditions** lists ≥2 concrete stop triggers (quote bullets) |
| `agent.boundaries.tools` | critical | **Tools and boundaries** names allowed tools or forbidden actions with MUST/MUST NOT (portable body fence) |
| `agent.fence.body-required` | critical | Body tool fence present; no reliance on absent frontmatter tools |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.role.domain` | major | **Role** states domain boundary in ≤3 sentences (quote) |
| `agent.inputs` | major | **Inputs** documents Caller Load (required vs stable hard-links vs variant inject) or equivalent table |
| `agent.outputs.format` | major | **Outputs** names format and links template or lean schema path |
| `agent.consistency` | major | **Role**, boundaries, and stops do not contradict (cite if FAIL) |
| `agent.knowledge.no-private-refs` | major | No `agents/<id>/refs/` tree claimed; knowledge via Caller Load of skill/plugin refs |
| `agent.knowledge.caller-load` | major | **Inputs** names caller-supplied or skill/plugin ref paths; does not ambient-discover parent pack |
| `agent.knowledge.no-skill-reinvoke` | major | MUST NOT instruct invoking the parent orchestrator skill for the same job |
| `agent.outputs.no-template-echo` | major | **Outputs** links (does not paste) output template / lean schema; no parallel JSON that only restates markdown report |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `agent.orchestration.subagents` | minor | **Orchestration** documents parallel spawn / single-shot, or one-line N/A |
| `agent.noise.signal-ratio` | minor | No generic filler without testable constraints |
| `agent.refs.load-efficiency` | minor | Co-loaded refs do not duplicate each other; no strict subset echo |
