# s-prepare

Builder-owned tech plan: pin-complete execute-slice → ordered task artifacts for Execute.

## Why

Execute needs capability atoms, real dependencies, cited tech ADRs, and a PR map before code — without inventing PRD intent or product law. Done when the slice task-summary is complete, every task file is detailed, and prepare stops (no auto-chain to **s-coder**).

## What

Owns tech-decision gate (lazy tech ADR), L1 ordered summary, L2 task detail, L3 PR division. Artifacts: global task registry + per-slice task folder.

**Out of scope:** product PRD/constitution/DEC; application code; forge PR open.

## When

### Use when

- `--prepare` / “prepare slice” / “decompose execute-slice” / “tech plan for slice” via **rr-builder** (explicit handoff)
- Builder orchestrate when prepare is incomplete (`prepare_status` ≠ complete / outlined rows; drive/scope per parent)
- After Plan slice freeze when builders need ordered tasks

### Avoid when

- Authoring product Plan docs → **rr-planner**
- Implementing code → **s-coder**
- Opening PR/MR → **s-ci**

## Philosophy

- **Lazy tech ADRs** — mint only when L1/L2 would invent mechanism
- **Code wins on brownfield mechanism** — reverse-derive; do not redesign against live call graph
- **Stop after L3** — prepare ≠ implement
- **Global task ids** — monotonic across slices via registry

## UX

### Invoke

Parent **rr-builder** loads this nested skill on `--prepare` handoff or orchestrate **prepare** stage (`disable-model-invocation: true` — manual `@s-*` / slash invoke).

### Intake

Resolve execute-slice kernel + posture (greenfield / brownfield / docs_ahead / conflict). Prefer an explicit kernel path from parent.

### Clarify

AskQuestion (or text-mode same options) for irreversible tech forks and L1 validation (DAG, grain, requirement map, posture). L2 batches by default; pause after each L2 only when parent requests.

### Output

Per-slice task-summary + numbered task files; optional forced tech ADRs under plan architecture paths.

### Close

Mark prepare complete; stop. Do not chain **s-coder**.

## Constraints

- Self-invoke nested skill — parent **Read** only; not in `plugin.json`
- Missing freeze → stop / **rr-planner**
- Conflict posture (code vs docs) → stop or AskQuestion; never silent average
- L1 `depends_on` must be a DAG
- Out of cascade validator scope

## Notes

- Kernel: `docs/rr/{track}/plan/execute-slice.yaml` (track from `docs/rr/rrr-status.yaml` / plan `status.yaml`)
- Tasks: `docs/rr/tasks/registry.yaml` + `docs/rr/tasks/{slice_id}/` (`task-summary.md`, `{NNNN}.md`)
- Pack layout: `SKILL.md`, `refs/` (input, sequencing, tech-decisions, grain, PR, templates, compatibility, phase contracts)
- Lexicon: plugin `GLOSSARY.md` / `ACRONYMS.md`
