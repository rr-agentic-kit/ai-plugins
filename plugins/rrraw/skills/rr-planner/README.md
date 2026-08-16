# rr-planner

Flag-driven software planning docs: progressive top-down discovery from vision through functional requirements, with compose, research, and challenge phases. No command files; NL + flag driven.

**Human index only.** Runtime policy is [SKILL.md](SKILL.md) + [refs/](refs/) — not this file.

## Philosophy

- **Progressive cascade** — Posture gate (including `domain_context`), then Exec summary → MRD → BRD → PRD → FRD; each level inherits and narrows the one above.
- **Item contract** — Hierarchical `{DOC}-{n.m}` ids, immediate parent pointer, atomic leaves; ranking is per layer (MoSCoW / Kano / FRD triad), not P0. MoSCoW *legend* follows project posture (Must is not always MVP). Spec vs build are separate axes. Ranked leaves carry a `_rationale_` pointer.
- **Goal-anchored** — Unclear and ambiguous statements are blocking; clarify before recording facts; every decision traces to stated goals. Reason-graph (evidence, `flips_when`, burial) lives in `decision-ledger.yaml`, not the decision log.
- **Expert panel** — Seats argue both sides; a blocking seat owes an alternative. Verdict is a state (`proceed` … `kill`), not an exit. Binding at exec-summary and MRD; `market_type: internal` skips TAM.
- **Decision ledger** — Items rest on rationales, rationales rest on evidence. Invalidation raises a re-decision queue; it never auto-flips status. Buried ids are reserved and never recycled.
- **Off-level answers** — A feature mentioned during vision parks on the affected doc (`{level}.notes.yaml`), not as an exec-summary assumption. The sidecar is transient: gone when that doc's notes are resolved.
- **Proactive discovery** — Premise test inside exec-summary; stage-exit blind-spots then Gate 7 viability before freeze; claim-class search budgets; write-time pre-save blocks on an open queue or unresolved binding `hold`/`kill`.
- **Interactive discovery, non-interactive agents** — Skill owns question loops (`AskQuestion` by default, `--text-mode` for inline); compose persists `{level}.md` + `items.json` and returns a slim receipt; research/challenge return findings JSON.
- **Stop and resume** — Pause anytime; state checkpoints to `session-state.json`; Q&A appends to `raw-history/`; `--resume` sweeps the ledger then continues. Confirmed posture is not re-asked.

## How to run

One primary action flag + optional selectors. Explicit flags win on conflict ([refs/input-resolution.md](refs/input-resolution.md)).

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file or directory | conversation context |
| `--output-dir` | directory path | `{PROJECT_ROOT}/docs/plans/` |
| `--format` | `md` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag)_ | off — load `session-state.json` from output-dir |

`PROJECT_ROOT` = git toplevel if available, else workspace root. `--output-dir` always wins. `--format yaml` and `--format json` are rejected (`UNSUPPORTED_FORMAT`). JSON on disk is only `items.json` (item graph) and `session-state.json` (resume / agent I/O).

## Common flows

```
rr-planner --discover
```
→ Confirm project posture, then full top-down cascade with interactive discovery; writes all docs to `{PROJECT_ROOT}/docs/plans/`.

```
rr-planner --prd --input "Build a team analytics dashboard for engineering managers"
```
→ Discovery + compose for exec-summary through PRD only.

```
rr-planner --research --output-dir docs/plans/
```
→ Post-composition market evaluation with cited findings.

```
rr-planner --challenge --output-dir docs/plans/
```
→ Devil's-advocate review of existing planning docs (union of all blind-spot lenses).

```
rr-planner --discover --text-mode
```
→ Questions asked inline in chat instead of structured `AskQuestion` prompts.

```
rr-planner --resume --output-dir docs/plans/
```
→ Continue a paused session from checkpoint. Q&A appends to the existing raw-history file.

```
rr-planner --discover --depth deep
```
→ Full cascade + mandatory research + challenge pass.

## Output artifacts

Compose writes cascade docs and `items.json`. The skill asks clarifications and writes `session-state.json`, `decision-ledger.yaml`, `raw-history/`, and `{level}.notes.yaml` (transient; deleted when that level's notes are resolved).

| File | Content |
|------|---------|
| `exec-summary.md` | Posture, vision, problem, why now |
| `mrd.md` | Market context |
| `brd.md` | Business requirements |
| `prd.md` | Product requirements |
| `frd.md` | Functional requirements with Gherkin acceptance criteria |
| `{level}.notes.yaml` | Off-level answers parked on the affected doc (always YAML; not validator input; exists only while unresolved) |
| `items.json` | Item graph / parent-child / spec-build / rationale ids (always written; validator target) |
| `decision-ledger.yaml` | Evidence, rationales, graveyard, reserved ids, re-decision queue (skill-owned; validator input) |
| `session-state.json` | Checkpoint for stop/resume (decisions, facts, `project_posture`, `viability`, `note_sessions`, `item_registry`, `raw_history_path`) |
| `raw-history/{UTC}.yaml` | Verbatim Q&A turns (append-only; created on first question) |
| `research-report.md` | Cited market findings (when research runs) |
| `challenge-report.md` | Blind-spot findings (when `--challenge` runs) |

Cascade docs are `.md` only. `items.json` and `session-state.json` are always JSON. `decision-ledger.yaml` and `{level}.notes.yaml` are always YAML. Only the ledger is validator input. `--format yaml` is `UNSUPPORTED_FORMAT`.

## Troubleshooting

- **Ambiguous action** — One primary flag per call; `--discover` and `--challenge` are mutually exclusive.
- **Out of scope (`OUT_OF_SCOPE`)** — Implementation, code review, tickets, or skill-vs-command advice with no planning flag. Pass `--discover` if that work is the product to plan.
- **Partial docs** — Say "stop" or "pause" to checkpoint; resume with `--resume`. Answer pending clarification questions to advance.
- **Old `docs/planning/` checkpoint** — Resume uses it once, states the new default `docs/plans/`, and does not copy files. Pass `--output-dir` to keep the old path.
- **Missing parent docs for challenge/research** — Run `--discover` first or point `--input` at existing docs.
- **Traceability failures** — Re-run focused level (e.g. `--frd`) after fixing parent docs.
- **Held session (`VIABILITY HOLD` / `blocked`)** — Binding `hold` names missing evidence in `viability[]` and the ledger. Do not treat the plan as accepted. Resume, satisfy the evidence bar or confirm `kill` with a revival trigger, then re-run pre-save.
- **Revived item** — A killed id stays in `reserved_ids` / `graveyard`. Revival is a **new** id plus `type: revival` pointing at the snapshot. Compose will not recycle the buried number.
- **`--format yaml` / `--format json`** — Not a plan format. Use `md` (default). Stale `{level}.yaml` cascade files are rewritten at resolve.

## Further reading

| Topic | Owner |
|-------|-------|
| Quick start | This file |
| Routing and cascade | [SKILL.md](SKILL.md) |
| Flag parsing / conflicts | [refs/input-resolution.md](refs/input-resolution.md) |
| Level order and gates | [refs/cascade.md](refs/cascade.md) |
| Project posture / MoSCoW legend | [refs/project-posture.md](refs/project-posture.md) |
| Expert panel / verdicts | [refs/expert-panel.md](refs/expert-panel.md) |
| Decision ledger / reason graph | [refs/decision-ledger.md](refs/decision-ledger.md) |
| Off-level answers | [refs/note-sessions.md](refs/note-sessions.md) |
| Phase schemas | [refs/contracts.md](refs/contracts.md) |
| Doc structures | [refs/doc-standards/](refs/doc-standards/) |
| Item identity / rank / status | [refs/doc-standards/item-schema.md](refs/doc-standards/item-schema.md) |
| Success gate | [refs/success-criteria.md](refs/success-criteria.md) |
| Output adapters | [refs/output-formats.md](refs/output-formats.md) |
