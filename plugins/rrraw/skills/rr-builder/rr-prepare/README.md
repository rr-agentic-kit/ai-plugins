# rr-prepare

Builder-owned tech plan: pin-complete `execute-slice.yaml` → ordered tasks under `docs/rr/tasks/`.

## Why

Execute needs capability atoms, real dependencies, cited tech ADRs, and a PR map before code — without inventing PRD intent or product law. Done when `task-summary.md` is complete, every task file is detailed, and prepare stops (no auto-chain to **rr-coder**).

## What

Owns tech-decision gate (lazy `ADR-n`), L1 ordered summary, L2 task detail, L3 PR division. Artifacts: `docs/rr/tasks/registry.yaml` + `{slice_id}/`.

**Out of scope:** product PRD/constitution/DEC; application code; forge PR open.

## When

### Use when

- `--prepare` / “prepare slice” / “decompose execute-slice” / “tech plan for slice” via **rr-builder**
- After Plan slice freeze when builders need ordered tasks

### Avoid when

- Authoring product Plan docs → **rr-planner**
- Implementing code → **rr-coder**
- Opening PR/MR → **rr-ci**

## Philosophy

- **Lazy tech ADRs** — mint only when L1/L2 would invent mechanism
- **Code wins on brownfield mechanism** — reverse-derive; do not redesign against live call graph
- **Stop after L3** — prepare ≠ implement
- **Global task ids** — monotonic across slices via `registry.yaml`

## UX

### Invoke

Parent **rr-builder** loads this nested skill (`disable-model-invocation` / `user-invocable: false`).

### Intake

Resolve `execute-slice.yaml` + posture (greenfield / brownfield / docs-ahead / conflict).

### Clarify

AskQuestion (or text-mode same options) for irreversible tech forks and L1 validation (DAG, grain, requirement map, posture); pause after L1 and each L2 by default (batch L2 only if parent requests).

### Output

`docs/rr/tasks/{slice_id}/task-summary.md` + `{NNNN}.md`; optional forced `ADR-n` under plan architecture paths.

### Close

Mark prepare complete; stop. Do not chain **rr-coder**.

## Constraints

- Self-invoke nested skill — parent **Read** only; not in `plugin.json`
- Missing freeze → stop / **rr-planner**
- Conflict posture (code vs docs) → stop or AskQuestion; never silent average
- L1 `depends_on` must be a DAG
- Out of cascade validator scope

## Notes

Layout: `SKILL.md`, `refs/` (input, sequencing, tech-decisions, grain, PR, templates, compatibility, phase contracts). Lexicon: plugin `GLOSSARY.md` / `ACRONYMS.md`.
