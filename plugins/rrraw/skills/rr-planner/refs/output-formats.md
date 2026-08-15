# output-formats

**Owner:** Doc file naming, md/yaml human adapters, JSON internals (`items.json`, `session-state.json`), and append-only Q&A history.

**Load when:** Write step — persisting artifacts to `--output-dir`. Also first Q&A (create/append `raw-history/`).

Item records: [doc-standards/item-schema.md](doc-standards/item-schema.md). Schema: [schemas/items.schema.json](schemas/items.schema.json).

## Layout

All files written to `payload.output_dir` (default `{PROJECT_ROOT}/docs/plans/`):

```
{PROJECT_ROOT}/docs/plans/
  exec-summary.md | exec-summary.yaml
  mrd.md | mrd.yaml
  brd.md | brd.yaml
  prd.md | prd.yaml
  frd.md | frd.yaml
  exec-summary.notes.yaml         # off-level sidecar (if any notes)
  mrd.notes.yaml
  brd.notes.yaml
  prd.notes.yaml
  frd.notes.yaml
  items.json                      # relationship graph only
  session-state.json              # internal checkpoint / agent I/O
  research-report.md | .yaml
  challenge-report.md | .yaml
  raw-history/
    2026-08-15T185203Z.yaml
```

| Doc type | Filename |
|----------|----------|
| exec-summary | `exec-summary.md` or `exec-summary.yaml` |
| mrd | `mrd.md` or `mrd.yaml` |
| brd | `brd.md` or `brd.yaml` |
| prd | `prd.md` or `prd.yaml` |
| frd | `frd.md` or `frd.yaml` |
| off-level notes | `{level}.notes.yaml` (always YAML; stub when first note appears) |
| item graph | `items.json` (always JSON) |
| session checkpoint | `session-state.json` (always JSON) |
| Q&A history | `raw-history/{UTC compact ISO-8601}.yaml` |
| research report | `research-report.md` or `.yaml` |
| challenge report | `challenge-report.md` or `.yaml` |

Create `--output-dir` if it does not exist. Create `raw-history/` on first Q&A. Create `{level}.notes.yaml` on first off-level note for that doc — even if the composed `{level}.md` does not exist yet.

`--format` selects the human-doc extension (`md` default, `yaml` alternative). `items.json` and `session-state.json` are always written as JSON. `{level}.notes.yaml` is always YAML — not selected by `--format`, not an item, **not validator input**. `--format json` is `UNSUPPORTED_FORMAT` — JSON is not a plan document format. Do not write `planning-bundle.json` or `session-log.md`. `decisions.json` is not a user artifact; decisions live in `session-state.json`.

## Markdown doc format

Each composed doc file:

```markdown
---
doc_type: prd
version: 1
created: 2026-06-24T10:00:00Z
traces_from: [exec-summary.md, mrd.md, brd.md]
---

# PRD: [Title]

[doc content from compose agent — item headings per item-schema]

## Item index

| ID | Parent | Spec | MoSCoW |
|----|--------|------|--------|
| PRD-3 | BRD-2 | draft | — |
| PRD-3.1 | PRD-3 | ready | Must |
```

Index column 4 is the level’s native field (`MoSCoW` / `Kano` / `Class`). Heading + metadata keys are a closed vocabulary — parser is regex, not an LLM.

## YAML doc format (`--format yaml`)

Same cascade docs, `.yaml` extension. Closed keys match the markdown header vocabulary as mappings under each item id. Skill serializes from compose `items[]` + prose; compose still returns JSON to the skill.

```yaml
doc_type: prd
version: 1
created: 2026-06-24T10:00:00Z
traces_from:
  - exec-summary.yaml
  - mrd.yaml
  - brd.yaml
title: Checkout

items:
  PRD-3:
    title: Checkout
    Parent: BRD-2
    Kind: container
    Spec: draft
  PRD-3.1:
    title: Guest checkout
    Parent: PRD-3
    Kind: leaf
    Spec: ready
    MoSCoW: Must
    body: |
      As a guest, I can complete checkout without an account.
```

| Rule | Detail |
|------|--------|
| Item ids | Keys under `items:` matching `{DOC}-{n}` / `{DOC}-{n.m}` |
| Closed keys | `Parent`, `Kind`, `Spec`, plus native method / FRD keys — same as md headers |
| `title` / `body` | Not closed metadata; title is the heading text; body is free prose (AI-judged) |
| Unranked / null | `—` or YAML `null` |
| Unknown keys | Validator FAIL (same as md) |
| Item index | Optional `item_index` list; not required for validation |

Do not wrap the human plan in a JSON bundle.

## `items.json`

Written on every compose (merged registry). Must match md headers or yaml closed keys; drift is a validator FAIL. Graph checks (parent walk, numbering, spec/build) run on this file.

```json
{
  "items": [
    {
      "id": "PRD-3.1",
      "parent": "PRD-3",
      "kind": "leaf",
      "spec": "ready",
      "priority_method": "moscow",
      "moscow": "Must",
      "title": "Guest checkout",
      "doc": "prd"
    }
  ]
}
```

## Raw-history YAML

Verbatim Q&A only. Decisions and assumptions stay in `session-state.json`. Append after **every** Q&A round (discovery, compose clarifications, stage-exit blind-spots). Pause still leaves reanalyzable history.

Filename: UTC compact ISO-8601 (`YYYY-MM-DDTHHMMSSZ.yaml`), e.g. `2026-08-15T185203Z.yaml`. One file per session. `--resume` appends to `session-state.raw_history_path`.

```yaml
session:
  started: 2026-08-15T18:52:03Z
  action: discover
  output_dir: /abs/path/docs/plans
  question_mode: ask
  depth: standard
turns:
  - ts: 2026-08-15T18:53:01Z
    level: exec-summary
    source: discovery
    question:
      id: q-001
      text: Who feels this pain?
      mode: ask
      options:
        - Engineering managers
        - ICs
        - Both equally
    answer:
      text: Engineering managers
      selected:
        - Engineering managers
```

| Field | Notes |
|-------|-------|
| `session.started` | ISO-8601 UTC of first Q&A (file create) |
| `session.action` | Normalized `action` |
| `session.output_dir` | Resolved output directory |
| `session.question_mode` | `ask` \| `text` |
| `session.depth` | `shallow` \| `standard` \| `deep` |
| `turns[].ts` | ISO-8601 UTC of the answer |
| `turns[].level` | Cascade level or `session` |
| `turns[].source` | `discovery` \| `compose` \| `blind-spots` \| `research` \| `challenge` \| `presave` |
| `turns[].question` | `id`, `text`, `mode`, `options[]` |
| `turns[].answer` | `text` (verbatim), `selected` (option labels when applicable) |

Append-only: never rewrite prior turns. Create `raw-history/` on first Q&A. If the session file is missing on resume, create a new timestamped file and update `raw_history_path`.

## Session checkpoint (`session-state.json`)

Written on **every stop** and after **each level completion**. Required for `--resume`. Internal only — not a human plan doc.

```json
{
  "metadata": {
    "action": "discover",
    "depth": "standard",
    "question_mode": "ask",
    "format": "md",
    "output_dir": "{PROJECT_ROOT}/docs/plans/",
    "raw_history_path": "raw-history/2026-08-15T185203Z.yaml",
    "updated": "ISO-8601"
  },
  "checkpoint": {
    "status": "paused|in_progress|complete",
    "current_level": "brd",
    "pending_clarifications": [],
    "levels_completed": ["exec-summary", "mrd"]
  },
  "decisions": [],
  "assumptions": [],
  "level_facts": {},
  "composed_docs": {},
  "item_registry": {},
  "frozen_levels": ["exec-summary", "mrd"],
  "project_posture": {
    "existence": "greenfield",
    "commitment": "unsigned",
    "source": "user_confirmed",
    "user_confirmed": true,
    "signed_set": [],
    "shipped_summary": null
  },
  "note_sessions": {},
  "pending_agent_output": null
}
```

`raw_history_path` is relative to `output_dir`. Resume loads this file, continues from `checkpoint.current_level`, and appends Q&A to that history file.

`item_registry`: id → `{ doc, parent, kind, spec, class? }`. Resume and re-compose remap child `parent:` from this map.

`project_posture`: confirmed existence × commitment ([project-posture.md](project-posture.md)). Resume skips the posture gate when `user_confirmed` is true and uncontradicted.

`note_sessions`: per-level index of parked notes; body is `{level}.notes.yaml` ([note-sessions.md](note-sessions.md)). Sidecars are not `--format` docs and are not parsed by `validate_planning.py`.

## Status merge

| Source | `final_status` |
|--------|----------------|
| All levels `ok`, success-criteria pass (static script + judgment) | `ok` |
| User stopped mid-session or accepted partial gaps | `partial` |
| Input-resolution error or unrecoverable agent failure | `failed` |

## Adapter rules

1. Never overwrite without user confirmation if files exist and `--input` did not imply refresh.
2. Always write `session-state.json` on stop or level completion for resume (include `raw_history_path`, `project_posture` once confirmed, `note_sessions`).
3. Always write `items.json` after compose (both `md` and `yaml` formats).
4. Append a raw-history turn after every Q&A; do not wait for stage-exit.
5. Write/append `{level}.notes.yaml` when an off-level answer is parked; do not put parked prose in item headings.
6. Research and challenge reports are standalone files, not merged into cascade docs. Extension follows `--format`.
7. Skill writes human files. Agents return JSON (`doc_content` + `items[]`); when `format: yaml`, skill serializes closed-key YAML from `items[]` + prose.
8. After write, skill runs `python3 scripts/validate_planning.py <output-dir>` (plugin root). Pass `--format md|yaml` when known; otherwise the script sniffs `.md`/`.yaml`. FAIL blocks `final_status: ok`. Sidecars are not validator input.
9. Pause does not run pre-save reflection and does not write unfrozen composed docs.
