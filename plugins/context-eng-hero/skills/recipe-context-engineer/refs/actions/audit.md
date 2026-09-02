# Action: audit (internal)

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `audit-1-load` |
| `questioning.md` | `audit-1-load` (missing path) |
| `classify.md` | `audit-1-load` (type) |
| `ui-brand.md` | `audit-1-load` (banner), `audit-2-static` (liveness) |
| `gate-prompts.md` | `audit-5-report` |
| `failure-patterns.md` | `audit-4-merge` |
| `templates/audit-output.template.md` | `audit-5-report` |
| `close-contract.md` | `audit-5-report` |
| Type rubric in `rubrics/<type>.rubric.md` (+ `rubrics/skill-ref.rubric.md` for Skill+Ref packs) | `audit-3-judgment` |

## Steps

### Step 1: `audit-1-load`

- **Outcome:** Target file and artifact type are known.
- **Done when:** Path resolved via `questioning.md` if missing; type stated per `classify.md` (or assumption noted once).
- **Banner:** `CE ► AUDIT` per `ui-brand.md`.

### Step 2: `audit-2-static`

- **Outcome:** Static check table is produced from `scripts/audit_static.py`.
- **Liveness:** Emit `◆ Running static audit (~5–10s)…` per `ui-brand.md` **before** the shell call.
- **Done when:** From plugin root (Python **3.14+**, see plugin root `CLAUDE.md` **Python runtime**):
  1. If PyYAML is missing, run `python3 -m pip install -r scripts/requirements.txt` (plugin root).
  2. Run `python3 scripts/audit_static.py . <relative-path>` (or `.venv/bin/python` if using a venv).
  3. Paste output into report **Static checks** section.
  If the script is missing or still errors after bootstrap, report **STATIC SKIPPED** with reason—**continue to judgment** (audit-only path). Do not treat SKIPPED as PASS.

### Step 3: `audit-3-judgment`

- **Outcome:** Every **Judgment** row in the type rubric is PASS/FAIL with observable evidence.
- **Done when:** All judgment ids evaluated; static ids from script output not manually rescored; Skill+Ref packs also run `rubrics/skill-ref.rubric.md` when applicable.

### Step 4: `audit-4-merge`

- **Outcome:** Severity summaries count pass/total per severity across static + judgment.
- **Done when:** Critical, Major, Minor lines filled; verdict **PASS** only if every check PASS (SKIPPED static → verdict cannot be PASS unless user accepts audit-only draft).

### Step 5: `audit-5-report`

- **Outcome:** Full audit report emitted; loop closed.
- **Done when:** Report per `templates/audit-output.template.md`; **post-audit-routing** AskQuestion per `gate-prompts.md`; follow-ups verb-only per `close-contract.md`.

## Stop

**Diagnosis only** during steps 1–5. No edits unless the user selects **Fix failures now** in **post-audit-routing** or explicitly requests redesign.
