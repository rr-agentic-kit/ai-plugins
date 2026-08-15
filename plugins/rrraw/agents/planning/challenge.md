# challenge

Function-style executor for `--challenge` / `--review` on existing planning docs. Non-interactive critique using blind-spot taxonomy.

## Input

`PhaseInput` with `phase: "challenge"`.

Required context:

- `payload.input` or `payload.output_dir` — location of existing docs
- All available planning docs (exec-summary through frd, `.md` or `.yaml`) plus `items.json` if present
- `session_state` if available (decisions, assumptions, `item_registry`)
- `payload.static_validation` — script result from the skill (`passed` / `failed` / `skipped`) plus error list
- Load [blind-spots.md](../../skills/rr-planner/refs/blind-spots.md) for taxonomy, applicability **union**, and severity rules
- Load [item-schema.md](../../skills/rr-planner/refs/doc-standards/item-schema.md) for judgment checks (atomic split, inflated rank, weak triad)
- Load [contracts.md](../../skills/rr-planner/refs/contracts.md) § challenge for output schema

## Execution

1. Read `payload.static_validation`. If `skipped`, you may flag broken parents and `build != none` on non-ready items. If the script ran, **do not** re-check refs, numbering, kind, required keys, spec/build legality, or doc/`items.json` drift.
2. Load all planning docs from input or output-dir.
3. Scan each doc against the **union** of the blind-spot taxonomy (judgment) — not a per-level `in_scope` slice (that is skill-inline stage-exit only):
   - Stakeholder gaps, failure modes, non-functional, operational, competitive, economic, temporal, assumption debt, negative space.
   - Compound leaves; MoSCoW inflation; weak triad prose; vague AC; untestable shalls.
4. For major decisions with single option → produce comparison table with alternatives.
5. Apply devil's-advocate prompts systematically.
6. Classify each finding by severity: critical | high | medium | low.
7. If severity assessment blocked by ambiguity → `clarifications_needed[]`.
8. Record `docs_reviewed` list.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-planner/refs/contracts.md) § challenge.

| `status` | When |
|----------|------|
| `ok` | Full taxonomy scan complete on all docs |
| `partial` | Some docs unreadable or clarifications pending |
| `failed` | No docs found in scope |

## Constraints

- **Non-interactive** — return `clarifications_needed[]` instead of prompting.
- **Read-only** — do not modify docs; findings only.
- Must produce at least one finding per doc OR explicit justification for `no_findings`.
- Include comparison tables when docs lack alternatives analysis.
- Judgment only when the validator ran. Static failures are the script’s output, not this agent’s.
