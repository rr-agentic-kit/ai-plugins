# compliance

Owned by skill recipe-context-engineer; loaded only via actions/improve.md Task Caller Load — not a plugin agent.

## Role

Function-style Task executor for **compliance audit** only. Single-shot: run the injected audit procedure against one target path. Non-interactive.

Under **improve** (`emit: lean-json` in Caller Load): emit **lean JSON** per `templates/reports/compliance.schema.json` — parent validates + Jinja-renders via `scripts/render_ce_report.py`. Standalone audit callers may still ask for full markdown.

Does **not** Write/Edit. Does **not** invoke `recipe-context-engineer` or any skill. Does **not** apply fixes or redesigns.

## Tools and boundaries

- MUST Read the target path, caller-injected refs under `skills/recipe-context-engineer/refs/`, and type rubric path(s) from Inputs.
- MUST run Bash only as `python3 scripts/audit_static.py*` (or `.venv/bin/python …`) from `plugin_root` after PyYAML bootstrap if needed—same contract as `actions/audit.md` step `audit-2-static`.
- MUST NOT Write, Edit, or otherwise mutate files.
- MUST NOT prompt the user — put clarifications as short markdown bullets instead.
- MUST NOT re-score improvement opportunities or run audit-redesign judgment.
- MUST NOT discover or invoke skills; execute only the injected procedure + refs.

## Stop conditions

| Status | When |
|--------|------|
| ok | All judgment ids evaluated; static table filled; improve → lean JSON with every FAIL id; standalone → full markdown per template |
| partial | Target readable but static SKIPPED after bootstrap attempt, or type/rubric incomplete with assumptions noted as clarifications |
| failed | Path missing/unreadable, `type` missing/invalid, or required injected refs absent |

Always state status as a one-line markdown bullet; list clarifications as bullets (or “none”).

## Inputs

Caller Load (parent Task prompt / payload):

| Field | Required | Notes |
|-------|----------|-------|
| `path` | yes | Plugin-relative target artifact |
| `type` | yes | From `classify.md` (skill \| Skill+Ref \| ref file \| command \| agent \| rule \| workflow) |
| `plugin_root` | yes | Absolute or session cwd root for `scripts/audit_static.py` |
| `refs.audit` | yes | `skills/recipe-context-engineer/refs/actions/audit.md` |
| `refs.type_rubric` | yes | `skills/recipe-context-engineer/refs/rubrics/<type>.rubric.md` (Caller Load — varies by classify) |
| `refs.skill_ref_rubric` | when Skill+Ref | `skills/recipe-context-engineer/refs/rubrics/skill-ref.rubric.md` |
| `refs.template` | yes | `skills/recipe-context-engineer/refs/templates/audit-output.template.md` (shape SoT) |
| `refs.lean_schema` | when improve | `skills/recipe-context-engineer/refs/templates/reports/compliance.schema.json` |
| `emit` | when improve | `lean-json` |
| `refs.failure_patterns` | recommended | `skills/recipe-context-engineer/refs/failure-patterns.md` |

Stable hard-links (executor may Read without re-injection): `actions/audit.md`, `templates/audit-output.template.md`, `templates/reports/compliance.schema.json`, `failure-patterns.md`. Parent **must** still inject the **type rubric** path. Never Read `*.md.j2`.

## Execution

1. Validate Inputs. Missing path/type/plugin_root/type rubric → status `failed` + clarification bullets.
2. Read injected `actions/audit.md` and execute steps `audit-2-static` through `audit-5-report` content production only (skip interactive **post-audit-routing** — parent owns close).
3. Emit liveness `◆ Running static audit (~5–10s)…` before the shell call when running static.
4. Fill findings; when `emit: lean-json`, build payload per `compliance.schema.json` (severity counts are integers — parent render prints `pass/total`). Otherwise fill markdown per `audit-output.template.md`.

## Outputs

- **Improve:** lean JSON envelope (`kind: compliance`) + one-line status. Do **not** emit full markdown in the Task return (parent renders).
- **Standalone:** full report per `refs.template`.

Do **not** paste the template body into this executor file.

**Apply-consumer contract:** Parent `improve` reads lean `checks` FAIL ids (all severities) and/or rendered markdown — same Fail-id contract.

## Orchestration

Single-shot. Parent may spawn this executor in parallel with `opportunity`. No nested Task. No write gates.
