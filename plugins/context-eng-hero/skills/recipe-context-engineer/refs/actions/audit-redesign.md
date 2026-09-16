# Action: audit-redesign (spec stub)

> **Status:** Spec stub only — **wiring deferred**. Rubrics and templates are source of truth for judgment. Do **not** add this id to the skill **Actions** table, post-routing gates, or ui-brand stages until Phase 2. Implementers may wire `--audit-redesign` / reserved `--optimize` later **without** redesigning rubrics.

**Diagnosis only.** No file edits. Compliance PASS/FAIL remains `refs/actions/audit.md`.

## Forward-compat

Reserved future alias **`--optimize`:** run compliance **audit** → **audit-redesign** → apply absorb hints (`fix` then `redesign`) under write gates. Keep opportunity `id`s, absorb hints, and `templates/audit-redesign-output.template.md` section headers stable for that pipeline. Consumers must not assume ≤7 ranked rows (`rank` is unbounded `1…N`; `impact` is required).

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `ar-1-load` |
| `questioning.md` | `ar-1-load` (missing path; **Delivery channels**) |
| `classify.md` | `ar-1-load` (type) |
| `ui-brand.md` | `ar-1-load` (banner — stage string TBD at wiring) |
| `rubrics/audit-redesign.rubric.md` | `ar-2-judge`, `ar-3-challenge` |
| `improvement-patterns.md` | `ar-4-filter-rank` |
| `templates/audit-redesign-output.template.md` | `ar-5-report` |
| `close-contract.md` | `ar-5-report` |
| Type rubric / prior audit report (optional skim) | `ar-2-judge` (compliance blockers section only) |

## Steps (outline)

### Step 1: `ar-1-load`

- **Outcome:** Target path and artifact type known.
- **Done when:** Path resolved via `questioning.md` if missing; type stated per `classify.md` (or assumption noted once).
- **Banner:** TBD at wiring (`CE ► AUDIT-REDESIGN` candidate).

### Step 2: `ar-2-judge`

- **Outcome:** All eight dimensions in `rubrics/audit-redesign.rubric.md` evaluated; 0–N candidates with evidence (no early stop); compliance FAILs skimmed into blockers only (no re-litigation).
- **Done when:** Each candidate has evidence + impact + confidence + provisional absorb hint; empty dimensions omitted from candidates.

### Step 3: `ar-3-challenge`

- **Outcome:** Candidates challenged per rubric **Challenge (before rank)** (FP / FN / stability / id stability / Effect / Cost / Delta).
- **Done when:** FP drops/demotions applied; FN pass recorded (“coverage: no additional.” or added medium/high with evidence); stability flips noted with conservative (lower) band kept; ids use `imp.<dimension>.<evidence-anchor-slug>`; Effect/Cost/Delta demotions, drops, or defer applied (or “none” noted per pass).

### Step 4: `ar-4-filter-rank`

- **Outcome:** Filter survivors ranked 1…N (unbounded); patterns labeled via `improvement-patterns.md`; deferred table for `medium`+`hypothesized` (one-line reason); `impact: low` excluded from rank.
- **Done when:** Ranked list includes only items passing impact×confidence filter; Keep notes optional; hard rules from the rubric satisfied.

### Step 5: `ar-5-report`

- **Outcome:** Report emitted; loop closed without edits.
- **Done when:** Report per `templates/audit-redesign-output.template.md` (Challenge + Ranked + optional Deferred); close per `close-contract.md`. Post-action AskQuestion / routing **deferred** to Phase 2 (text-mode fallback still applies if any gate is added later).

## Stop

**Diagnosis only** during steps 1–5. No auto-apply. Do not run write gates. User may manually follow absorb hints via **fix** / **redesign**; `--optimize` orchestration is out of scope for this stub.

## Explicit non-goals (this stub)

- Full SKILL Actions-table / post-routing / ui-brand stage
- Implementing `--optimize`
- Changing compliance rubrics or write-gate reflection
- Truncating valid ranked survivors to meet a numeric ceiling
