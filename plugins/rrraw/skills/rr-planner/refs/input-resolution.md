# input-resolution

**Owner:** Normalize raw flags and natural-language intent into a canonical **Plan** payload before any agent invocation.

**Scope:** `rr-planner` only. Discover actions belong to `rr-discovery` — route there. Execute / sprint / release-plan inventiveness → OUT_OF_SCOPE or reframe.

Shared schemas: `refs/planning/contracts.md`, `refs/planning/baselines.md`, `refs/planning/output-formats.md`, `refs/planning/setup.md`.

## Responsibilities

- Recognize primary action flags (exactly one per invocation).
- Parse shared selectors: `--input`, `--output-dir`, `--format`, `--depth`, `--text-mode`, `--resume`, `--change` + `--section` + `--target`, slice select / `--freeze-slice`.
- Resolve `PROJECT_ROOT` and default `output_dir`.
- Fall back to NL intent when no explicit action flag is present.
- Apply conflict matrix and precedence rules.
- Emit `NormalizedPayload` plus `resolution_trace`.
- Surface **entry-gate** failure when Plan compose is requested without frozen BRD + `business-case.yaml`.

## Primary action flags

| Flag | `action` value |
|------|----------------|
| `--prd` | `prd` |
| `--change` | `change` |
| `--research` | `research` |
| `--challenge` | `challenge` |
| `--review` | `challenge` |
| `--setup` | `setup` |
| `--freeze-slice` | `freeze-slice` |
| `--resume` | _(selector)_ — sets `resume: true`; not a second primary when paired with continue-intent |

When no primary flag is present, run **NL intent fallback**, then **Out-of-scope NL**, then **Status-first routing**. Bare invoke **never** silent-rediscovers and **never** silent-composes PRD without entry gate. Combining `--setup` with another primary → `CONFLICTING_FLAGS`. `--setup` never starts Plan compose.

### Not Plan primaries (route away)

| Flag / intent | Resolution |
|---------------|------------|
| `--discover` / `--all` / Discover stems | `OUT_OF_SCOPE` — cite `rr-discovery` |
| NL: problem, market, viability, ideation, GTM, freeze business-case | `OUT_OF_SCOPE` → `rr-discovery` unless a Plan primary is present |
| NL: sprint planning, velocity, capacity, sprint retro-as-Plan | **Anti-trigger** — refuse; reframe as **slice selection** / phase ([execute-handoff.md](execute-handoff.md)) |
| NL: implement / Execute / ship-check / tickets as Plan | `OUT_OF_SCOPE` — Execute future / When-not-to-use |
| NL: release plan / version bundling of slices | `OUT_OF_SCOPE` this redesign — selection + slice freeze are the building blocks; do not invent release artifacts |

## Project root

`PROJECT_ROOT`:

1. `git rev-parse --show-toplevel` if git repo.
2. Else workspace / cwd root.

Default `output_dir` = `{PROJECT_ROOT}/docs/rr/{track}/plan/` (track from `docs/rr/rrr-status.yaml`, default `0.1`). `--output-dir` always wins. When `status.yaml.next` is set and route is `continue-next-track`, set `output_dir` to `{PROJECT_ROOT}/docs/rr/{next}/plan/` unless explicit. Summary + parking stay in `{PROJECT_ROOT}/docs/rr/`.

## Shared selectors

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file path or directory | null |
| `--output-dir` | directory path | `{PROJECT_ROOT}/docs/rr/{track}/plan/` |
| `--format` | `md` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag)_ | off — `AskQuestion` |
| `--resume` | _(flag)_ | off |
| `--change` | _(flag)_ | off |
| `--section` | item id, heading, or section name | null — required with `--change` |
| `--target` | `prd` / standing doc / track | null — required with `--change` |
| `--freeze-slice` | _(flag)_ or with requirement id list | off |
| `--questions-per-cycle` | positive integer | `1` |

`--format yaml|json` → `UNSUPPORTED_FORMAT`.

### Question mode / questions per cycle

Same as before: default `ask` + `questions_per_cycle: 1`; confirm-once persistence on explicit `--questions-per-cycle`.

### Resume

| Flag | Behavior |
|------|----------|
| `--resume` | Load `session-state.json`; continue Plan checkpoint; append Q&A. Route: `resume`. |
| Auto-resume | NL “continue” / “resume” with checkpoint → treat as `--resume` |

### `--change` / slice select

`--change` requires `--section` and `--target`. Discover-stem targets → `OUT_OF_SCOPE` → `rr-discovery`.

Slice selection: mark requirement leaves `_status_: selected` (and peers `deferred`) without deleting rows. NL “select these for the slice” / “freeze this slice” → `freeze-slice` or change-on-status.

After payload emit, skill **classifies** patch / redirect-to-next / open-next / unfreeze per `refs/planning/baselines.md`.

### Legacy path fallback

Same once-announce fallback as Discover: prefer `docs/rr/{track}/plan/`; if only legacy `docs/plan/`, `docs/plans/`, or `docs/planning/` has a checkpoint, announce and point at `--setup` layout migrate.

### Depth normalization

| Value | Plan behavior |
|-------|---------------|
| `shallow` | Gates light; research/challenge optional |
| `standard` | Full Plan gates + smell before freeze |
| `deep` | + research + technical challenge (Plan challenge-method) |

## NL intent fallback

| Intent signal | `action` |
|---------------|----------|
| setup, bootstrap planning, init plans | `setup` |
| product requirements, PRD, features, RICE, stories, requirements, architecture spine | `prd` |
| freeze this slice, freeze-slice, select slice | `freeze-slice` |
| research, competitors deep-dive (post-compose) | `research` |
| challenge, review, critique, pre-mortem, red-team (Plan docs) | `challenge` |
| resume, continue planning | `prd` + `resume: true` (or resume route) |
| change, revise, patch the, update the PRD / delta / AC | `change` |
| discover, exec summary, MRD, BRD, viability, ideation, business-case | `OUT_OF_SCOPE` → `rr-discovery` |
| sprint, velocity, capacity planning | anti-trigger → reframe slice selection (no payload inventiveness) |

If multiple intent signals match with equal confidence → `AMBIGUOUS_ACTION`.

### Out-of-scope NL

| Class | Match |
|-------|--------|
| Discover work | Problem/market/viability/ideation/GTM / freeze handoff → `rr-discovery` |
| Execute / code / ticket | Implement, ship-check, tickets, CI — unless they asked to Plan that product |
| Release/version plan | Grouping slices into a version — deferred; cite selection + slice freeze only |

## Conflict matrix

| Dimension | Rule |
|-----------|------|
| Action | Exactly one primary per invocation |
| Plan focus | `--prd` mutually exclusive with `--change` / `--research` / `--challenge` / `--freeze-slice` |
| `--change` | Requires `--section` and `--target` |
| `--setup` | Never combines with Plan primaries; never starts compose |
| Discover flags | Always `OUT_OF_SCOPE` |
| Format | Single value; must be `md` |

## Precedence

1. Explicit CLI flags beat NL intent.
2. Among explicit flags, left-to-right is tie-breaker for logging only; conflicts still error.
3. Defaults apply only after successful resolution.
4. No explicit action, no NL Plan match, not out-of-scope → **Status-first routing**.

## Status-first routing

Load `docs/rr/rrr-status.yaml` (fall back to legacy `docs/rrr-status.yaml`), then `{output_dir}/status.yaml` and `session-state.json`. Entry gate also reads discovery status + `business-case.yaml`.

| `payload.route` | When |
|-----------------|------|
| `ask-discover` | No frozen BRD / no handoff — point to `rr-discovery` |
| `resume` | `--resume`, NL continue, or paused Plan checkpoint |
| `continue-prd` | PRD draft `rev: ?` and entry gate passes |
| `freeze-slice` | Selected requirements ready / `--freeze-slice` |
| `start-change` | `--change` with no in-flight change |
| `continue-change` | In-flight change |
| `continue-next-track` | `next` set and next-track docs still `?` |
| `ask` | Bare invoke, nothing open — Ask: patch / change / freeze-slice / open-next / stop |

`--prd` overrides route pick but **does not** skip entry gate.

## Entry gate (Plan compose)

Before `prd`, `change` targeting plan docs, or `freeze-slice`:

1. Frozen BRD + valid `business-case.yaml`
2. On fail → `PLAN_ENTRY_REFUSED` (AskQuestion: migrate brownfield | run `rr-discovery` | abort)

## Normalized payload schema

```json
{
  "action": "prd",
  "input": null,
  "output_dir": "{PROJECT_ROOT}/docs/rr/0.1/plan/",
  "format": "md",
  "depth": "standard",
  "question_mode": "ask",
  "resume": false,
  "route": "continue-prd",
  "change_section": null,
  "change_target": null,
  "slice_requirement_ids": null,
  "cascade_levels": ["prd"],
  "chain": ["compose"],
  "resolution_trace": {
    "source": "flags",
    "flags_seen": ["--prd"],
    "nl_matched": null,
    "errors": []
  }
}
```

### `cascade_levels` / `chain`

| `action` | `cascade_levels` | Default `chain` |
|----------|------------------|-----------------|
| `prd` / `change` | `["prd"]` | `["compose"]` (+ humanize by skill) |
| `freeze-slice` | `[]` | `["slice-freeze"]` |
| `research` | `[]` | `["research"]` |
| `challenge` | `[]` | `["challenge"]` |
| `setup` | `[]` | `["setup"]` |
| `depth: deep` | — | append `research`, `challenge` after compose when applicable |

## Deterministic errors

| Code | Condition |
|------|-----------|
| `AMBIGUOUS_ACTION` | Multiple primaries after flag + NL |
| `CONFLICTING_FLAGS` | Mutually exclusive flags |
| `INVALID_INPUT_PATH` | `--input` missing |
| `MISSING_DOCS` | `--challenge` / `--research` with no docs |
| `MISSING_CHECKPOINT` | `--resume` without session-state |
| `CHANGE_MISSING_SELECTORS` | `--change` without section and target |
| `UNSUPPORTED_FORMAT` | Format not `md` |
| `UNSUPPORTED_DEPTH` | Depth not allowed |
| `OUT_OF_SCOPE` | Discover / Execute / release-plan inventiveness / When-not-to-use |
| `PLAN_ENTRY_REFUSED` | Frozen BRD + handoff missing |
| `SLICE_REFUSED` | Smell-fail / Effort-without-architecture / shrink-full-set |

Error shape: `refs/planning/contracts.md` `PhaseError`.
