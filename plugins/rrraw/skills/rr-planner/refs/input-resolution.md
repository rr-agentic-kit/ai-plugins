# input-resolution

**Owner:** Normalize raw flags and natural-language intent into a canonical **Plan** payload before any agent invocation.

**Scope:** `rr-planner` only. Discover actions (`--discover`, `--executive-summary` / `--mrd` / `--brd`, ideation, business-case freeze) belong to `rr-discovery` — route there; do not invent Discover cascade here.

Shared schemas: [contracts.md](../../../refs/planning/contracts.md), [baselines.md](../../../refs/planning/baselines.md), [output-formats.md](../../../refs/planning/output-formats.md), [setup.md](../../../refs/planning/setup.md). Load the shared package directly.

## Responsibilities

- Recognize primary action flags (exactly one per invocation).
- Parse shared selectors: `--input`, `--output-dir`, `--format`, `--depth`, `--text-mode`, `--resume`, `--change` + `--section` + `--target`.
- Resolve `PROJECT_ROOT` and default `output_dir`.
- Fall back to NL intent when no explicit action flag is present.
- Apply conflict matrix and precedence rules.
- Emit `NormalizedPayload` (see [contracts.md](../../../refs/planning/contracts.md)) plus `resolution_trace`.
- Surface **entry-gate** failure when Plan compose is requested without frozen BRD + `business-case.yaml` ([business-case-handoff.md](../../rr-discovery/refs/business-case-handoff.md)).

## Primary action flags

| Flag | `action` value |
|------|----------------|
| `--prd` | `prd` |
| `--change` | `change` |
| `--research` | `research` |
| `--challenge` | `challenge` |
| `--review` | `challenge` |
| `--setup` | `setup` |
| `--resume` | _(selector)_ — sets `resume: true`; not a second primary when paired with continue-intent |

When no primary flag is present, do not emit a payload yet. Run **NL intent fallback**, then **Out-of-scope NL**, then **Status-first routing**. Bare invoke **never** silent-rediscovers and **never** silent-composes PRD without entry gate. Combining `--setup` with another primary → `CONFLICTING_FLAGS`. `--setup` never starts Plan compose.

### Not Plan primaries (route to Discover)

| Flag / intent | Resolution |
|---------------|------------|
| `--discover` / `--all` | `OUT_OF_SCOPE` — cite `rr-discovery` |
| `--executive-summary` / `--exec-summary` / `--mrd` / `--brd` | `OUT_OF_SCOPE` — cite `rr-discovery` |
| NL: problem, market, viability, ideation, beachhead, GTM framing, freeze business-case | `OUT_OF_SCOPE` → `rr-discovery` unless a Plan primary is already present |

## Project root

`PROJECT_ROOT`:

1. `git rev-parse --show-toplevel` if the working tree is a git repo.
2. Else workspace / current working directory root.

Default `output_dir` = `{PROJECT_ROOT}/docs/plan/`. `--output-dir` always wins. When phase `status.yaml.next` is set and the route is `continue-next-track` (or `--target` names that track), set `output_dir` to `{PROJECT_ROOT}/docs/plan/{next}/` unless `--output-dir` was explicit. Summary `rrr-status.yaml`, `agent.plan.md`, parking files stay in `{PROJECT_ROOT}/docs/`; phase detail in `docs/plan/` ([baselines.md](../../../refs/planning/baselines.md)).

## Shared selectors

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file path or directory | null (use conversation context) |
| `--output-dir` | directory path | `{PROJECT_ROOT}/docs/plan/` |
| `--format` | `md` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag, no value)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag, no value)_ | off — start fresh or from `--input` |
| `--change` | _(flag, no value)_ | off — resume/research as resolved |
| `--section` | item id, heading, or section name | null — required with `--change` |
| `--target` | cascade level (`prd`) and/or track (`0.1`, `next`, `current`) | null — required with `--change`; default track is current |
| `--questions-per-cycle` | positive integer | `1` — max AskQuestion count per address cycle |

`--format yaml` and `--format json` are not plan-document formats. Emit `UNSUPPORTED_FORMAT`.

Allowed JSON on disk: `items.json`, `session-state.json`. Machine handoff: `business-case.yaml`. Agent `Task` payloads stay JSON (internal). `payload.format` stays `"md"`.

### Question mode

| Flag | `question_mode` |
|------|-----------------|
| _(default)_ | `ask` — structured `AskQuestion` |
| `--text-mode` | `text` — questions inline in chat |

### Questions per cycle

| Flag | `preferences.questions_per_cycle` |
|------|-----------------------------------|
| _(default)_ | `1` |
| `--questions-per-cycle N` | `N` (integer ≥ 1) |

Confirm-once: on first explicit `--questions-per-cycle N`, persist to `session-state.json`. Resume reads stored value.

### Resume

| Flag | Behavior |
|------|----------|
| `--resume` | Load `session-state.json` from `--output-dir`; continue from `checkpoint.current_level` (PRD); append Q&A to `raw_history_path`. Route: `resume`. |
| Auto-resume | If `session-state.json` exists and user says "continue" / "resume" in NL → treat as `--resume` |

`--resume` = continue-open Plan. It does not start `--change` and does not rediscover.

### `--change` (section + target)

`--change` is a primary action. It requires `--section` and `--target`.

| Selector | Meaning |
|----------|---------|
| `--section` | What to change: item id (`PRD-3.1`), heading, or doc-standard section name |
| `--target` | Where: `prd` and/or track (`0.1`, `0.2`, `current`, `next`) |

`--change` does not combine with `--prd` / `--research` / `--challenge` / Discover flags. Discover-stem targets → `OUT_OF_SCOPE` → `rr-discovery`.

After payload emit, the skill **classifies** (judgment — not CI):

| Classify as | When |
|-------------|------|
| **patch** | Obligation-preserving on current (defect, lock-target, docs patch). Allowed while next is open. |
| **redirect-to-next** | Minor+ on current while `next` is open → refuse; point at next or `future.md`. |
| **open-next** | Current docs shipped, no next, user wants minor+ → confirm, then mint `next`. Refuse if current docs still `?`. |
| **unfreeze** | Obligations break, no next (or patch-sized). Ask. Never auto-unfreeze. |

Unlock / patch-only-current: [baselines.md](../../../refs/planning/baselines.md).

### Legacy path fallback

Only when `output_dir` is the **default** and resume is requested:

1. If `{PROJECT_ROOT}/docs/plan/session-state.json` exists → use it.
2. Else if `{PROJECT_ROOT}/docs/plans/session-state.json` exists → **once**: announce new defaults (`docs/discovery/` + `docs/plan/`); do **not** migrate.
3. Else if `{PROJECT_ROOT}/docs/planning/session-state.json` exists → same one-shot announce.
4. Else `MISSING_CHECKPOINT`.

Explicit `--output-dir` skips this fallback.

### Depth normalization

| Value | Plan behavior |
|-------|---------------|
| `shallow` | PRD gates light; research/challenge optional |
| `standard` | Full PRD gates |
| `deep` | PRD + research + challenge append on `chain` |

### Input normalization

1. If `--input` is a directory, scan for existing planning docs (`prd.md` required for Plan compose; Discover stems may exist as frozen parents).
2. If `--input` is a file, treat as seed context for Plan.
3. Reject non-existent paths.

### Stale cascade rewrite

After a successful payload, before any `Task`: if `output_dir` has cascade docs, run:

```bash
sh scripts/validate_planning.sh --rewrite <output_dir>
```

Skip when no cascade files exist. Do not treat yaml as a live `--format`.

## NL intent fallback

When no primary action flag is detected, map phrases (case-insensitive, first match wins):

| Intent signal | `action` |
|---------------|----------|
| setup, bootstrap planning, init plans | `setup` |
| product requirements, PRD, features, RICE, stories | `prd` |
| research, market research (post-compose), competitors deep-dive | `research` |
| challenge, review, critique, devil's advocate (Plan docs) | `challenge` |
| resume, continue planning, pick up where we left off | `prd` + `resume: true` (or route resume) |
| change, revise, patch the, update the PRD | `change` (extract `--section` / `--target`; missing both → `CHANGE_MISSING_SELECTORS`) |
| discover, exec summary, MRD, BRD, viability, ideation, business-case | `OUT_OF_SCOPE` → `rr-discovery` |

If multiple intent signals match with equal confidence → `AMBIGUOUS_ACTION`.

### Out-of-scope NL

Runs only when **no primary action flag** is present **and** the NL intent table did not match Plan.

| Class | Match |
|-------|--------|
| Discover work | Problem/market/viability/ideation/GTM framing / freeze handoff → `rr-discovery` |
| Code / ticket work | Implement, refactor, code review, tickets, CI — unless they asked to Plan that product as PRD |

On Discover `OUT_OF_SCOPE`: cite `rr-discovery`. On code/ticket: cite SKILL **When not to use**.

## Conflict matrix

| Dimension | Rule |
|-----------|------|
| Action | Exactly one primary action per invocation |
| Plan focus | `--prd` mutually exclusive with `--change` / `--research` / `--challenge` |
| `--change` | Requires `--section` and `--target`. Combining with other primaries → `CONFLICTING_FLAGS` |
| `--research` / `--challenge` | Require existing docs. Combining with another primary → `CONFLICTING_FLAGS`. `depth: deep` may append both on `chain` — not a second primary |
| `--setup` | Combining with Plan primaries → `CONFLICTING_FLAGS`. Never starts compose |
| Discover flags | Always `OUT_OF_SCOPE` — not Plan primaries |
| Format | Single value only; must be `md` |

## Precedence

1. Explicit CLI flags beat NL intent.
2. Among explicit flags, left-to-right order in argv is tie-breaker for logging only; conflicts still error.
3. Defaults apply only after successful resolution (no error).
4. No explicit action flag, no NL Plan match, and not out-of-scope → **Status-first routing**.

## Status-first routing

Load `docs/rrr-status.yaml`, then `{output_dir}/status.yaml` and `session-state.json`. Entry gate also reads `docs/discovery/status.yaml` + `business-case.yaml`. Pick **one** route.

| `payload.route` | When |
|-----------------|------|
| `ask-discover` | No frozen BRD / no `business-case.yaml` — point to `rr-discovery`; do not compose PRD |
| `resume` | `--resume`, or NL continue, or checkpoint `paused` / `in_progress` with pending PRD work |
| `continue-prd` | PRD draft `rev: ?` and entry gate passes |
| `start-change` | `--change` (or NL change) and no in-flight change checkpoint |
| `continue-change` | In-flight change on that section+target |
| `continue-next-track` | `next` set and next-track docs still `?` |
| `ask` | Bare invoke, PRD frozen/shipped, nothing open — Ask: patch / `--change` / open-next / stop |

`--prd` overrides route pick but **does not** skip entry gate.

## Entry gate (Plan compose)

Before `action` `prd` or `change` targeting `prd`:

1. `brd` ∈ discovery `session_state.frozen_levels` (or `docs/discovery/status.yaml` frozen BRD), **and**
2. `docs/discovery/business-case.yaml` present with required fields

On fail → `PLAN_ENTRY_REFUSED` (AskQuestion: migrate brownfield | run `rr-discovery` | abort). Exception: documented brownfield (legacy shallow ES+PRD) — one AskQuestion, not silent.

Validator helper: `check_plan_entry` ([output-formats.md](../../../refs/planning/output-formats.md)).

## Normalized payload schema

```json
{
  "action": "prd",
  "input": null,
  "output_dir": "{PROJECT_ROOT}/docs/plan/",
  "format": "md",
  "depth": "standard",
  "question_mode": "ask",
  "resume": false,
  "route": "continue-prd",
  "change_section": null,
  "change_target": null,
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

### `cascade_levels` expansion

| `action` | `cascade_levels` |
|----------|------------------|
| `prd` | `["prd"]` |
| `change` | `["prd"]` when target is prd; Discover targets → out of scope |
| `research` | `[]` |
| `challenge` | `[]` |
| `setup` | `[]` |

### `chain` expansion

| `action` | Default `chain` |
|----------|-----------------|
| `prd` / `change` | `["compose"]` (+ humanize by skill) |
| `research` | `["research"]` |
| `challenge` | `["challenge"]` |
| `setup` | `["setup"]` |
| `depth: deep` | append `research`, `challenge` after compose when applicable |

## Deterministic errors

| Code | Condition |
|------|-----------|
| `AMBIGUOUS_ACTION` | Multiple primary actions after flag + NL resolution |
| `CONFLICTING_FLAGS` | Mutually exclusive flags |
| `INVALID_INPUT_PATH` | `--input` path does not exist |
| `MISSING_DOCS` | `--challenge` or `--research` with no docs in input or output-dir |
| `MISSING_CHECKPOINT` | `--resume` but no `session-state.json` |
| `CHANGE_MISSING_SELECTORS` | `--change` without both section and target |
| `UNSUPPORTED_FORMAT` | Format not `md` |
| `UNSUPPORTED_DEPTH` | Depth not in allowed set |
| `OUT_OF_SCOPE` | Discover intent or When-not-to-use class |
| `PLAN_ENTRY_REFUSED` | Frozen BRD + valid `business-case.yaml` missing |

Error response shape: see [contracts.md](../../../refs/planning/contracts.md) `PhaseError`.
