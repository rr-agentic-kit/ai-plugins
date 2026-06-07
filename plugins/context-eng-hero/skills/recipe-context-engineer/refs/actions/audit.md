# Action: audit (internal)

## Load (Read)

- `ui-brand.md`
- `gate-prompts.md`
- `questioning.md`
- `failure-patterns.md`
- `audit-output.template.md`
- Rubric for detected type: `skill.audit-rubric.md` | `command.audit-rubric.md` | `agent.audit-rubric.md` | `rule.audit-rubric.md` | `workflow.audit-rubric.md`

## Steps

### Step 1: `audit-1-load`

- **Outcome:** Target file and artifact type are known; rubric and templates are loaded.
- **Done when:** Path resolved via `questioning.md` if missing; type stated (or assumption noted once); all Load files read.
- **Banner:** `CE ► AUDIT` per `ui-brand.md`.

### Step 2: `audit-2-static`

- **Outcome:** Static check table is produced from `scripts/audit_static.py`.
- **Liveness:** Emit `◆ Running static audit (~5–10s)…` per `ui-brand.md` **before** the shell call.
- **Done when:** From plugin root (Python **3.14+**, see plugin root `CLAUDE.md` **Python runtime**):
  1. If PyYAML is missing, run `python3 -m pip install -r scripts/requirements.txt` (plugin root).
  2. Run `python3 scripts/audit_static.py . <relative-path>` (or `.venv/bin/python` if using a venv).
  3. Paste output into report **Static checks** section.
  If the script is missing or still errors after bootstrap, report **STATIC SKIPPED** with reason—do not silently omit.

### Step 3: `audit-3-judgment`

- **Outcome:** Every **Judgment** row in the type rubric is PASS/FAIL with observable evidence.
- **Done when:** All judgment ids evaluated; static ids from script output not manually rescored; no score or 12-check cap.

### Step 4: `audit-4-merge`

- **Outcome:** Severity summaries count pass/total per severity across static + judgment.
- **Done when:** Critical, Major, Minor lines filled; verdict **PASS** only if every check PASS.

### Step 5: `audit-5-report`

- **Outcome:** Full audit report emitted per `audit-output.template.md`; loop closed with routing gate.
- **Done when:** Report includes narrative findings (pattern labels), severity summary, static + judgment tables; **post-audit-routing** AskQuestion per `gate-prompts.md`; on selection, skill continues to the routed action (do not defer to slash commands).

## Stop

**Diagnosis only** during steps 1–5. No edits unless the user selects **Fix failures now** in **post-audit-routing** (routes to **fix**) or explicitly requests redesign.
