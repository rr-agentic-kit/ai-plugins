# Harness effectiveness (reference)

Loaded during **pre-write reflection** only (`pre-write-reflection.md`). Use with the type’s `*.audit-rubric.md` judgment rows—not a substitute for rubric ids.

## Reliable

- Every procedure step has an **observable** done condition or explicit stop (quote at least one).
- Write-blocking failures emit an explicit signal (`PRE-SHIP FAILED`, `PRE-WRITE REFLECTION FAILED`, or named stop)—not “try”, “if possible”, or silent continue.
- Required inputs missing → bounded behavior (ask once, stop, or route)—not open-ended guessing.

## Consistent

- No contradictory MUST/MUST NOT between **Purpose**, contracts, and **Procedure** (cite both sides if FAIL).
- Same terms for the same concept (input/output/stop) across sections.
- Delegated **Action** verb matches the artifact’s stated purpose (commands).
- Co-loaded refs do not restate the same constraint; each file in a **Load** chain contributes unique information.

## Deterministic

- Enumerable choices → structured question (AskQuestion) or fixed options—not “ask the user what they want” without bounds.
- **Output** shape pinned (report fields, write/stop outcomes, verdict rules).
- Conditional branches use observable predicates (“if path missing → ask once”); no “use judgment” without limits.

## Pre-write harness checks (ids)

Evaluate in `pre-write-reflection.md` step 4:

| id | Severity | PASS when |
|----|----------|-----------|
| `harness.reliable.done-stop` | critical | Every imperative step in Procedure/Progress has done/stop or cites single-shot N/A in one line |
| `harness.reliable.fail-signal` | critical | Failed gates block write with named failure label; no soft-fail language on ship path |
| `harness.consistent.contracts` | major | Inputs/outputs/stop rules align across frontmatter description, contracts, and body |
| `harness.consistent.no-cross-echo` | major | Artifact body does not restate constraints already present in files it loads; co-loaded refs do not duplicate each other |
| `harness.deterministic.inputs` | major | Missing required input behavior is explicit; enumerable forks use AskQuestion or fixed options |
| `harness.deterministic.output` | major | Success/failure outputs are verifiable without rereading the whole repo |
| `harness.deterministic.branches` | major | If/else branches use observable conditions; no unbounded discretion on ship path |
