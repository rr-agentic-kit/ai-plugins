# Action: audit-redesign (internal)

**Diagnosis only.** Ranked Keep/Improve/Restructure opportunities—no file edits. Compliance PASS/FAIL remains `refs/actions/audit.md`. Apply orchestration is owned by **improve** (`refs/actions/improve.md`).

## Apply-consumer contract

Opportunity field names, absorb hints, and `templates/audit-redesign-output.template.md` section headers are stable for **`--improve`**. Consumers must not assume ≤7 ranked rows (`rank` is unbounded `1…N`; `impact` is required). Skip Keep notes, `absorb: defer`, Deferred, and `impact: low` when applying.

**Detect ≠ absorb:** Ranked opportunities may include **SCRIPTABLE** waste (deterministic invent or context-bloating shell/list) even when the skill has no `scripts/` yet. Summary/Why = detection; Suggested direction + `absorb` = how to improve (point Procedure at CLI/helper/filtered stdout). Do not treat “no helper-cli” as a compliance-style blocker or as the opportunity itself.

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `ar-1-load` |
| `questioning.md` | `ar-1-load` (missing path; **Delivery channels**) |
| `classify.md` | `ar-1-load` (type) |
| `ui-brand.md` | `ar-1-load` (banner) |
| `rubrics/audit-redesign.rubric.md` | `ar-2-judge`, `ar-3-challenge` |
| `improvement-patterns.md` | `ar-4-filter-rank` |
| `templates/audit-redesign-output.template.md` | `ar-5-report` |
| `gate-prompts.md` | `ar-5-report` (**post-audit-redesign-routing**) |
| `close-contract.md` | `ar-5-report` |
| Type rubric / prior audit report (optional skim) | `ar-2-judge` (compliance blockers section only) |

## Steps

### Step 1: `ar-1-load`

- **Outcome:** Target path and artifact type known.
- **Done when:** Path resolved via `questioning.md` if missing; type stated per `classify.md` (or assumption noted once).
- **Banner:** `CE ► AUDIT-REDESIGN` per `ui-brand.md`.

### Step 2: `ar-2-judge`

- **Outcome:** All eight dimensions in `rubrics/audit-redesign.rubric.md` evaluated; 0–N candidates with evidence (no early stop); compliance FAILs skimmed into blockers only (no re-litigation).
- **Done when:** Each candidate has evidence + impact + confidence + provisional absorb hint; empty dimensions omitted from candidates.

### Step 3: `ar-3-challenge`

- **Outcome:** Candidates challenged per rubric **Challenge (before rank)** (FP / FN / stability / id stability / Effect / Cost / Delta).
- **Done when:** FP drops/demotions applied; FN pass recorded (“coverage: no additional.” or added medium/high with evidence) **including** explicit scriptable + context-bloat walks (or “scriptable/context-bloat: none”); stability flips noted with conservative (lower) band kept; ids use `imp.<dimension>.<evidence-anchor-slug>`; Effect/Cost/Delta demotions, drops, or defer applied (or “none” noted per pass)—Cost must not demote SCRIPTABLE solely for introducing an indexed helper.

### Step 4: `ar-4-filter-rank`

- **Outcome:** Filter survivors ranked 1…N (unbounded); patterns labeled via `improvement-patterns.md`; deferred table for `medium`+`hypothesized` (one-line reason); `impact: low` excluded from rank.
- **Done when:** Ranked list includes only items passing impact×confidence filter; Keep notes optional; hard rules from the rubric satisfied.

### Step 5: `ar-5-report`

- **Outcome:** Report emitted; loop closed without edits.
- **Done when:** Report per `templates/audit-redesign-output.template.md` (Challenge + Ranked + optional Deferred); **post-audit-redesign-routing** AskQuestion per `gate-prompts.md`; follow-ups verb-only per `close-contract.md`.

## Stop

**Diagnosis only** during steps 1–5. No auto-apply. Do not run write gates. User may absorb via **fix** / **redesign** from the routing gate, or run **improve** for parallel audits + gated apply.

## Explicit non-goals

- Auto-applying opportunities (owned by **improve**)
- Changing compliance rubrics or write-gate reflection
- Truncating valid ranked survivors to meet a numeric ceiling
