# input-resolution

**Owner:** Normalize raw flags and natural-language intent into a canonical discovery payload before any agent invocation.

**Scope:** `rr-discovery` only. Plan actions (`--prd`, `--research`, PRD compose) belong to `rr-planner` — do not invent them here.

Shared schemas and freeze rules: `refs/planning/contracts.md`, `refs/planning/baselines.md`, `refs/planning/output-formats.md`, `refs/planning/setup.md`. Load the shared package directly.

## Responsibilities

- Recognize primary action flags (exactly one per invocation).
- Parse shared selectors: `--input`, `--output-dir`, `--format`, `--depth`, `--text-mode`, `--resume`, `--change` + `--section` + `--target`.
- Resolve `PROJECT_ROOT` and default `output_dir`.
- Fall back to NL intent when no explicit action flag is present.
- Apply conflict matrix and precedence rules.
- Emit `NormalizedPayload` (see `refs/planning/contracts.md`) plus `resolution_trace`.

## Primary action flags

| Flag | `action` value |
|------|----------------|
| `--discover` | `discover` |
| `--all` | `discover` |
| `--from-code` | `from-code` |
| `--executive-summary` | `executive-summary` |
| `--exec-summary` | `executive-summary` (legacy alias — prefer `--executive-summary`) |
| `--mrd` | `mrd` |
| `--brd` | `brd` |
| `--change` | `change` |
| `--challenge` | `challenge` |
| `--review` | `challenge` |
| `--setup` | `setup` |
| `--resume` | _(selector)_ — sets `resume: true`; not a second primary when paired with continue-intent |

When no primary flag is present, do not emit a payload yet. Run **NL intent fallback**, then **Out-of-scope NL**, then **Status-first routing**. Default `action` = `discover` only when routing picks `from-0` (no cascade `{stem}.md`; `status.yaml` / `agent.plan.md` alone do not count). Bare invoke **never** silent-rediscovers. Combining `--setup` with another primary → `CONFLICTING_FLAGS`. `--setup` never starts discover/compose. `--from-code` is exclusive with other primaries (same conflict class as `--discover`).

### Not discovery primaries

| Flag / intent | Resolution |
|---------------|------------|
| `--prd` | `OUT_OF_SCOPE` — cite `rr-planner` (Plan: PRD+). Do not expand cascade to PRD. |
| `--research` | `OUT_OF_SCOPE` — cite `rr-planner`. Discovery challenge is `--challenge` / `--review` only. |
| NL: product requirements, PRD, features, RICE, stories | `OUT_OF_SCOPE` → `rr-planner` unless a discovery primary is already present |
| NL: market research phase, competitor deep-dive as post-compose research | `OUT_OF_SCOPE` → `rr-planner --research` |

## Project root

`PROJECT_ROOT`:

1. `git rev-parse --show-toplevel` if the working tree is a git repo.
2. Else workspace / current working directory root.

Default `output_dir` = `{PROJECT_ROOT}/docs/rr/{track}/discovery/` (track from `docs/rr/rrr-status.yaml`, default `0.1`). `--output-dir` always wins. When phase `status.yaml.next` is set and the route is `continue-next-track` (or `--target` names that track), set `output_dir` to `{PROJECT_ROOT}/docs/rr/{next}/discovery/` unless `--output-dir` was explicit. Summary `rrr-status.yaml`, `agent.plan.md`, `future.md`, `tech.md`, and `later.md` stay in `{PROJECT_ROOT}/docs/rr/`; phase detail under `docs/rr/{track}/discovery/` (`refs/planning/baselines.md`).

## Shared selectors

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file path or directory | null (conversation context; for `from-code`, research root defaults to `PROJECT_ROOT`) |
| `--output-dir` | directory path | `{PROJECT_ROOT}/docs/rr/{track}/discovery/` |
| `--format` | `md` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag, no value)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag, no value)_ | off — start fresh or from `--input` |
| `--change` | _(flag, no value)_ | off — discover/resume/challenge as resolved |
| `--section` | item id, heading, or section name | null — required with `--change` |
| `--target` | cascade level (`executive-summary` \| `mrd` \| `brd`) and/or track (`0.1`, `next`, `current`) | null — required with `--change`; default track is current |
| `--questions-per-cycle` | positive integer | `1` — max AskQuestion count per address cycle |

`--format yaml` and `--format json` are not plan-document formats. Do **not** alias either to md. Emit `UNSUPPORTED_FORMAT`.

Allowed JSON on disk (not selected by `--format`): `items.json` and `session-state.json`. Agent `Task` payloads stay JSON (internal). `payload.format` stays `"md"`. Durable project knowledge is `docs/rr/rrr-status.yaml` (summary) + `docs/rr/{track}/discovery/status.yaml` (detail); skill-owned — `refs/planning/baselines.md`. `business-case.yaml` is YAML handoff — [business-case-handoff.md](business-case-handoff.md).

### Question mode

| Flag | `question_mode` |
|------|-----------------|
| _(default)_ | `ask` — structured `AskQuestion` |
| `--text-mode` | `text` — questions inline in chat |

### Questions per cycle

Address-loop batch size. Persisted in `session-state.json` `preferences.questions_per_cycle`. Default never silently rises above `1` without explicit opt-in.

| Flag | `preferences.questions_per_cycle` |
|------|-----------------------------------|
| _(default)_ | `1` — one question per address cycle |
| `--questions-per-cycle N` | `N` (integer ≥ 1) |

Confirm-once (same pattern as [project-posture.md](project-posture.md)): on first explicit `--questions-per-cycle N`, persist to `session-state.json`. Resume reads the stored value; do not re-ask unless the user passes a new explicit value.

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
| `--section` | What to change: item id (`ES-1`, `MRD-2.1`, `BRD-3.1`), heading, or doc-standard section name |
| `--target` | Where: cascade level (`executive-summary`…`brd`) and/or track (`0.1`, `0.2`, `current`, `next`) |

`--target prd` → `OUT_OF_SCOPE` (Plan owns PRD). `--discover` overrides status-first (force discover path). `--change` does not combine with `--discover` / level flags / `--challenge`.

After payload emit, the skill **classifies** (judgment — not CI):

| Classify as | When |
|-------------|------|
| **patch** | Obligation-preserving on current (defect, lock-target, docs patch). Allowed while next is open. |
| **redirect-to-next** | Minor+ on current while `next` is open → refuse; point at next or `future.md`. |
| **open-next** | Current docs shipped, no next, user wants minor+ → confirm, then mint `next` as `{track+minor}.0?`. Refuse if current docs still `?`. |
| **unfreeze** | Obligations break, no next (or patch-sized). Ask. Never auto-unfreeze. |

Unlock / patch-only-current: `refs/planning/baselines.md`. Do **not** emit `NEXT_LOCKED` or `CURRENT_NOT_PATCH`.

### Legacy path fallback

Only when `output_dir` is the **default** (`{PROJECT_ROOT}/docs/rr/{track}/discovery/`) and resume is requested:

1. If `{PROJECT_ROOT}/docs/rr/{track}/discovery/session-state.json` exists → use it.
2. Else if `{PROJECT_ROOT}/docs/discovery/session-state.json` exists → **once**: set `output_dir` there, tell the user to run `--setup` (layout migrate to `docs/rr/`), do **not** copy.
3. Else if `{PROJECT_ROOT}/docs/plans/session-state.json` or `docs/planning/session-state.json` exists → same one-shot announce; prefer `--setup` migrate.
4. Else `MISSING_CHECKPOINT`.

Explicit `--output-dir` skips this fallback.

### Depth normalization

| Value | Discovery behavior |
|-------|-------------------|
| `shallow` | Executive-summary only — **no** PRD skip path, **no** MRD/BRD auto-include |
| `standard` | Full discovery cascade (ES → MRD → BRD) with standard gates |
| `deep` | Full discovery cascade + mandatory challenge pass at **deep** layer (`chain` += `challenge`; `challenge_depth: deep`) |

There is no discovery path that writes PRD by skipping middle levels.

### Challenge depth

| Signal | `challenge_depth` | Attestation when clean |
|--------|-------------------|------------------------|
| `--challenge` / `--review` without `deep` | `standard` | `clean-shallow` |
| `--challenge deep` / discover `depth: deep` chain / NL “deep challenge” | `deep` | `clean-deep` |

Parse `deep` as a challenge mode — bare `--challenge` is **standard**, not deep. Layers: `refs/planning/challenge-layers.md`.

### Input normalization

1. If `--input` is a directory, scan for existing discovery docs (`executive-summary`, `mrd`, `brd` with `.md`; accept legacy `exec-summary.md` once and rewrite to `executive-summary.md`). Cascade `{stem}.yaml` in that dir is stale — rewrite (below), not live yaml mode. Presence of `prd.md` alone does not make this Plan — still discovery-scoped for this skill.
2. If `--input` is a file, treat as seed context for discovery.
3. Reject non-existent paths.

### Stale cascade rewrite

After a successful payload, before any `Task` (discover, challenge, resume): if `output_dir` already has cascade docs (`{stem}.md` or stale `{stem}.yaml` for `executive-summary`/`mrd`/`brd`), run:

```bash
sh scripts/validate_planning.sh --rewrite <output_dir>
```

Same for `--input` when it is a directory of cascade docs and differs from `output_dir`. `--rewrite` converts list-meta and `{stem}.yaml` to canonical `{stem}.md` and deletes the yaml sibling. Skip when no cascade files exist (greenfield). Do not treat yaml as a live `--format`.

## NL intent fallback

When no primary action flag is detected, map phrases (case-insensitive, first match wins):

| Intent signal | `action` |
|---------------|----------|
| setup, bootstrap planning, init plans | `setup` |
| from code, reverse from codebase, reverse-engineer discovery docs, discover from existing product source | `from-code` |
| discover, start discovery, new venture, greenfield problem, validate idea | `discover` |
| exec summary, executive summary, vision, problem statement, proceed/hold/kill memo | `executive-summary` |
| market, MRD, competitive landscape, beachhead | `mrd` |
| business requirements, BRD, stakeholders, objectives | `brd` |
| challenge, review, critique, devil's advocate, pre-mortem, red-team | `challenge` |
| resume, continue discovery, pick up where we left off | `discover` + `resume: true` |
| change, revise, patch the, update the ES/MRD/BRD/… | `change` (extract `--section` / `--target` from NL; missing both → `CHANGE_MISSING_SELECTORS`) |

`from-code` NL is listed **before** generic `discover` so reverse-from-source intent wins. When NL means Discover docs from source, **from-code wins over** the out-of-scope “code review” class below.

If multiple intent signals match with equal confidence → `AMBIGUOUS_ACTION`.

Match is token-aware, not naive substring: `review` does not match `code review`; `plan` in "plan a refactor" is out-of-scope code work (below), not discover.

### Out-of-scope NL

Runs only when **no primary action flag** is present **and** the NL intent table did not match. If either matched, skip this check (flags and discovery phrases win — e.g. `--discover` or "discover a billing problem").

If the utterance matches a **When not to use** class below → `OUT_OF_SCOPE`. Do not default `discover`. Do not start posture. Do not edit implementation files.

| Class | Match (case-insensitive; examples, not an exhaustive regex) |
|-------|--------------------------------------------------------------|
| Plan / PRD work | Request for PRD, product requirements, RICE/RIC, stories, feature backlog, `--prd`, or Plan entry without discovery freeze |
| Research phase | Post-compose market research, `--research`, competitor deep-dive as a research report |
| Code / ticket work | Implement, refactor, rewrite a service, review **code**, file tickets, tune production config, debug, or hotfix — **except** when NL matched `from-code` (Discover docs from source wins) |
| Artifact-type advice | Asking whether something should be a skill, command, agent, rule, or workflow — unless they asked to discover that product as a venture |
| Launch / GTM execution | Launch calendar, campaign plan, battlecard, growth-loop execution |

On `OUT_OF_SCOPE`: return `PhaseError` with `message` citing SKILL **When not to use**, and that they may pass `--discover` (or a level flag) for Discover, or load `rr-planner` for Plan/research.

### Posture hints (not an action)

NL tokens `greenfield`, `brownfield`, `existing`, `signed v1` **seed** the [project-posture.md](project-posture.md) confirm step. They are not a primary action flag and do not change `cascade_levels`. `greenfield` in the table above still maps to `discover` when no other action is present.

## Conflict matrix

| Dimension | Rule |
|-----------|------|
| Action | Exactly one primary action per invocation |
| Cascade focus | `--executive-summary` / `--exec-summary` / `--mrd` / `--brd` are mutually exclusive with `--discover`/`--all`/`--from-code` and with `--change` |
| `--change` | Primary only. Requires `--section` and `--target` (flags or NL). Combining with `--discover`/`--all`/`--from-code`/level flags/`--challenge` → `CONFLICTING_FLAGS`. Missing selectors → `CHANGE_MISSING_SELECTORS`. `--target prd` → `OUT_OF_SCOPE`. |
| `--challenge` / `--review` | Primary only. Requires existing docs (`--input` or `--output-dir`). Combining with another primary (e.g. `--discover --challenge` or `--from-code --challenge`) → `CONFLICTING_FLAGS`. `depth: deep` appends challenge to the **discover** chain only — not a second primary; never auto-appended for `from-code`. |
| `--setup` | Primary only. Bootstrap/repair. Combining with `--discover`/`--all`/`--from-code`/level flags/`--change`/`--challenge` → `CONFLICTING_FLAGS`. Never starts discover. |
| `--from-code` | Primary only. Exclusive with `--discover`/`--all`/level flags/`--change`/`--challenge`/`--setup` → `CONFLICTING_FLAGS`. Depth still trims stems; no auto challenge in chain. |
| `--prd` / `--research` | Never valid as discovery primaries → `OUT_OF_SCOPE` (not `CONFLICTING_FLAGS`) |
| Format | Single value only; must be `md` |
| Depth | `shallow` cannot combine with `--mrd` / `--brd` (those imply ancestors through that level) |

## Precedence

1. Explicit CLI flags beat NL intent.
2. Among explicit flags, left-to-right order in argv is tie-breaker for logging only; conflicts still error.
3. Defaults apply only after successful resolution (no error).
4. No explicit action flag, no NL intent match, and not out-of-scope → **Status-first routing** (below). `discover` only when that pick is `from-0`.

## Status-first routing

Load `docs/rr/rrr-status.yaml` (glance; fall back to legacy `docs/rrr-status.yaml`), then `{output_dir}/status.yaml` (or `{PROJECT_ROOT}/docs/rr/{track}/discovery/status.yaml` when `output_dir` is a next-track phase dir) and `session-state.json`. Pick **one** route. Do not start posture until this pick is done.

| `payload.route` | When |
|-----------------|------|
| `from-0` | No cascade `{stem}.md` for discovery stems. Greenfield discover **or** `--from-code` with empty stems. Summary / phase `status.yaml` / `agent.plan.md` alone do **not** count as in-progress. |
| `resume` | `--resume`, or NL continue, or checkpoint `paused` / `in_progress` with pending work. Promote `code-extraction` → `draft` when continue-shaping ([from-code.md](from-code.md)). |
| `continue-discover` | Cascade `{stem}.md` exists AND current-track discovery levels still `rev: ?` (unfrozen). Continue the open cascade. |
| `start-change` | `--change` (or NL change) and no in-flight change checkpoint. |
| `continue-change` | `--change` / NL change with an in-flight change on that section+target. |
| `continue-next-track` | `next` set and next-track docs still `?`; user is working that track (or `--target next`). |
| `ask` | Bare invoke, discovery docs frozen / `discovery_complete`, nothing open — **do not** rediscover. Ask: patch / `--change` / open-next / hand off to Plan / stop. **Also** `--from-code` when cascade stems already exist — no silent overwrite; ask before replace. |

`--discover` / `--all` / `--from-code` / a level flag **overrides** this pick (still expand `cascade_levels` as below). `--from-code` with existing stems still routes `ask` (no silent overwrite) unless the user confirms replace. Override does not skip unlock stops in `refs/planning/baselines.md`.

Classify patch vs redirect-to-next vs open-next vs unfreeze per `--change` above. Those are skill stops, not validator codes.

## Normalized payload schema

```json
{
  "action": "discover",
  "input": null,
  "output_dir": "{PROJECT_ROOT}/docs/rr/0.1/discovery/",
  "format": "md",
  "depth": "standard",
  "challenge_depth": "standard",
  "question_mode": "ask",
  "resume": false,
  "route": "from-0",
  "change_section": null,
  "change_target": null,
  "cascade_levels": ["executive-summary", "mrd", "brd"],
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
| `discover` | All three discovery levels (trimmed by `depth`) |
| `from-code` | Same depth trim as `discover` |
| `executive-summary` | `["executive-summary"]` |
| `mrd` | `["executive-summary", "mrd"]` |
| `brd` | `["executive-summary", "mrd", "brd"]` |
| `change` | Ancestors through `--target` level (same expansion as that level flag). Track from `--target` / `route`. |
| `challenge` | `[]` (reads existing docs) |
| `setup` | `[]` |

Never emit `prd` in discovery `cascade_levels`.

### `depth` trimming

| `depth` | Effective `cascade_levels` for `discover` / `from-code` |
|---------|-------------------------------------------|
| `shallow` | `["executive-summary"]` only |
| `standard` | all three |
| `deep` | all three; for `discover` only, `chain` appends `challenge` with `challenge_depth: deep` — **`from-code` never auto-appends challenge** |

### `chain` expansion

| `action` | Default `chain` |
|----------|-----------------|
| `discover` | `["discover", "compose"]` per level; after BRD freeze → handoff ([business-case-handoff.md](business-case-handoff.md)) |
| `from-code` | `["from-code", "compose"]` — **no** auto challenge; **no** freeze-handoff in this chain ([from-code.md](from-code.md)) |
| `challenge` | `["challenge"]` — mode from `challenge_depth` (default **standard**) |
| `setup` | `["setup"]` |
| single-level focus | `["discover", "compose"]` for specified levels |
| `change` | `["discover", "compose"]` for `cascade_levels` (patch / lock-target / unfreeze as classified) |

Ideation (when gated) runs skill-inline before L1 compose — not a separate `chain` action. **`from-code` skips ideation.** Humanize is skill-owned after compose draft — [compose-prose.md](compose-prose.md).

## Deterministic errors

Stop immediately; do not invoke agents. Return `PhaseError` with code below.

| Code | Condition |
|------|-----------|
| `AMBIGUOUS_ACTION` | Multiple primary actions after flag + NL resolution |
| `CONFLICTING_FLAGS` | Mutually exclusive flags (e.g. `--discover` + `--challenge`) |
| `INVALID_INPUT_PATH` | `--input` path does not exist |
| `MISSING_DOCS` | `--challenge` with no docs in input or output-dir |
| `MISSING_CHECKPOINT` | `--resume` but no `session-state.json` in `--output-dir` (after old-dir fallback) |
| `CHANGE_MISSING_SELECTORS` | `--change` (or NL change) without both section and target |
| `UNSUPPORTED_FORMAT` | Format not `md` (including `yaml` and `json`) |
| `UNSUPPORTED_DEPTH` | Depth not in allowed set |
| `OUT_OF_SCOPE` | `--prd` / `--research`, Plan/PRD NL, research-phase NL, code/ticket work, or artifact-type advice with no discovery primary |

Error response shape: see `refs/planning/contracts.md` `PhaseError`.
