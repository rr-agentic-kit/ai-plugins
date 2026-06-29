# input-resolution

**Owner:** Normalize raw flags and natural-language intent into a canonical payload before any agent invocation.

## Responsibilities

- Recognize primary action flags (exactly one per invocation).
- Parse shared selectors: `--input`, `--output-dir`, `--format`, `--depth`, `--text-mode`, `--resume`.
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

When no primary flag is present, default `action` = `discover`.

## Shared selectors

| Selector | Values | Default |
|----------|--------|---------|
| `--input` | file path or directory | null (use conversation context) |
| `--output-dir` | directory path | `docs/planning/` |
| `--format` | `md`, `json` | `md` |
| `--depth` | `shallow`, `standard`, `deep` | `standard` |
| `--text-mode` | _(flag, no value)_ | off — questions use `AskQuestion` |
| `--resume` | _(flag, no value)_ | off — start fresh or from `--input` |

### Question mode

| Flag | `question_mode` |
|------|-----------------|
| _(default)_ | `ask` — structured `AskQuestion` |
| `--text-mode` | `text` — questions inline in chat |

### Resume

| Flag | Behavior |
|------|----------|
| `--resume` | Load `session-state.json` from `--output-dir`; continue from `checkpoint.current_level` |
| Auto-resume | If `session-state.json` exists in `--output-dir` and user says "continue" / "resume" in NL → treat as `--resume` |

### Depth normalization

| Value | Discovery behavior |
|-------|-------------------|
| `shallow` | Exec-summary + PRD only; skip MRD/BRD/FRD unless explicitly flagged |
| `standard` | Full cascade with standard gates |
| `deep` | Full cascade + mandatory research phase + challenge pass |

### Input normalization

1. If `--input` is a directory, scan for existing planning docs (`exec-summary.md`, `mrd.md`, `brd.md`, `prd.md`, `frd.md`).
2. If `--input` is a file, treat as seed context for discovery.
3. Reject non-existent paths.

## NL intent fallback

When no primary action flag is detected (default `discover` still applies), map phrases (case-insensitive, first match wins):

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

## Conflict matrix

| Dimension | Rule |
|-----------|------|
| Action | Exactly one primary action per invocation |
| Cascade focus | `--exec-summary` through `--frd` are mutually exclusive with `--discover`/`--all` |
| `--research` | Standalone or appended after compose chain (not with `--challenge` as sole action unless docs exist) |
| `--challenge` / `--review` | Mutually exclusive with `--discover`/`--all`; requires existing docs via `--input` or `--output-dir` |
| Format | Single value only |
| Depth | `shallow` cannot combine with individual level flags below PRD |

## Precedence

1. Explicit CLI flags beat NL intent.
2. Among explicit flags, left-to-right order in argv is tie-breaker for logging only; conflicts still error.
3. Defaults apply only after successful resolution (no error).
4. No explicit action flag → `discover`.

## Normalized payload schema

```json
{
  "action": "discover",
  "input": null,
  "output_dir": "docs/planning/",
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
| `MISSING_CHECKPOINT` | `--resume` but no `session-state.json` in `--output-dir` |
| `UNSUPPORTED_FORMAT` | Format not in allowed set |
| `UNSUPPORTED_DEPTH` | Depth not in allowed set |

Error response shape: see [contracts.md](contracts.md) `PhaseError`.
