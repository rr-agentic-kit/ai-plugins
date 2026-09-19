# Improvement patterns (audit-redesign taxonomy)

Use these labels in **audit-redesign** narrative opportunities. Parallel to `failure-patterns.md` (compliance FAIL taxonomy)—**do not** merge opportunity ids into type-rubric PASS/FAIL rows.

Map each opportunity to one primary pattern. Group bullets under one pattern when they share a root cause.

| Pattern | Meaning | Typical dimension ids |
|---------|---------|------------------------|
| **COHESION** | Unclear seams; mixed concerns; pack boundaries fuzzy | `imp.cohesion.seams` |
| **DISCLOSURE** | Wrong always-on vs progressive load; body/ref economics | `imp.disclosure.economics` |
| **FRAMING** | LLM-hostile wording; buried constraints; weak forcing functions | `imp.framing.llm` |
| **ORCHESTRATION** | Clarify/TodoWrite/close ergonomics costly or inconsistent | `imp.orchestration.ergonomics` |
| **FREEDOM** | Degrees of freedom mismatch (too rigid or too open) | `imp.freedom.fit` |
| **EVAL-LOOP** | Hard to audit/test/thicken from observed FAILs | `imp.eval.loop-fitness` |
| **LOAD** | Executor cognitive load; too many hops or decisions per turn | `imp.load.executor` |
| **SCRIPTABLE** | Agent forced to invent deterministic multi-step work (or dump→filter) a one-shot tool could return | `imp.load.executor` |
| **COLLISION** | Discovery overlap or sibling skill/command collision | `imp.discovery.sibling-collision` |

**Shared-knowledge examples** (same pattern labels; no new ids):

| Smell | Pattern |
|-------|---------|
| Echo of rubrics/output templates into agent body, or parallel JSON that restates Ranked/Findings | **COHESION** |
| Wrong always-on sub-skill used only to share static judgment/files | **DISCLOSURE** |
| Agent re-orchestrates / re-invokes parent skill for the same job | **LOAD** / **ORCHESTRATION** |
| Procedure makes the LLM mint/scan/allocate/parse via multi-step invent (registry ids, path walks) when a single CLI/script could emit the value | **SCRIPTABLE** |
| Shell/grep/find dumps large name lists into context for the LLM to filter, instead of emitting the needed value | **SCRIPTABLE** |

**Detect ≠ absorb:** Ranking **SCRIPTABLE** does **not** require `scripts/` on the skill today. Opportunity = the waste. Absorb (fix/redesign) separately chooses: point Procedure at an existing CLI, index a custom helper from the skill, or tighten stdout filters. When the waste is **report/scaffold paste** (large markdown tables, severity math, repeated report shapes), prefer the **Lean emit + schema + render** recipe in `helper-cli.md` / `templates/reports/README.md` over adding more prose procedure. Stock one-off `git`/`gh` calls are not auto-opportunities; custom repeated optimizations should be indexed from the skill when absorbed.

**Not compliance:** These are ranked improvement opportunities (Keep / Improve / Restructure), not ship-blocking FAILs. Compliance blockers belong in a skim section only—see `rubrics/audit-redesign.rubric.md`.

## Assessment quality (not compliance FAIL labels)

Use these when reviewing audit-redesign judgment quality (self-check, challenge notes, or learn-from-miss). They are **not** type-rubric FAIL ids.

| Label | Meaning |
|-------|---------|
| **NONDET** | Same evidence anchor flips omit / medium / high across runs |
| **FP-CRAFT** | Taste or compliance re-litigation emitted as opportunity |
| **FN-SKIP** | Dimension not scanned, or valid medium+observed dropped for count |
