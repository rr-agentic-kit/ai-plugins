# input-resolution

**Owner:** Normalize raw flags and natural-language intent into a canonical payload before any agent invocation.

## Responsibilities

- Recognize primary action flags (exactly one per invocation).
- Parse shared selectors: `--input`, `--output-dir`, `--format`, `--depth`, `--text-mode`, `--resume`, `--change` + `--section` + `--target`.
- Resolve `PROJECT_ROOT` and default `output_dir`.
- Fall back to NL intent when no explicit action flag is present.
- Apply conflict matrix and precedence rules.
- Emit `NormalizedPayload` (see [contracts.md](contracts.md)) plus `resolution_trace`.

## Primary action flags

| Flag | `action` value |
|------|----------------|
| `--discover` | `discover` |
| `--all` | `discover` |
| `--exec-summary` | `exec-summary` |
| `--mrd` | `mrd` |
| `--brd` | `brd` |
| `--prd` | `prd` |
| `--frd` | `frd` |
| `--change` | `change` |
| `--research` | `research` |
| `--challenge` | `challenge` |
| `--review` | `challenge` |
| `--setup` | `setup` |

When no primary flag is present, do not emit a payload yet. Run **NL intent fallback**, then **Out-of-scope NL**, then **Status-first routing**. Default `action` = `discover` only when routing picks `from-0` (no cascade `{stem}.md`; `status.yaml` / `agent.plan.md` alone do not count). Bare invoke **never** silent-rediscovers. Combining `--setup` with another primary → `CONFLICTING_FLAGS`. `--setup` never starts discover/compose.

## Project root

`PROJECT_ROOT`:

1. `git rev-parse --show-toplevel` if the working tree is a git repo.
2. Else workspace / current working directory root.

Default `output_dir` = `{PROJECT_ROOT}/docs/plans/`. `--output-dir` always wins. When `status.yaml.next` is set and the route is `continue-next-track` (or `--target` names that track), set `output_dir` to `{PROJECT_ROOT}/docs/plans/{next}/` unless `--output-dir` was explicit. `status.yaml`, `agent.plan.md`, and `future.md` stay in `{PROJECT_ROOT}/docs/plans/` ([baselines.md](baselines.md)).

## Shared selectors

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file path or directory | null (use conversation context) |
| `--output-dir` | directory path | `{PROJECT_ROOT}/docs/plans/` |
| `--format` | `md` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag, no value)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag, no value)_ | off — start fresh or from `--input` |
| `--change` | _(flag, no value)_ | off — discover/resume/research as resolved |
| `--section` | item id, heading, or section name | null — required with `--change` |
| `--target` | cascade level (`prd`) and/or track (`0.1`, `next`, `current`) | null — required with `--change`; default track is current |

`--format yaml` and `--format json` are not plan-document formats. Do **not** alias either to md. Emit `UNSUPPORTED_FORMAT`.

Allowed JSON on disk (not selected by `--format`): `items.json` (item graph) and `session-state.json` (resume / agent shared state). Agent `Task` payloads stay JSON (internal). `payload.format` stays `"md"`. Durable project knowledge is `status.yaml` (YAML, skill-owned) — [baselines.md](baselines.md).

### Question mode

| Flag | `question_mode` |
|------|-----------------|
| _(default)_ | `ask` — structured `AskQuestion` |
| `--text-mode` | `text` — questions inline in chat |

### Resume

| Flag | Behavior |
|------|----------|
| `--resume` | Load `session-state.json` from `--output-dir`; continue from `checkpoint.current_level`; append Q&A to `raw_history_path`. Route: `resume`. |
| Auto-resume | If `session-state.json` exists in `--output-dir` and user says "continue" / "resume" in NL → treat as `--resume` |

`--resume` = continue-open. It does not start `--change` and does not rediscover from 0.

### `--change` (section + target)

`--change` is a primary action. It requires `--section` and `--target`.

| Selector | Meaning |
|----------|---------|
| `--section` | What to change: item id (`PRD-3.1`), heading, or doc-standard section name |
| `--target` | Where: cascade level (`exec-summary`…`frd`) and/or track (`0.1`, `0.2`, `current`, `next`) |

`--discover` overrides status-first (force discover path). `--change` does not combine with `--discover` / level flags / `--research` / `--challenge`.

After payload emit, the skill **classifies** (judgment — not CI):

| Classify as | When |
|-------------|------|
| **patch** | Obligation-preserving on current (defect, lock-target, docs patch). Allowed while next is open. |
| **redirect-to-next** | Minor+ on current while `next` is open → refuse; point at next or `future.md`. |
| **open-next** | Current docs shipped, no next, user wants minor+ → confirm, then mint `next` as `{track+minor}.0?`. Refuse if current docs still `?`. |
| **unfreeze** | Obligations break, no next (or patch-sized). Ask. Never auto-unfreeze. |

Unlock / patch-only-current: [baselines.md](baselines.md). Do **not** emit `NEXT_LOCKED` or `CURRENT_NOT_PATCH`.

### Old `docs/planning/` fallback

Only when `output_dir` is the **default** (`{PROJECT_ROOT}/docs/plans/`) and resume is requested:

1. If `{PROJECT_ROOT}/docs/plans/session-state.json` exists → use it.
2. Else if `{PROJECT_ROOT}/docs/planning/session-state.json` exists → **once**: set `output_dir` to that old path, tell the user the new default is `{PROJECT_ROOT}/docs/plans/`, do **not** copy or migrate files.
3. Else `MISSING_CHECKPOINT`.

Explicit `--output-dir` skips this fallback.

### Depth normalization

| Value | Discovery behavior |
|-------|-------------------|
| `shallow` | Exec-summary + PRD only; skip MRD/BRD/FRD unless explicitly flagged |
| `standard` | Full cascade with standard gates |
| `deep` | Full cascade + mandatory research phase + challenge pass |

### Input normalization

1. If `--input` is a directory, scan for existing planning docs (`exec-summary`, `mrd`, `brd`, `prd`, `frd` with `.md`). Cascade `{stem}.yaml` in that dir is stale — rewrite (below), not live yaml mode.
2. If `--input` is a file, treat as seed context for discovery.
3. Reject non-existent paths.

### Stale cascade rewrite

After a successful payload, before any `Task` (discover, research, challenge, resume): if `output_dir` already has cascade docs (`{stem}.md` or stale `{stem}.yaml` for `exec-summary`/`mrd`/`brd`/`prd`/`frd`), run:

```bash
python3 scripts/validate_planning.py --rewrite <output_dir>
```

Same for `--input` when it is a directory of cascade docs and differs from `output_dir`. `--rewrite` converts list-meta (`- **Key:**`) and `{stem}.yaml` to canonical `{stem}.md` (hyphenated `_key_:` line, `>` body) and deletes the yaml sibling. Skip when no cascade files exist (greenfield). Do not treat yaml as a live `--format`.

## NL intent fallback

When no primary action flag is detected, map phrases (case-insensitive, first match wins):

| Intent signal | `action` |
|---------------|----------|
| setup, bootstrap planning, init plans | `setup` |
| discover, plan, start planning, new project, greenfield | `discover` |
| exec summary, vision, problem statement | `exec-summary` |
| market, MRD, competitive landscape | `mrd` |
| business requirements, BRD, stakeholders | `brd` |
| product requirements, PRD, features | `prd` |
| functional, FRD, technical requirements | `frd` |
| research, market research, competitors | `research` |
| challenge, review, critique, devil's advocate | `challenge` |
| resume, continue planning, pick up where we left off | `discover` + `resume: true` |
| change, revise, patch the, update the PRD/BRD/… | `change` (extract `--section` / `--target` from NL; missing both → `CHANGE_MISSING_SELECTORS`) |

If multiple intent signals match with equal confidence → `AMBIGUOUS_ACTION`.

Match is token-aware, not naive substring: `review` does not match `code review`; `plan` in "plan a refactor" is a discover hit and skips out-of-scope.

### Out-of-scope NL

Runs only when **no primary action flag** is present **and** the NL intent table did not match. If either matched, skip this check (flags and planning phrases win — e.g. `--discover` or "plan a refactor of billing").

If the utterance matches a **When not to use** class below → `OUT_OF_SCOPE`. Do not default `discover`. Do not start posture. Do not edit implementation files.

| Class | Match (case-insensitive; examples, not an exhaustive regex) |
|-------|--------------------------------------------------------------|
| Code / ticket work | Request to implement, refactor, rewrite a service, review **code**, file tickets, tune production config, debug, or hotfix |
| Artifact-type advice | Asking whether something should be a skill, command, agent, rule, or workflow; or how to run a process/CI checklist — unless they asked to cascade-plan that product |

On `OUT_OF_SCOPE`: return `PhaseError` with `message` citing SKILL **When not to use**, and that they may pass `--discover` (or a level flag) if they want a cascade plan for that work as a product.

### Posture hints (not an action)

NL tokens `greenfield`, `brownfield`, `existing`, `signed v1` **seed** the [project-posture.md](project-posture.md) confirm step. They are not a primary action flag and do not change `cascade_levels`. `greenfield` in the table above still maps to `discover` when no other action is present.

## Conflict matrix

| Dimension | Rule |
|-----------|------|
| Action | Exactly one primary action per invocation |
| Cascade focus | `--exec-summary` through `--frd` are mutually exclusive with `--discover`/`--all` and with `--change` |
| `--change` | Primary only. Requires `--section` and `--target` (flags or NL). Combining with `--discover`/`--all`/level flags/`--research`/`--challenge` → `CONFLICTING_FLAGS`. Missing selectors → `CHANGE_MISSING_SELECTORS`. |
| `--research` | Primary only. Requires existing docs (`--input` or `--output-dir`). Combining with another primary (e.g. `--discover --research`) → `CONFLICTING_FLAGS`. Research+challenge append is `depth: deep` only (`chain` += `research`, `challenge`) — not a second primary. |
| `--challenge` / `--review` | Primary only. Requires existing docs (`--input` or `--output-dir`). Combining with another primary (e.g. `--discover --challenge`) → `CONFLICTING_FLAGS`. Same `depth: deep` append as `--research` — not a second primary. |
| `--setup` | Primary only. Bootstrap/repair. Combining with `--discover`/`--all`/level flags/`--change`/`--research`/`--challenge` → `CONFLICTING_FLAGS`. Never starts discover. |
| Format | Single value only; must be `md` |
| Depth | `shallow` cannot combine with individual level flags below PRD |

## Precedence

1. Explicit CLI flags beat NL intent.
2. Among explicit flags, left-to-right order in argv is tie-breaker for logging only; conflicts still error.
3. Defaults apply only after successful resolution (no error).
4. No explicit action flag, no NL intent match, and not out-of-scope → **Status-first routing** (below). `discover` only when that pick is `from-0`.

## Status-first routing

Load `{output_dir}/status.yaml` (or `{PROJECT_ROOT}/docs/plans/status.yaml` when `output_dir` is a next-track subdir) and `session-state.json`. Pick **one** route. Do not start posture until this pick is done.

| `payload.route` | When |
|-----------------|------|
| `from-0` | No cascade `{stem}.md`. Greenfield discover. `status.yaml` / `agent.plan.md` alone do **not** count as in-progress. |
| `resume` | `--resume`, or NL continue, or checkpoint `paused` / `in_progress` with pending work. |
| `continue-discover` | Cascade `{stem}.md` exists AND current-track levels still `rev: ?` (unfrozen). Continue the open cascade. |
| `start-change` | `--change` (or NL change) and no in-flight change checkpoint. |
| `continue-change` | `--change` / NL change with an in-flight change on that section+target. |
| `continue-next-track` | `next` set and next-track docs still `?`; user is working that track (or `--target next`). |
| `ask` | Bare invoke, current docs frozen/shipped, nothing open — **do not** rediscover. Ask: patch / `--change` / open-next / stop. |

`--discover` / `--all` / a level flag **overrides** this pick (still expand `cascade_levels` as today). Override does not skip unlock stops in [baselines.md](baselines.md): if the user asked to open 0.2 while 0.1 docs are `?`, refuse (skill, not CI).

Classify patch vs redirect-to-next vs open-next vs unfreeze per `--change` above. Those are skill stops, not validator codes.

## Normalized payload schema

```json
{
  "action": "discover",
  "input": null,
  "output_dir": "{PROJECT_ROOT}/docs/plans/",
  "format": "md",
  "depth": "standard",
  "question_mode": "ask",
  "resume": false,
  "route": "from-0",
  "change_section": null,
  "change_target": null,
  "cascade_levels": ["exec-summary", "mrd", "brd", "prd", "frd"],
  "chain": ["discover", "compose"],
  "resolution_trace": {
    "source": "flags",
    "flags_seen": ["--discover"],
    "nl_matched": null,
    "errors": []
  }
}
```

### `cascade_levels` expansion (skill layer)

| `action` | `cascade_levels` |
|----------|------------------|
| `discover` | All five levels (trimmed by `depth`) |
| `exec-summary` | `["exec-summary"]` |
| `mrd` | `["exec-summary", "mrd"]` |
| `brd` | `["exec-summary", "mrd", "brd"]` |
| `prd` | `["exec-summary", "mrd", "brd", "prd"]` |
| `frd` | `["exec-summary", "mrd", "brd", "prd", "frd"]` |
| `change` | Ancestors through `--target` level (same expansion as that level flag). Track from `--target` / `route`. |
| `research` | `[]` (reads existing docs) |
| `challenge` | `[]` (reads existing docs) |
| `setup` | `[]` |

### `depth` trimming

| `depth` | Effective `cascade_levels` for `discover` |
|---------|-------------------------------------------|
| `shallow` | `["exec-summary", "prd"]` |
| `standard` | all five |
| `deep` | all five; `chain` appends `research`, `challenge` |

### `chain` expansion

| `action` | Default `chain` |
|----------|-----------------|
| `discover` | `["discover", "compose"]` per level |
| `research` | `["research"]` |
| `challenge` | `["challenge"]` |
| `setup` | `["setup"]` |
| single-level focus | `["discover", "compose"]` for specified levels |
| `change` | `["discover", "compose"]` for `cascade_levels` (patch / lock-target / unfreeze as classified) |

## Deterministic errors

Stop immediately; do not invoke agents. Return `PhaseError` with code below.

| Code | Condition |
|------|-----------|
| `AMBIGUOUS_ACTION` | Multiple primary actions after flag + NL resolution |
| `CONFLICTING_FLAGS` | Mutually exclusive flags (e.g. `--discover` + `--challenge`) |
| `INVALID_INPUT_PATH` | `--input` path does not exist |
| `MISSING_DOCS` | `--challenge` or `--research` with no docs in input or output-dir |
| `MISSING_CHECKPOINT` | `--resume` but no `session-state.json` in `--output-dir` (after old-dir fallback) |
| `CHANGE_MISSING_SELECTORS` | `--change` (or NL change) without both section and target |
| `UNSUPPORTED_FORMAT` | Format not `md` (including `yaml` and `json`) |
| `UNSUPPORTED_DEPTH` | Depth not in allowed set |
| `OUT_OF_SCOPE` | No primary flag, no NL planning match, and utterance matches **When not to use** (code/ticket work or artifact-type advice) |

Error response shape: see [contracts.md](contracts.md) `PhaseError`.
