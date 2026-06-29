# research

Function-style executor for post-composition market evaluation. Non-interactive — returns cited findings and refinement signals.

## Input

`PhaseInput` with `phase: "research"`.

Required context:

- `payload.output_dir`
- Composed docs in `output_dir` (exec-summary through frd as available)
- `session_state.assumptions` (prioritize unvalidated)
- Load [research-method.md](../../skills/rr-planner/refs/research-method.md) for methodology
- Load [contracts.md](../../skills/rr-planner/refs/contracts.md) § research for output schema

## Execution

1. Read all planning docs from `payload.output_dir`.
2. Extract claims, assumptions, and gaps needing external validation.
3. Plan research queries per iteration (3–5 queries each).
4. Execute web searches; collect citations per research-method format.
5. Synthesize findings with `impact`: confirms | contradicts | extends.
6. Emit `refinement_signals` for affected doc sections.
7. For contradictions research cannot resolve → `clarifications_needed[]`.
8. Repeat until no new material findings and user confirms done, or user stops.

## Output

`PhaseOutput` with `data` per [contracts.md](../../skills/rr-planner/refs/contracts.md) § research.

| `status` | When |
|----------|------|
| `ok` | Research complete; no blocking clarifications |
| `partial` | User stopped or unresolved clarifications |
| `failed` | No docs found in output_dir |

## Constraints

- **Non-interactive** — return `clarifications_needed[]` instead of prompting.
- **Cited findings only** — no unsourced factual claims.
- Do not modify planning docs — findings and refinement signals only.
- Broader than discovery-time searches; follows research-method iterative loop.
