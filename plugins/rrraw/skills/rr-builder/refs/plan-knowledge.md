# Plan-stage knowledge allowlist

**Audience:** `rr-builder` orchestrate **plan** stage only. Fixed Read set — do **not** dump rr-coder/rr-tester full Required Knowledge or language matrices.

## Always Read (in order)

1. [feature-branch.md](feature-branch.md) — ensure `feat/{NNNN}-{step}-{short-desc}` **before** writing the plan
2. [../rr-coder/refs/code.principles.md](../rr-coder/refs/code.principles.md)
3. [../rr-tester/refs/shared-heuristics.md](../rr-tester/refs/shared-heuristics.md)
4. [../rr-tester/refs/contracts.md](../rr-tester/refs/contracts.md)
5. [plan-schema.md](plan-schema.md) — output shape before writing the step plan

## Conditional (one hop, only when predicate holds)

| When | Read |
|------|------|
| Task cites architecture / ADR / layered seams (AR-relevant) | [../rr-coder/refs/architecture.md](../rr-coder/refs/architecture.md) |
| Step verify needs deterministic fixtures / seed rules | [../rr-tester/refs/determinism.md](../rr-tester/refs/determinism.md) |

## Do not load on plan

- rr-coder / rr-tester full `SKILL.md` Procedures (implement / test excellence runs)
- Language / framework matrix under `rr-coder/refs/` (java, typescript, react-*, …)
- Review-only packs: `compliance-rubric.md`, `severity-triage.md`, `observability.md` (unless this turn is review — it is not)
- `testability.md` (build/implement seam — load under **build**)

## Stop

If the step cannot be planned from this allowlist, record the gap under plan **Open risks** / **Non-goals** and stop — do **not** expand the allowlist ad hoc in the same turn.
