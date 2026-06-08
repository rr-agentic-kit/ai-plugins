# rr-test

Flag-driven test excellence: one skill routes phase agents to assess quality, find gaps, write high-signal tests, fix failures, and triage flaky behavior. No command files; no mandatory artifact I/O.

**Runtime:** [SKILL.md](SKILL.md) · **Policies:** [refs/](refs/)

## Philosophy

- **High-signal tests** — Fail when protected behavior breaks (oracle validation). Fewer, stronger tests beat coverage padding.
- **Determinism** — Same inputs → same scope, ordering, routing.
- **Exhaustive per-epoch** — Every file in scope is assessed; every gap is identified; every plan step is executed. Multi-epoch flows default to 3 passes as a safety cap. Residuals at epoch cap indicate scope or skill failure, not a normal exit — re-run with higher `--max-epochs` or mark `wontfix`.

## How to run

One primary action flag + optional selectors. Explicit flags win on conflict ([refs/input-resolution.md](refs/input-resolution.md)).

| Selector | Values | Default |
|----------|--------|---------|
| `--scope` | `repo`, `diff`, `uncommitted`, `paths:<csv>` | `diff` |
| `--target` | `frontend`, `backend`, `devops`, `scripts`, `auto` | `auto` |
| `--output` | `md`, `text`, `json`, `report` (alias `md`) | `md` |
| `--max-epochs` | integer | `5` (multi-pass only; safety cap, not expected exit) |

## Common flows

```
rr-test --init
```
→ Stack discovery; writes `## rr-test Project Testing Context` to `CLAUDE.md`.

```
rr-test --assess --scope diff
```
→ Quality verdict for changed production code.

```
rr-test --identify-missing --scope paths:src/foo/Bar.java
```
→ Ranked missing-test findings.

```
rr-test --write-tests --target backend --scope paths:src/foo/Bar.java
```
→ Writes tests, runs green, oracle-validates.

```
rr-test --complete-missing-tests --scope diff --max-epochs 3
```
→ Full gap-closure loop until all findings resolved or epoch budget exhausted (`partial`).

```
rr-test --diagnose-flaky --scope paths:tests/foo/BarTest.java
```
→ Flaky cause and fix recommendation.

## Troubleshooting

- **Ambiguous action** — One primary flag per call; run `--init` separately.
- **Wrong scope** — Use `--scope diff` for PRs; `paths:...` for surgical runs.
- **Misclassified target** — Set `--target` explicitly instead of `auto`.
- **Partial exit at epoch cap** — Residual `flagged` findings remain; re-run with `--max-epochs N` or mark `wontfix` in constraints.

## Further reading

| Topic | Owner |
|-------|-------|
| Quick start | This file |
| Routing and phase chains | [SKILL.md](SKILL.md) |
| Flag parsing / conflicts | [refs/input-resolution.md](refs/input-resolution.md) |
| Phase schemas | [refs/contracts.md](refs/contracts.md) |
| Ordering / retries / exit | [refs/determinism.md](refs/determinism.md) |
| Output adapters | [refs/output-formats.md](refs/output-formats.md) |
| Verdict heuristics | [refs/shared-heuristics.md](refs/shared-heuristics.md) |
| Init workflow | [refs/init-mode.md](refs/init-mode.md) |
| CLAUDE.md testing section | [refs/claude-md-schema.md](refs/claude-md-schema.md) |
