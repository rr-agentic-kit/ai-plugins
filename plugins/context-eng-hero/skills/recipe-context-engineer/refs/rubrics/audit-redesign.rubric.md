# Audit-redesign rubric (improvement opportunities)

Diagnosis-only judgment for **improvement** quality—not compliance PASS/FAIL. Compliance remains `rubrics/<type>.rubric.md` + `scripts/audit_static.py` via the **audit** action.

Map each opportunity to a label in `improvement-patterns.md`. Output shape: `templates/audit-redesign-output.template.md`. Procedure: `actions/audit-redesign.md`.

**Stable ids:** Dimension and opportunity field names below are reserved for the **`--improve`** pipeline (compliance audit → audit-redesign → absorb `fix` then `redesign`). Do not rename without a migration note. **Migration:** `rank` is unbounded `1…N`; `impact` is a required field (`high` \| `medium` \| `low`); the former “max 7” cap is retired—`--improve` consumers must not assume ≤7 rows.

## Success / anti-goals

- **One-shot assessment:** treat this judgment as the only/final pass—maximize recall of medium+ opportunities now. Do **not** plan on “re-run until clean”; there is no assumed follow-up audit-redesign to catch misses.
- **Primary:** high recall of real Improve/Restructure opportunities; **after challenge, no false positives** (no evidence-free, compliance re-litigation, or taste-as-opportunity). Stated success ≈100% recall and 0 FP after challenge; perfect recall is asymptotic—closest means thorough dimension coverage + explicit FN challenge, not a hard count cap.
- **Anti-goal:** truncating valid medium+observed items to meet a count; treating assessment as iterative polish loops.
- **Acceptable:** similar reports when re-assessed later (consistency); same item medium vs high once.
- **Unacceptable:** same evidence anchor omitted one assessment, medium another, high a third (NONDET)—consistency failure, not a cue to iterate.

## Hard rules

1. **No re-litigation of compliance FAILs** — do not restate type-rubric or static FAILs as opportunities; list unresolved compliance issues only under **Compliance blockers** (skim).
2. **Evidence-or-drop** — every opportunity cites observable evidence (path + section/quote) or is discarded. `observed` requires path + section/quote; otherwise force `hypothesized` or drop.
3. **Thorough scan, quality filter, unbounded rank** — evaluate all eight dimensions; emit 0–N candidates with evidence (no early stop at N). Ranked list includes only opportunities that pass both:
   - `impact` ∈ `{high, medium}`
   - `confidence` = `observed`, **or** (`impact` = `high` **and** `confidence` = `hypothesized`)
   - `impact: low` never ranks; `medium` + `hypothesized` goes to optional **Deferred** (not ranked), with one-line reason.
   - Remaining items ranked 1…N by `(impact, confidence)` then severity of evidence (`high`+`observed` first). No upper bound.
4. **Absorb hint** — each opportunity sets `fix` | `redesign` | `defer` (hint only; this action does not apply).
5. **Confidence** — each opportunity sets `observed` | `hypothesized`.
6. **No mega-FAIL on craft** — framing/taste never becomes a compliance FAIL id.
7. **Challenge before rank** — run **Challenge (before rank)** on all candidates before filter/rank; do not emit the ranked table until FP/FN/stability/id **and** Effect/Cost/Delta passes complete.

## Impact bands (discrete)

| `impact` | Assign when |
|----------|-------------|
| `high` | Wrong seam/outcome/disclosure/orchestration would cause repeated wrong behavior or high invoke cost if left alone |
| `medium` | Real craft/ergonomics gap; same contracts survive but executor reliability or load clearly improves |
| `low` | Taste, polish, or speculative nicety without observable executor cost |

**No** `medium-high` / half-bands. Drift of medium↔high on a borderline item is acceptable; **ignore vs medium vs high across independent assessments is a consistency failure** (not a reason to re-run this action until scores stabilize).

## Stance per finding

| Stance | Use when |
|--------|----------|
| **Keep** | Current shape is fit; note why (optional in report Keep list) |
| **Improve** | Same outcome/contracts; tighten wording, disclosure, or ergonomics (`absorb: fix`) |
| **Restructure** | Seams, outcome, audience, or capability boundaries should change (`absorb: redesign`) |

`defer` = real opportunity kept out of ranked absorb priority (out of scope for this target, or low ROI vs higher-ranked items)—still record so one-shot recall stays high; not “park for a later assessment cycle.”

## Dimensions (Judgment)

Evaluate each dimension. Emit 0–N candidates with evidence; omit empty dimensions from the ranked list. Do not stop early to meet a count.

### Cohesion / seams — `imp.cohesion.seams`

| Field | Rule |
|-------|------|
| **Look for** | Mixed concerns in one artifact; unclear SKILL vs ref vs companion boundaries; duplicate ownership; agent body echoing linked rubrics/templates or parallel JSON restating Ranked/Findings |
| **Improve when** | Seams exist but are muddy; split or rename without changing outcome |
| **Restructure when** | Wrong pack architecture (e.g. Skill+Ref needed, or ref should be inlined) |

### Disclosure economics — `imp.disclosure.economics`

| Field | Rule |
|-------|------|
| **Look for** | Always-on body bloated; critical constraints buried in refs; refs that should be body (or reverse); always-on sub-skill used only to share static judgment/files |
| **Improve when** | Move/compress content without contract change |
| **Restructure when** | Progressive-disclosure topology is wrong for invoke cost |

### LLM framing — `imp.framing.llm`

| Field | Rule |
|-------|------|
| **Look for** | Vague MUST language; buried stop rules; weak forcing functions; noise that dilutes constraints |
| **Improve when** | Same contracts, clearer operational wording |
| **Restructure when** | Procedure shape itself fights reliable execution |

### Orchestration ergonomics — `imp.orchestration.ergonomics`

| Field | Rule |
|-------|------|
| **Look for** | Clarify/TodoWrite/close paths costly; stacked gates; agent re-orchestrates parent skill instead of single-shot return |
| **Improve when** | Same forks, cheaper delivery |
| **Restructure when** | Gate graph or close surface should change |

### Degrees-of-freedom fit — `imp.freedom.fit`

| Field | Rule |
|-------|------|
| **Look for** | Over-scripted judgment work or under-constrained irreversible steps (see `design/design-core.md`) |
| **Improve when** | Local tighten/loosen |
| **Restructure when** | Freedom band for the whole artifact is wrong |

### Eval-loop fitness — `imp.eval.loop-fitness`

| Field | Rule |
|-------|------|
| **Look for** | Hard to audit/test; no observable done-when; cannot thicken from FAIL |
| **Improve when** | Add probes/evidence hooks without outcome change |
| **Restructure when** | Action/report contracts block eval-first loops |

### Executor cognitive load — `imp.load.executor`

| Field | Rule |
|-------|------|
| **Look for** | Too many hops, tables, or decisions per turn; Ref index overload; agent re-invokes parent orchestrator for the same job; **scriptable waste** — procedure forces LLM through deterministic multi-step algorithms (mint/scan/allocate/parse) a one-shot tool could return; **context-bloating shell/list** — grep/find/awk/sed (or equivalent) dumps large listings for the LLM to filter instead of emitting the needed value |
| **Improve when** | Compress load path; or (absorb separately) point Procedure at filtered CLI / custom helper indexed from the skill — do **not** treat “no `scripts/` yet” as absence of opportunity |
| **Restructure when** | Action surface should split or merge |

**SCRIPTABLE (pattern):** Prefer label **SCRIPTABLE** when the evidence is invent-or-dump waste above; still use dimension `imp.load.executor`. Skills need **no** existing `scripts/` or helper-cli for this opportunity to rank.

### Discovery / sibling collision — `imp.discovery.sibling-collision`

| Field | Rule |
|-------|------|
| **Look for** | `description` overlaps siblings; false triggers; competing slash/skill names |
| **Improve when** | Narrow description / anti-triggers |
| **Restructure when** | Ownership between siblings should change |

## Challenge (before rank)

Mandatory internal pass after candidates exist and **before** filter/rank. Mirror deep-reflect discipline (invoker/failure/ambiguity mindset) without loading `pre-write-reflection.md`. Emit a short Challenge block in the report (or immediately above the ranked table). Completeness requires all seven passes—this is the quality gate for one-shot recall, not a prelude to another assessment loop.

1. **FP pass** — for each candidate: would a second agent reject for weak evidence, compliance echo, or taste? Drop or demote impact/confidence. Do **not** FP-drop SCRIPTABLE solely because `scripts/` is absent (absence is allowed; opportunity is the waste).
2. **FN pass** — walk each dimension again; **also** walk: (a) any deterministic multi-step invent that is easily scriptable? (b) any shell/list step that bloates context instead of returning the needed value? List missed medium/high with evidence, or write “coverage: no additional.” (include “scriptable/context-bloat: none” when both walks are empty).
3. **Stability pass** — re-apply impact/confidence tables to every survivor; if score would change, keep the **lower** impact / weaker confidence (conservative) and note the flip.
4. **Id stability** — `id` derived from `imp.<dimension>.<evidence-anchor-slug>` so independent assessments collide on the same slug when evidence matches.
5. **Effect pass** — for each candidate: if left alone, how much does this change executor output or wrong-behavior risk? Demote impact or drop if the effect is speculative or taste-only.
6. **Cost pass** — compare status-quo invoke/token/hop load vs the proposed absorb. Demote if the “fix” adds load without proportional reliability gain. Do **not** demote SCRIPTABLE only because absorb would *introduce* a helper — weigh status-quo invent/dump cost vs one indexed invoke.
7. **Delta pass** — how much would the suggested Improve/Restructure actually improve vs status quo? Drop or set `absorb: defer` if the delta is marginal.

## Opportunity record (required fields)

| Field | Values / rule |
|-------|----------------|
| `id` | Stable slug: `imp.<dimension>.<evidence-anchor-slug>` (unique in report; collide across independent assessments when evidence matches) |
| `dimension` | One of the eight dimension ids above |
| `pattern` | Label from `improvement-patterns.md` (use **SCRIPTABLE** when invent/dump waste is the primary smell) |
| `stance` | `Keep` \| `Improve` \| `Restructure` (ranked list uses Improve/Restructure only) |
| `evidence` | Path + section/quote; else drop |
| `impact` | `high` \| `medium` \| `low` (discrete bands only) |
| `confidence` | `observed` \| `hypothesized` |
| `absorb` | `fix` \| `redesign` \| `defer` — **how to improve**, not the detection itself |
| `rank` | Unbounded `1…N` among filter survivors (1 = highest priority); omit for Deferred / dropped |

**Detect vs absorb (field split):**

| Report field | Owns |
|--------------|------|
| Summary / Why it matters | **Detect** — name the waste (invent steps, context dump, token/hop cost) |
| Suggested direction / Absorb hint | **Improve** — how to cut it (point at existing CLI; index custom helper from skill; filter stdout→value). Not “missing scripts/” as the opportunity. |

## Explicit non-goals

- Replacing compliance rubrics or write-gate reflection
- Auto-applying opportunities (owned by **improve**)
- Truncating valid ranked survivors to meet a numeric ceiling
