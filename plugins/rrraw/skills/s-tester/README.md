# s-tester

Flag-driven test excellence lane for **rr-builder**.

## Why

Test assess/write/fix/migrate/flaky work needs deterministic routing to `agents/test/*` with exhaustive per-epoch scope coverage. Done when status + findings match the action contract and verify/oracle gates pass.

## What

Normalizes test flags into a canonical payload, delegates to one phase agent or chain, and formats output. Skill owns routing and epoch loops; agents execute one phase each.

**Out of scope:** production design (**s-coder**); OWASP (**s-security**); review orchestration (**s-review**).

## When

### Use when

- `--init`, `--assess`, `--complete-missing-tests`, `--fix-broken-tests`, `--migrate-tests`, `--diagnose-flaky`, or other primary test flags via **rr-builder** `--tester`
- Test lane under **s-review**; builder orchestrate **plan** (knowledge) / **build** (full skill with s-coder; drive/scope per parent)

### Avoid when

- Production code standards only → **s-coder**
- OWASP / secrets audit → **s-security**
- MR inline POST alone → **s-ci** after **s-review** `--ci`

## Philosophy

- **High-signal tests** — fail when protected behavior breaks (oracle validation)
- **Non-testable → exclude** — type-only, generated, barrel files get coverage exclusion
- **Determinism** — same inputs → same scope, ordering, routing
- **Exhaustive per-epoch** — every file in scope assessed; residuals at epoch cap → `partial`

## UX

### Invoke

Via **rr-builder** `--tester` (or nested test flags under that handoff), **s-review** test lane, or parent **Read** on orchestrate plan/build stages.

### Intake

Flag parse → canonical payload per `refs/input-resolution.md` (conflict matrix authoritative there).

### Clarify

Ambiguous primary action or conflicting flags → stop or AskQuestion once; do not invent a second primary.

### Output

Structured assess/write/fix/migrate/flaky results via `refs/output-formats.md`.

### Close

Determinism hooks block completion on verify/oracle failure; epoch residuals surface as `partial`.

## Constraints

- Exactly one primary action (or `--init` exclusivity)
- Defaults: `--scope diff`, `--target auto`, `--output md`, `--max-epochs 3`
- Agent paths: `agents/test/*` relative to plugin root (`refs/agent-index.md`)
- `disable-model-invocation: true`

## Notes

Language refs load on demand: `refs/java-test.md`, `python-test.md`, `react-test.md`, `vue-test.md`, `playwright.md`.
