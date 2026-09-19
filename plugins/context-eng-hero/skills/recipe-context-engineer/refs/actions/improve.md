# Action: improve (internal)

Orchestrate **compliance audit** + **audit-redesign** in parallel, merge an apply list, then run **fix** then **redesign** under shared write gates. Parent-only Task executors (`compliance`, `opportunity`) do **not** invoke this skill; parent injects refs (Caller Load).

**Skip Advise** for this action (reports are the plan)—see `advisory.md`.

## Apply policy

Merge from the **persisted** markdown reports only (rendered from lean JSON—no full-report paste into chat). Template SoT: `templates/audit-output.template.md` (Verdict / Findings FAIL ids) and `templates/audit-redesign-output.template.md` (Ranked **Absorb** column + apply-consumer field contract). Lean JSON contracts: `templates/reports/<kind>.schema.json` (index: `templates/ce-report-lean.schema.md`).

Under write gates:

1. Compliance FAILs (all severities, from Findings) → **fix** first
2. Ranked opportunities with Absorb `fix` → **fix**
3. Ranked opportunities with Absorb `redesign` → **redesign**
4. **Skip:** Keep notes, Absorb `defer`, Deferred table, Impact `low`

**Two human gates (not one theatrical approve):**

1. **approve-apply-plan** after `improve-3-merge` — before any target-path mutation
2. **approve-revise-abort** after shared write gates — before promoting draft → target

After Write-gate **Approve** (promote succeeded): **scoped git stage** of the improve **touch list** only — see `shared-write-gates.md` Write gate. Never `git commit` / PR from improve. Abort → no git stage.

## Report scratch (read-budget)

Per improve run, create `.ai/learning/ce-improve/<run-id>/` under the **user project** (mkdir if needed). Persist:

| File | Content |
|------|---------|
| `compliance.json` / `opportunity.json` | Lean executor payloads (Task return / stdin to render) |
| `compliance.md` / `opportunity.md` | Full reports via `python3 scripts/render_ce_report.py` — **not** agent `Write` of full bodies |
| `apply-plan.json` / `apply-plan.md` | Merged plan lean + rendered |
| `touch-list.txt` | Newline-separated repo-relative paths improve wrote/promoted (for scoped `git add`) |
| `draft/` | Off-path draft tree (optional mirror of target relatives) |

Chat after audits: status + Verdict / ranked counts + **links** to rendered `.md` files — **do not** paste full report bodies.

**Render invoke (plugin root = context-eng-hero):**

```bash
python3 scripts/render_ce_report.py compliance --in .ai/learning/ce-improve/<run-id>/compliance.json --out .ai/learning/ce-improve/<run-id>/compliance.md
python3 scripts/render_ce_report.py opportunity --in …/opportunity.json --out …/opportunity.md
python3 scripts/render_ce_report.py apply-plan --in …/apply-plan.json --out …/apply-plan.md
```

(Paths may be absolute under the user project; adjust `--in`/`--out` accordingly.)

**Validate→fix:** on exit **2**, read stderr `path: message` lines, fix the lean `*.json`, re-run render — do **not** agent-`Write` full report markdown. Pattern: `templates/reports/README.md`.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `improve-1-load` |
| `questioning.md` | `improve-1-load` (missing path; **Delivery channels**) |
| `classify.md` | `improve-1-load` (type) |
| `ui-brand.md` | `improve-1-load` (banner), parallel audits (liveness) |
| `actions/audit.md` | Inject into `compliance` Task |
| `actions/audit-redesign.md` | Inject into `opportunity` Task |
| `rubrics/<type>.rubric.md` (+ `skill-ref` when Skill+Ref) | Inject into `compliance` Task |
| `rubrics/audit-redesign.rubric.md` | Inject into `opportunity` Task |
| `improvement-patterns.md` | Inject into `opportunity` Task |
| `templates/audit-output.template.md` | Shape SoT for render (compliance) |
| `templates/audit-redesign-output.template.md` | Shape SoT for render (opportunity) |
| `templates/reports/compliance.schema.json` | Inject into compliance Task (lean emit) |
| `templates/reports/opportunity.schema.json` | Inject into opportunity Task (lean emit) |
| `templates/reports/apply-plan.schema.json` | Parent merge lean emit |
| `templates/reports/README.md` | Lean-emit pattern (optional Read) |
| `templates/ce-report-lean.schema.md` | Index → per-kind schemas (redirect only) |
| `templates/improve-compliance-task.template.md` | `improve-2-parallel-audits` (compliance Task prompt) |
| `templates/improve-opportunity-task.template.md` | `improve-2-parallel-audits` (opportunity Task prompt) |
| `templates/improve-apply-plan.template.md` | `improve-3-merge` (markdown shape; prefer render) |
| `failure-patterns.md` | Inject into `compliance` Task (recommended) |
| `helper-cli.md` | Report render / touch-list git stage |
| `actions/fix.md` | `improve-4-apply-fix` |
| `actions/redesign.md` | `improve-5-apply-redesign` |
| `actions/shared-write-gates.md` | After apply drafts (one combined write approve + scoped git stage) |
| `gate-prompts.md` | `improve-3-merge` (**approve-apply-plan**); write gate; `improve-6-close` |
| `close-contract.md` | `improve-6-close` |
| Executors: `executors/compliance.md`, `executors/opportunity.md` | `improve-2-parallel-audits` (Read via Caller Load — not catalog agents) |

## Steps

### Step 1: `improve-1-load`

- **Outcome:** Target path and artifact type known; plugin root resolved; `<run-id>` chosen (short timestamp or uuid stem).
- **Done when:** Path resolved via `questioning.md` if missing (ambient “improve this” without a declared path → stop per skill exit conditions); type stated per `classify.md` (or assumption noted once); scratch dir path known; empty `touch-list.txt` created.
- **Banner:** `CE ► IMPROVE` per `ui-brand.md`.

### Step 2: `improve-2-parallel-audits`

- **Outcome:** Both diagnosis reports **persisted** (lean JSON + rendered markdown) and linked.
- **Done when:** In **one turn**, spawn two **`generalPurpose`** Tasks (wait for both). Do **not** use named catalog subagent types from `agents/`—these executors are skill refs only. Fill prompts from `templates/improve-compliance-task.template.md` and `templates/improve-opportunity-task.template.md` (required Caller Load fields + injected refs + **`emit: lean-json`**).
  1. **compliance** — template + `{ path, type, plugin_root }` + type rubric (+ skill-ref rubric if Skill+Ref) + `actions/audit.md` + `templates/reports/compliance.schema.json` (+ `failure-patterns.md`).
  2. **opportunity** — template + `{ path, type, plugin_root }` + `actions/audit-redesign.md` + `rubrics/audit-redesign.rubric.md` + `improvement-patterns.md` + `templates/reports/opportunity.schema.json` (+ optional compliance skim when already returned).
- Emit liveness before waits: `◆ Parallel audits (compliance + opportunity)…`.
- Collect **lean JSON** from each Task (status + payload). If either status is `failed`, stop with clarifications—do not apply.
- **Parent persist (no full-body Write):** write `compliance.json` / `opportunity.json`; run `scripts/render_ce_report.py` for each → `.md`. On exit **2**, fix JSON from stderr and re-run (never Write full `.md`). Chat: one-line status each + Verdict / ranked-count summary + **markdown links**. **read-budget:** do not re-paste full report bodies into chat or into agent `Write` tool args.

### Step 3: `improve-3-merge`

- **Outcome:** Unified apply list approved **before** any target mutation.
- **Done when:** Built from **persisted** lean JSON / rendered reports (not a second invent schema) and written via lean `apply-plan.json` + `render_ce_report.py apply-plan` (required **Reports** block + lean **Intent** per id):
  - **fix list:** every compliance Findings FAIL id (all severities) ∪ Ranked rows with Absorb `fix` (Impact high|medium)
  - **redesign list:** Ranked rows with Absorb `redesign` (Impact high|medium)
  - **Dropped:** Keep notes, Absorb `defer`, Deferred rows, Impact `low`
- Present in chat: link to `apply-plan.md` + Reports links + lane tables (no full report dump). Empty both lists → skip to `improve-6-close` with diagnosis-only Next Up (no write).
- **Gate:** **approve-apply-plan** per `gate-prompts.md`. Abort → no draft, no target Write, still close. Approve → continue to apply steps.

### Step 4: `improve-4-apply-fix`

- **Outcome:** Compliance FAILs + Absorb `fix` opportunities addressed with minimal same-intent edits **off target path**.
- **Done when:** If fix list empty → mark completed and continue. Else run `actions/fix.md` **Nested under improve** short path against the merged fix list (not the full standalone Steps 1–5). **Nested intake:** `fix-1-read` done-when satisfied from the merge plan—path + type already known; failure source = compliance Findings FAIL ids ∪ Ranked Absorb `fix` ids; skip AskQuestion for Missing failure source (`fix-intake.md`). **TodoWrite:** only `improve-1…6` — do not spawn `fix-*` todos.
- **stop-rule:** Do **not** Write/Edit the approved **target** plugin paths in this step. Hold draft in memory and/or under `.ai/learning/ce-improve/<run-id>/draft/`. Append intended promote paths to `touch-list.txt` as drafts are finalized. **Filesystem snapshot is not a goal** — optional only as intermediary to know/restore the touch list on Abort (see T3). Prefer draft-tree static over mutating live targets for the static gate.
- Produce draft only—**do not** run write gates yet if redesign list is non-empty (combine drafts). If redesign list empty → proceed to shared write gates on the fix draft before close.

### Step 5: `improve-5-apply-redesign`

- **Outcome:** Absorb `redesign` opportunities applied to the **draft** set (or skipped).
- **Done when:** If redesign list empty → mark completed. Else run `actions/redesign.md` **Nested under improve** short path against the redesign list. **Nested intake:** treat full `redesign-1-clarify` / `redesign-intake.md` done-when as satisfied from the merge plan—delta brief = Ranked Absorb `redesign` opportunity detail; skip **all** redesign-intake AskQuestions (outcome/audience/capabilities/failure modes/breaking-change); record breaking-change assumption once in the apply plan. **TodoWrite:** only `improve-1…6` — do not spawn `redesign-*` todos. Merge with any fix draft into one candidate artifact set; keep `touch-list.txt` complete.
- **Same stop-rule** as improve-4: no target-path promotion yet.
- **Gates:** Run `shared-write-gates.md` once on the combined **draft**. One **approve-revise-abort** for the whole plan — AskQuestion **must** include Reports + apply-plan + draft links. On **Approve** → promote draft → target paths → **scoped `git add --` paths in `touch-list.txt` only** (never `git add -A`). On **Abort** → discard draft / restore only if a restore intermediary was used; **target paths unchanged**; **no git stage**; still close with Next Up.

### Step 6: `improve-6-close`

- **Outcome:** User routed after improve.
- **Done when:** **post-improve-routing** AskQuestion per `gate-prompts.md`; follow-ups verb-only per `close-contract.md`. Close narrative cites **paths** to persisted reports (and apply-plan) — not full report bodies. Note whether scoped git stage ran.

## Stop

- No ambient improve without a declared path.
- Executors never Write; parent owns lean persist, **render script**, apply drafts, gates, and scoped git stage.
- Do not auto-apply Deferred / Keep / Absorb `defer` / Impact `low`.
- Do not spawn a third “write agent”; parent executes fix/redesign **Nested under improve** short paths.
- Nested apply: TodoWrite **only** `improve-1…6`; never nest `fix-*` / `redesign-*` todo lists.
- **No target-path Write before approve-apply-plan.** **No target-path promotion before Write-gate Approve.**
- **No `git commit` / forge PR from improve.** Scoped `git add` of touch list only after Approve promote.
- **read-budget:** never paste full compliance/opportunity reports into chat or agent `Write` when scratch + render script exist — link rendered files.
- **Snapshot is not a success criterion.**
