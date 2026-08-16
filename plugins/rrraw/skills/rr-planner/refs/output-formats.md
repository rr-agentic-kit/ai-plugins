# output-formats

**Owner:** Doc file naming, markdown cascade docs, JSON internals (`items.json`, `session-state.json`), and append-only Q&A history.

**Load when:** After compose (cascade docs already on disk); skill persist of `session-state.json` / `raw-history/` / notes; first Q&A.

Item records: [doc-standards/item-schema.md](doc-standards/item-schema.md). Schema: [schemas/items.schema.json](schemas/items.schema.json).

## Layout

All files written to `payload.output_dir` (default `{PROJECT_ROOT}/docs/plans/`):

```
{PROJECT_ROOT}/docs/plans/
  exec-summary.md
  mrd.md
  brd.md
  prd.md
  frd.md
  exec-summary.notes.yaml         # same write/load/delete as every {level}.notes.yaml; only while unresolved
  mrd.notes.yaml
  brd.notes.yaml
  prd.notes.yaml
  frd.notes.yaml
  items.json                      # relationship graph only
  decision-ledger.yaml            # evidence + rationale graph (skill-owned; validator input)
  session-state.json              # internal checkpoint / agent I/O
  research-report.md
  challenge-report.md
  raw-history/
    2026-08-15T185203Z.yaml
```

| Doc type | Filename |
|----------|----------|
| exec-summary | `exec-summary.md` |
| mrd | `mrd.md` |
| brd | `brd.md` |
| prd | `prd.md` |
| frd | `frd.md` |
| off-level notes | `{level}.notes.yaml` (always YAML; same write/load/delete for every level; exists only while unresolved) |
| item graph | `items.json` (always JSON) |
| decision ledger | `decision-ledger.yaml` (always YAML; skill-owned; validator input) |
| session checkpoint | `session-state.json` (always JSON) |
| Q&A history | `raw-history/{UTC compact ISO-8601}.yaml` |
| research report | `research-report.md` |
| challenge report | `challenge-report.md` |

Create `--output-dir` if it does not exist. Create `raw-history/` on first Q&A. Create `{level}.notes.yaml` on first off-level note for that doc — even if the composed `{level}.md` does not exist yet. File exists only while unresolved notes remain; skill deletes it when empty after compose persist.

`--format` allowed value is `md` only. `yaml` and `json` → `UNSUPPORTED_FORMAT` ([input-resolution.md](input-resolution.md)). `payload.format` stays `"md"`. `items.json` and `session-state.json` are always JSON. `decision-ledger.yaml` is always YAML — skill-owned, validator input, not selected by `--format`. `{level}.notes.yaml` is always YAML — not selected by `--format`, not an item, **not validator input**. Cascade `{stem}.yaml` is stale input for `--rewrite`, not a live format. Do not write `planning-bundle.json` or `session-log.md`. `decisions.json` is not a user artifact; decisions live in `session-state.json`. Reason-graph bodies live in `decision-ledger.yaml`, not the decision log.

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

[doc content from compose agent — item headings + `_key_:` line + `>` body per item-schema]

## Item index

| ID | Parent | Spec | MoSCoW |
|----|--------|------|--------|
| PRD-3 | BRD-2 | draft | — |
| PRD-3.1 | PRD-3 | ready | Must |
```

Index column 4 is the level’s native field (`MoSCoW` / `Kano` / `Class`). Heading + `_key_:` metadata are a closed vocabulary — parser is regex, not an LLM. Item templates: [doc-standards/item-schema.md](doc-standards/item-schema.md).

## `items.json`

Compose merges this file on every invocation (read-modify-write: replace only this `doc`’s records; do not clobber other levels). Must match md `_key_:` headers; drift is a validator FAIL. Graph checks (parent walk, numbering, spec/build) run on this file. Skill reads it after compose to refresh `item_registry` — never copies item records through chat.

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
      "rationale": "r-014",
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
| `turns[].source` | `discovery` \| `compose` \| `blind-spots` \| `research` \| `challenge` \| `presave` \| `panel` |
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
    "status": "paused|in_progress|complete|blocked",
    "current_level": "brd",
    "pending_clarifications": [],
    "levels_completed": ["exec-summary", "mrd"]
  },
  "decisions": [],
  "assumptions": [],
  "level_facts": {},
  "composed_docs": {
    "exec-summary": "exec-summary.md",
    "mrd": "mrd.md"
  },
  "item_registry": {},
  "frozen_levels": ["exec-summary", "mrd"],
  "project_posture": {},
  "viability": [
    {
      "level": "exec-summary",
      "verdict": "proceed",
      "conditions": [],
      "dissent": [],
      "binding": true
    }
  ],
  "note_sessions": {}
}
```

`raw_history_path` is relative to `output_dir`. Resume loads this file, continues from `checkpoint.current_level`, and appends Q&A to that history file.

`composed_docs`: `doc_type` → path relative to `output_dir`. Paths only — never document bodies. Do not stash compose output in session-state; compose writes immediately.

`item_registry`: id → `{ doc, parent, kind, spec, class? }`. Skill refreshes this from `items.json` after compose. Resume uses it for minting. Frozen re-compose remap of child `parent:` is compose’s job in the same invocation.

`project_posture`: `{}` until confirm; then the Session field in [project-posture.md](project-posture.md). Resume skips the posture gate when `user_confirmed` is true and uncontradicted.

`viability[]`: Gate 7 / premise-test verdicts ([expert-panel.md](expert-panel.md)). Binding at exec-summary and MRD.

`note_sessions`: per-level index of parked notes; body is `{level}.notes.yaml` ([note-sessions.md](note-sessions.md)). Drop the key when that sidecar is deleted. Sidecars are not `--format` docs and are not parsed by `validate_planning.py`.

Skill owns `decision-ledger.yaml` ([decision-ledger.md](decision-ledger.md)). Compose and challenge never write it. Validator loads it when present.

## Status merge

| Source | `final_status` |
|--------|----------------|
| All levels `ok`, success-criteria pass (static script + judgment); queue empty; no binding `hold`/`kill` | `ok` |
| User stopped mid-session or accepted partial gaps | `partial` |
| Binding `hold`, unresolved `kill`, or open re-decision queue | `blocked` |
| Input-resolution error or unrecoverable agent failure | `failed` |

## Adapter rules

1. Overwrite confirm: [cascade.md](cascade.md) per-level discovery step 8. Skip the prompt when `--input` implied refresh.
2. Always write `session-state.json` on stop or level completion for resume (include `raw_history_path`, `project_posture` once confirmed, `viability[]`, `note_sessions`, `composed_docs` paths). Skill is the only writer of this file. Skill is also the only writer of `decision-ledger.yaml`.
3. Compose writes/merges `items.json`. Skill reads it; skill does not write it. Compose reads `reserved_ids` from the ledger and never re-mints those ids.
4. Append a raw-history turn after every Q&A; do not wait for stage-exit. Skill owns `raw-history/`.
5. Write/append `{level}.notes.yaml` when an off-level answer is parked; do not put parked prose in item headings. Skill owns sidecars; prune: [note-sessions.md](note-sessions.md).
6. Research and challenge reports are standalone `.md` files, not merged into cascade docs. Skill persists those reports from findings JSON.
7. Compose writes human cascade docs (`{level}.md` only). Document bodies never travel through chat. Research/challenge still return findings JSON.
8. After compose Task: parse slim receipt → if clarifications, ask and re-invoke → else read `items.json` to refresh `item_registry` → Gate 3 static ([success-criteria.md](success-criteria.md)). FAIL blocks `final_status: ok`. Sidecars are not validator input.
9. Pause skips pre-save ([proactivity.md](proactivity.md)). Freeze is a `frozen_levels` update, not a second write of the doc ([cascade.md](cascade.md)).
