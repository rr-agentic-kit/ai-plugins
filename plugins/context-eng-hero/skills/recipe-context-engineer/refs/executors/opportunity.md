# opportunity

Owned by skill recipe-context-engineer; loaded only via actions/improve.md Task Caller Load — not a plugin agent.

## Role

Function-style Task executor for **audit-redesign** (improvement opportunities) only. Single-shot: run the injected audit-redesign procedure against one target path. Non-interactive.

Under **improve** (`emit: lean-json`): emit **lean JSON** per `templates/reports/opportunity.schema.json` — parent validates + Jinja-renders via `scripts/render_ce_report.py`. Standalone callers may still ask for full markdown.

Does **not** Write/Edit/Bash. Does **not** invoke `recipe-context-engineer` or any skill. Does **not** apply absorb hints (parent `improve` / fix / redesign own apply).

## Tools and boundaries

- MUST Read the target path and caller-injected refs under `skills/recipe-context-engineer/refs/`.
- Under improve with `lean_out`: MAY Write **only** that scratch JSON path. MUST NOT Edit/Write target skill paths or any other files. MUST NOT Bash.
- Without `lean_out`: MUST NOT run Bash, Write, Edit, or otherwise mutate files (read-only judgment).
- MUST NOT prompt the user — put clarifications as short markdown bullets instead.
- MUST NOT re-litigate compliance PASS/FAIL as opportunities; skim unresolved FAILs into **Compliance blockers** only when supplied or visible.
- MUST NOT discover or invoke skills; execute only the injected procedure + refs.

## Stop conditions

| Status | When |
|--------|------|
| ok | All eight dimensions evaluated; Challenge + Ranked complete; improve → lean JSON with Ranked Absorb/Impact; standalone → full markdown |
| partial | Target readable but type incomplete, or compliance skim incomplete with assumptions noted as clarifications |
| failed | Path missing/unreadable, `type` missing/invalid, or required injected refs absent |

Always state status as a one-line markdown bullet; list clarifications as bullets (or “none”).

## Inputs

Caller Load (parent Task prompt / payload):

| Field | Required | Notes |
|-------|----------|-------|
| `path` | yes | Plugin-relative target artifact |
| `type` | yes | From `classify.md` |
| `plugin_root` | yes | Session plugin root (for path resolution; no shell required) |
| `refs.audit_redesign` | yes | `skills/recipe-context-engineer/refs/actions/audit-redesign.md` |
| `refs.rubric` | yes | `skills/recipe-context-engineer/refs/rubrics/audit-redesign.rubric.md` |
| `refs.patterns` | yes | `skills/recipe-context-engineer/refs/improvement-patterns.md` |
| `refs.template` | yes | `skills/recipe-context-engineer/refs/templates/audit-redesign-output.template.md` (shape SoT) |
| `refs.lean_schema` | when improve | `skills/recipe-context-engineer/refs/templates/reports/opportunity.schema.json` |
| `emit` | when improve | `lean-json` |
| `lean_out` | when improve | Absolute path under `.ai/learning/ce-improve/<run-id>/opportunity.json` — Write lean JSON here; chat return stays tiny |
| `compliance_skim` | optional | FAIL ids / note from parallel `compliance` executor — blockers section only |

Stable hard-links (executor may Read without re-injection): `actions/audit-redesign.md`, `rubrics/audit-redesign.rubric.md`, `improvement-patterns.md`, `templates/audit-redesign-output.template.md`, `templates/reports/opportunity.schema.json`. Parent still injects paths in the Task prompt (Caller Load). Never Read `*.md.j2`.

## Execution

1. Validate Inputs. Missing path/type/required refs → status `failed` + clarification bullets.
2. Read injected `actions/audit-redesign.md` and execute steps `ar-2-judge` through `ar-5-report` content production only (skip interactive **post-audit-redesign-routing** — parent owns close when running standalone; `improve` merges instead).
3. Apply rubric Challenge (before rank) and impact×confidence filter. Rank unbounded `1…N`. Do not assume ≤7 rows. FN must walk scriptable invent + context-bloating shell/list (SCRIPTABLE); do not require existing `scripts/`.
4. Fill findings; when `emit: lean-json`, build payload per `opportunity.schema.json`. Otherwise fill markdown per `audit-redesign-output.template.md`. Summary/Why = detect; absorb = improve path.

## Outputs

- **Improve:** Write lean JSON envelope (`kind: opportunity`) to `lean_out` when provided; chat return = status + ranked_count + path — **not** full JSON. Do **not** emit full markdown in the Task return.
- **Standalone:** full report per `refs.template`.

Do **not** paste the template body into this executor file.

**Apply-consumer contract:** Parent `improve` reads lean `ranked[]` (Absorb + Impact) and/or rendered markdown. Apply only Absorb `fix`\|`redesign` with Impact ∈ {high, medium}. Skip Keep, Absorb `defer`, Deferred, Impact `low`.

## Orchestration

Single-shot. Parent may spawn this executor in parallel with `compliance`. No nested Task. No write gates. No auto-apply.
