# rr-planner

Flag-driven software planning docs: progressive top-down discovery from vision through functional requirements, with compose, research, and challenge phases. No command files; NL + flag driven.

**Runtime:** [SKILL.md](SKILL.md) · **Policies:** [refs/](refs/)

## Philosophy

- **Progressive cascade** — Exec summary → MRD → BRD → PRD → FRD; each level inherits and narrows the one above.
- **Goal-anchored** — Disambiguate vague input, clarify before assuming, capture nuance; every decision traces to stated goals.
- **Proactive discovery** — Auto-reflection and lightweight challenge baked into discovery; broad market research deferred to post-composition.
- **Interactive discovery, non-interactive agents** — Skill owns question loops (`AskQuestion` by default, `--text-mode` for inline); compose/research/challenge agents return `clarifications_needed[]`.
- **Stop and resume** — Pause anytime; state checkpoints to `session-state.json`; `--resume` continues where you left off.

## How to run

One primary action flag + optional selectors. Explicit flags win on conflict ([refs/input-resolution.md](refs/input-resolution.md)).

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file or directory | conversation context |
| `--output-dir` | directory path | `docs/planning/` |
| `--format` | `md`, `json` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag)_ | off — load `session-state.json` from output-dir |

## Common flows

```
rr-planner --discover
```
→ Full top-down cascade with interactive discovery; writes all docs to `docs/planning/`.

```
rr-planner --prd --input "Build a team analytics dashboard for engineering managers"
```
→ Discovery + compose for exec-summary through PRD only.

```
rr-planner --research --output-dir docs/planning/
```
→ Post-composition market evaluation with cited findings.

```
rr-planner --challenge --output-dir docs/planning/
```
→ Devil's-advocate review of existing planning docs.

```
rr-planner --discover --text-mode
```
→ Questions asked inline in chat instead of structured `AskQuestion` prompts.

```
rr-planner --resume --output-dir docs/planning/
```
→ Continue a paused session from checkpoint.

```
rr-planner --discover --depth deep
```
→ Full cascade + mandatory research + challenge pass.

## Output artifacts

| File | Content |
|------|---------|
| `exec-summary.md` | Vision, problem, why now |
| `mrd.md` | Market context |
| `brd.md` | Business requirements |
| `prd.md` | Product requirements |
| `frd.md` | Functional requirements with Gherkin acceptance criteria |
| `session-state.json` | Checkpoint for stop/resume (decisions, facts, current level) |
| `session-log.md` | Decisions, assumptions, clarification history |
| `research-report.md` | Cited market findings (when research runs) |
| `challenge-report.md` | Blind-spot findings (when challenge runs) |

## Troubleshooting

- **Ambiguous action** — One primary flag per call; `--discover` and `--challenge` are mutually exclusive.
- **Partial docs** — Say "stop" or "pause" to checkpoint; resume with `--resume`. Answer pending clarification questions to advance.
- **Missing parent docs for challenge/research** — Run `--discover` first or point `--input` at existing docs.
- **Traceability failures** — Re-run focused level (e.g. `--frd`) after fixing parent docs.

## Further reading

| Topic | Owner |
|-------|-------|
| Quick start | This file |
| Routing and cascade | [SKILL.md](SKILL.md) |
| Flag parsing / conflicts | [refs/input-resolution.md](refs/input-resolution.md) |
| Level order and gates | [refs/cascade.md](refs/cascade.md) |
| Phase schemas | [refs/contracts.md](refs/contracts.md) |
| Doc structures | [refs/doc-standards/](refs/doc-standards/) |
| Success gate | [refs/success-criteria.md](refs/success-criteria.md) |
| Output adapters | [refs/output-formats.md](refs/output-formats.md) |
