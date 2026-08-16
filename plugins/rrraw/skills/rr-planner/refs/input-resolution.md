# input-resolution

**Owner:** Normalize raw flags and natural-language intent into a canonical payload before any agent invocation.

## Responsibilities

- Recognize primary action flags (exactly one per invocation).
- Parse shared selectors: `--input`, `--output-dir`, `--format`, `--depth`, `--text-mode`, `--resume`.
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
| `--research` | `research` |
| `--challenge` | `challenge` |
| `--review` | `challenge` |

When no primary flag is present, do not emit a payload yet. Run **NL intent fallback**, then **Out-of-scope NL**, then default `action` = `discover` only if neither matched.

## Project root

`PROJECT_ROOT`:

1. `git rev-parse --show-toplevel` if the working tree is a git repo.
2. Else workspace / current working directory root.

Default `output_dir` = `{PROJECT_ROOT}/docs/plans/`. `--output-dir` always wins.

## Shared selectors

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file path or directory | null (use conversation context) |
| `--output-dir` | directory path | `{PROJECT_ROOT}/docs/plans/` |
| `--format` | `md` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag, no value)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag, no value)_ | off — start fresh or from `--input` |

`--format yaml` and `--format json` are not plan-document formats. Do **not** alias either to md. Emit `UNSUPPORTED_FORMAT`.

Allowed JSON on disk (not selected by `--format`): `items.json` (item graph) and `session-state.json` (resume / agent shared state). Agent `Task` payloads stay JSON (internal). `payload.format` stays `"md"`.

### Question mode

| Flag | `question_mode` |
|------|-----------------|
| _(default)_ | `ask` — structured `AskQuestion` |
| `--text-mode` | `text` — questions inline in chat |

### Resume

| Flag | Behavior |
|------|----------|
| `--resume` | Load `session-state.json` from `--output-dir`; continue from `checkpoint.current_level`; append Q&A to `raw_history_path` |
| Auto-resume | If `session-state.json` exists in `--output-dir` and user says "continue" / "resume" in NL → treat as `--resume` |

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
| discover, plan, start planning, new project, greenfield | `discover` |
| exec summary, vision, problem statement | `exec-summary` |
| market, MRD, competitive landscape | `mrd` |
| business requirements, BRD, stakeholders | `brd` |
| product requirements, PRD, features | `prd` |
| functional, FRD, technical requirements | `frd` |
| research, market research, competitors | `research` |
| challenge, review, critique, devil's advocate | `challenge` |
| resume, continue planning, pick up where we left off | `discover` + `resume: true` |

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
| Cascade focus | `--exec-summary` through `--frd` are mutually exclusive with `--discover`/`--all` |
| `--research` | Primary only. Requires existing docs (`--input` or `--output-dir`). Combining with another primary (e.g. `--discover --research`) → `CONFLICTING_FLAGS`. Research+challenge append is `depth: deep` only (`chain` += `research`, `challenge`) — not a second primary. |
| `--challenge` / `--review` | Primary only. Requires existing docs (`--input` or `--output-dir`). Combining with another primary (e.g. `--discover --challenge`) → `CONFLICTING_FLAGS`. Same `depth: deep` append as `--research` — not a second primary. |
| Format | Single value only; must be `md` |
| Depth | `shallow` cannot combine with individual level flags below PRD |

## Precedence

1. Explicit CLI flags beat NL intent.
2. Among explicit flags, left-to-right order in argv is tie-breaker for logging only; conflicts still error.
3. Defaults apply only after successful resolution (no error).
4. No explicit action flag, no NL intent match, and not out-of-scope → `discover`.

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
| `research` | `[]` (reads existing docs) |
| `challenge` | `[]` (reads existing docs) |

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
| single-level focus | `["discover", "compose"]` for specified levels |

## Deterministic errors

Stop immediately; do not invoke agents. Return `PhaseError` with code below.

| Code | Condition |
|------|-----------|
| `AMBIGUOUS_ACTION` | Multiple primary actions after flag + NL resolution |
| `CONFLICTING_FLAGS` | Mutually exclusive flags (e.g. `--discover` + `--challenge`) |
| `INVALID_INPUT_PATH` | `--input` path does not exist |
| `MISSING_DOCS` | `--challenge` or `--research` with no docs in input or output-dir |
| `MISSING_CHECKPOINT` | `--resume` but no `session-state.json` in `--output-dir` (after old-dir fallback) |
| `UNSUPPORTED_FORMAT` | Format not `md` (including `yaml` and `json`) |
| `UNSUPPORTED_DEPTH` | Depth not in allowed set |
| `OUT_OF_SCOPE` | No primary flag, no NL planning match, and utterance matches **When not to use** (code/ticket work or artifact-type advice) |

Error response shape: see [contracts.md](contracts.md) `PhaseError`.
