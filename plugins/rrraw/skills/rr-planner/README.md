# rr-planner

Flag-driven software planning docs: progressive top-down discovery from vision through functional requirements, with compose, research, and challenge phases. No command files; NL + flag driven.

**Runtime:** [SKILL.md](SKILL.md) · **Policies:** [refs/](refs/)

## Philosophy

- **Progressive cascade** — Posture gate, then Exec summary → MRD → BRD → PRD → FRD; each level inherits and narrows the one above.
- **Item contract** — Hierarchical `{DOC}-{n.m}` ids, immediate parent pointer, atomic leaves; ranking is per layer (MoSCoW / Kano / FRD triad), not P0. MoSCoW *legend* follows project posture (Must is not always MVP). Spec vs build are separate axes.
- **Goal-anchored** — Unclear and ambiguous statements are blocking; clarify before recording facts; every decision traces to stated goals.
- **Off-level answers** — A feature mentioned during vision parks on the affected doc (`{level}.notes.yaml`), not as an exec-summary assumption.
- **Proactive discovery** — Stage-exit blind-spots before freeze; write-time pre-save reflection; broad market research deferred to post-composition.
- **Interactive discovery, non-interactive agents** — Skill owns question loops (`AskQuestion` by default, `--text-mode` for inline); compose/research/challenge agents return `clarifications_needed[]`.
- **Stop and resume** — Pause anytime; state checkpoints to `session-state.json`; Q&A appends to `raw-history/`; `--resume` continues where you left off. Confirmed posture is not re-asked.

## How to run

One primary action flag + optional selectors. Explicit flags win on conflict ([refs/input-resolution.md](refs/input-resolution.md)).

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file or directory | conversation context |
| `--output-dir` | directory path | `{PROJECT_ROOT}/docs/plans/` |
| `--format` | `md`, `yaml` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag)_ | off — load `session-state.json` from output-dir |

`PROJECT_ROOT` = git toplevel if available, else workspace root. `--output-dir` always wins. `--format json` is rejected (`UNSUPPORTED_FORMAT`). JSON on disk is only `items.json` (item graph) and `session-state.json` (resume / agent I/O).

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

```
rr-planner --discover --format yaml
```
→ Same cascade docs with `.yaml` extension and closed-key mappings.

## Output artifacts

| File | Content |
|------|---------|
| `exec-summary.md` \| `.yaml` | Posture, vision, problem, why now |
| `mrd.md` \| `.yaml` | Market context |
| `brd.md` \| `.yaml` | Business requirements |
| `prd.md` \| `.yaml` | Product requirements |
| `frd.md` \| `.yaml` | Functional requirements with Gherkin acceptance criteria |
| `{level}.notes.yaml` | Off-level answers parked on the affected doc (always YAML; not validator input) |
| `items.json` | Item graph / parent-child / spec-build (always written; validator target) |
| `session-state.json` | Checkpoint for stop/resume (decisions, facts, `project_posture`, `note_sessions`, `item_registry`, `raw_history_path`) |
| `raw-history/{UTC}.yaml` | Verbatim Q&A turns (append-only; created on first question) |
| `research-report.md` \| `.yaml` | Cited market findings (when research runs) |
| `challenge-report.md` \| `.yaml` | Blind-spot findings (when `--challenge` runs) |

`--format` selects the human-doc extension. `items.json` and `session-state.json` are always JSON. `{level}.notes.yaml` is always YAML and is not a plan doc.

## Troubleshooting

- **Ambiguous action** — One primary flag per call; `--discover` and `--challenge` are mutually exclusive.
- **Partial docs** — Say "stop" or "pause" to checkpoint; resume with `--resume`. Answer pending clarification questions to advance.
- **Old `docs/planning/` checkpoint** — Resume uses it once, states the new default `docs/plans/`, and does not copy files. Pass `--output-dir` to keep the old path.
- **Missing parent docs for challenge/research** — Run `--discover` first or point `--input` at existing docs.
- **Traceability failures** — Re-run focused level (e.g. `--frd`) after fixing parent docs.
- **`--format json`** — Not a plan format. Use `md` or `yaml`.

## Further reading

| Topic | Owner |
|-------|-------|
| Quick start | This file |
| Routing and cascade | [SKILL.md](SKILL.md) |
| Flag parsing / conflicts | [refs/input-resolution.md](refs/input-resolution.md) |
| Level order and gates | [refs/cascade.md](refs/cascade.md) |
| Project posture / MoSCoW legend | [refs/project-posture.md](refs/project-posture.md) |
| Off-level answers | [refs/note-sessions.md](refs/note-sessions.md) |
| Phase schemas | [refs/contracts.md](refs/contracts.md) |
| Doc structures | [refs/doc-standards/](refs/doc-standards/) |
| Item identity / rank / status | [refs/doc-standards/item-schema.md](refs/doc-standards/item-schema.md) |
| Success gate | [refs/success-criteria.md](refs/success-criteria.md) |
| Output adapters | [refs/output-formats.md](refs/output-formats.md) |
