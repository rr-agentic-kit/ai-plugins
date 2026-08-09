# challenge

Function-style executor for `--challenge` / `--review` on existing planning docs. Non-interactive critique using blind-spot taxonomy.

## Input

`PhaseInput` with `phase: "challenge"`.

Required context:

- `payload.input` or `payload.output_dir` — location of existing docs
- All available planning docs (exec-summary through frd)
- `session_state` if available (decisions, assumptions)
- Load [blind-spots.md](../../skills/rr-planner/refs/blind-spots.md) for taxonomy and severity rules
- Load [contracts.md](../../skills/rr-planner/refs/contracts.md) § challenge for output schema

## Execution

1. Load all planning docs from input or output-dir.
2. Scan each doc against full blind-spot taxonomy:
   - Stakeholder gaps, failure modes, non-functional, operational, competitive, economic, temporal, assumption debt, traceability breaks, negative space.
3. For major decisions with single option → produce comparison table with alternatives.
4. Apply devil's-advocate prompts systematically.
5. Classify each finding by severity: critical | high | medium | low.
6. Check traceability chain (fr → prd → brd → exec) for breaks.
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
