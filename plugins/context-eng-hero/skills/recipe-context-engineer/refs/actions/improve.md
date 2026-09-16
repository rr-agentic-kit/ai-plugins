# Action: improve (internal)

Orchestrate **compliance audit** + **audit-redesign** in parallel, merge an apply list, then run **fix** then **redesign** under shared write gates. Agents do **not** invoke this skill; parent injects refs (Caller Load).

**Skip Advise** for this action (reports are the plan)—see `advisory.md`.

## Apply policy

Merge from the **markdown** reports only (no parallel JSON handoff). Template SoT: `templates/audit-output.template.md` (Verdict / Findings FAIL ids) and `templates/audit-redesign-output.template.md` (Ranked **Absorb** column + apply-consumer field contract).

Under write gates:

1. Compliance FAILs (all severities, from Findings) → **fix** first
2. Ranked opportunities with Absorb `fix` → **fix**
3. Ranked opportunities with Absorb `redesign` → **redesign**
4. **Skip:** Keep notes, Absorb `defer`, Deferred table, Impact `low`

One **approve-revise-abort** covers the combined apply plan (not per-opportunity spam)—`shared-write-gates.md`.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `improve-1-load` |
| `questioning.md` | `improve-1-load` (missing path; **Delivery channels**) |
| `classify.md` | `improve-1-load` (type) |
| `ui-brand.md` | `improve-1-load` (banner), parallel audits (liveness) |
| `actions/audit.md` | Inject into compliance Task |
| `actions/audit-redesign.md` | Inject into opportunity Task |
| `rubrics/<type>.rubric.md` (+ `skill-ref` when Skill+Ref) | Inject into compliance Task |
| `rubrics/audit-redesign.rubric.md` | Inject into opportunity Task |
| `improvement-patterns.md` | Inject into opportunity Task |
| `templates/audit-output.template.md` | Inject into compliance Task |
| `templates/audit-redesign-output.template.md` | Inject into opportunity Task |
| `failure-patterns.md` | Inject into compliance Task (recommended) |
| `actions/fix.md` | `improve-4-apply-fix` |
| `actions/redesign.md` | `improve-5-apply-redesign` |
| `actions/shared-write-gates.md` | After apply drafts (one combined approve) |
| `gate-prompts.md` | `improve-6-close` (**post-improve-routing**); write gate |
| `close-contract.md` | `improve-6-close` |
| Agents: `agents/audit/compliance.md`, `agents/audit/opportunity.md` | `improve-2-parallel-audits` |

## Steps

### Step 1: `improve-1-load`

- **Outcome:** Target path and artifact type known; plugin root resolved.
- **Done when:** Path resolved via `questioning.md` if missing (ambient “improve this” without a declared path → stop per skill exit conditions); type stated per `classify.md` (or assumption noted once).
- **Banner:** `CE ► IMPROVE` per `ui-brand.md`.

### Step 2: `improve-2-parallel-audits`

- **Outcome:** Both diagnosis reports available.
- **Done when:** In **one turn**, spawn two Task subagents (wait for both):
  1. **compliance** — `agents/audit/compliance.md`; inject `{ path, type, plugin_root }` + `actions/audit.md` + type rubric (+ skill-ref rubric if Skill+Ref) + `templates/audit-output.template.md` (+ `failure-patterns.md`).
  2. **opportunity** — `agents/audit/opportunity.md`; inject `{ path, type, plugin_root }` + `actions/audit-redesign.md` + `rubrics/audit-redesign.rubric.md` + `improvement-patterns.md` + `templates/audit-redesign-output.template.md` (+ optional compliance skim when already returned).
- Emit liveness before waits: `◆ Parallel audits (compliance + opportunity)…`.
- Collect the full markdown reports from each. If either status line is `failed`, stop with clarifications—do not apply.

### Step 3: `improve-3-merge`

- **Outcome:** Unified apply list ready for write paths.
- **Done when:** Built from report markdown (not a second schema):
  - **fix list:** every compliance Findings FAIL id (all severities) ∪ Ranked rows with Absorb `fix` (Impact high|medium)
  - **redesign list:** Ranked rows with Absorb `redesign` (Impact high|medium)
  - **Dropped:** Keep notes, Absorb `defer`, Deferred rows, Impact `low`
- Present a short combined apply plan (ids + absorb lane) before gates. Empty both lists → skip to `improve-6-close` with diagnosis-only Next Up (no write).

### Step 4: `improve-4-apply-fix`

- **Outcome:** Compliance FAILs + Absorb `fix` opportunities addressed with minimal same-intent edits.
- **Done when:** If fix list empty → mark completed and continue. Else run `actions/fix.md` procedure against the merged fix list (skip standalone fix banner/close; use IMPROVE context). Produce draft only—**do not** run write gates yet if redesign list is non-empty (combine drafts). If redesign list empty → proceed to shared write gates on the fix draft before close.

### Step 5: `improve-5-apply-redesign`

- **Outcome:** Absorb `redesign` opportunities applied (or skipped).
- **Done when:** If redesign list empty → mark completed. Else run `actions/redesign.md` procedure against the redesign list (skip standalone redesign close). Merge with any fix draft into one candidate artifact set.
- **Gates:** Run `shared-write-gates.md` once on the combined draft. One **approve-revise-abort** for the whole plan. On Abort → no write; still close with Next Up.

### Step 6: `improve-6-close`

- **Outcome:** User routed after improve.
- **Done when:** **post-improve-routing** AskQuestion per `gate-prompts.md`; follow-ups verb-only per `close-contract.md`. Surface both diagnosis reports (or paths/summaries) in the close narrative when useful.

## Stop

- No ambient improve without a declared path.
- Agents never Write; parent owns apply + gates.
- Do not auto-apply Deferred / Keep / Absorb `defer` / Impact `low`.
- Do not spawn a third “write agent”; parent executes fix/redesign procedures.
