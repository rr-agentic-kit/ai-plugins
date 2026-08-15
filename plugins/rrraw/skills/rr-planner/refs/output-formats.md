# output-formats

**Owner:** Doc file naming, chat-log format, and md/json output adapters.

**Load when:** Write step — persisting artifacts to `--output-dir`.

Item records: [doc-standards/item-schema.md](doc-standards/item-schema.md). Schema: [schemas/items.schema.json](schemas/items.schema.json).

## File naming

All files written to `payload.output_dir` (default `docs/planning/`):

| Doc type | Filename |
|----------|----------|
| exec-summary | `exec-summary.md` |
| mrd | `mrd.md` |
| brd | `brd.md` |
| prd | `prd.md` |
| frd | `frd.md` |
| item registry | `items.json` |
| session checkpoint | `session-state.json` |
| session log | `session-log.md` |
| decisions export | `decisions.json` |
| research report | `research-report.md` |
| challenge report | `challenge-report.md` |

Create `--output-dir` if it does not exist.

**Always write `items.json`** (union of all composed items), including when `--format md`. `--format json` also embeds the same records in `planning-bundle.json`.

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

## `items.json`

Written on every compose (merged registry). Must match markdown headers; drift is a validator FAIL.

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

## Session log format

`session-log.md` captures the planning conversation arc:

```markdown
# Planning Session Log

**Started:** ISO-8601
**Action:** discover
**Depth:** standard

## Decisions

| ID | Level | Decision | Goal ref |
|----|-------|----------|----------|
| d-001 | exec-summary | ... | ES-1 |

## Assumptions

| ID | Level | Assumption | Validated |
|----|-------|------------|-----------|
| a-001 | mrd | ... | false |

## Level progression

### exec-summary
- Status: ok
- Frozen: true

### mrd
- Status: in_progress

## Clarifications

| # | Level | Question | Answer |
|---|-------|----------|--------|
| 1 | brd | ... | ... |

## Checkpoints

| Timestamp | Status | Level | Notes |
|-----------|--------|-------|-------|
| ISO-8601 | paused | brd | User requested stop |
```

## Session checkpoint (`session-state.json`)

Written on **every stop** and after **each level completion**. Required for `--resume`.

```json
{
  "metadata": {
    "action": "discover",
    "depth": "standard",
    "question_mode": "ask",
    "output_dir": "docs/planning/",
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
  "pending_agent_output": null
}
```

`item_registry`: id → `{ doc, parent, kind, spec, class? }`. Resume and re-compose remap child `parent:` from this map.

Resume loads this file and continues from `checkpoint.current_level`.

## JSON format (`--format json`)

Write `planning-bundle.json` **and** `items.json`:

```json
{
  "metadata": {
    "action": "discover",
    "depth": "standard",
    "output_dir": "docs/planning/",
    "created": "ISO-8601",
    "final_status": "ok|partial|failed"
  },
  "docs": {
    "exec-summary": { "content": "...", "status": "ok" },
    "mrd": { "content": "...", "status": "ok" }
  },
  "items": [],
  "session_state": {
    "decisions": [],
    "assumptions": [],
    "level_facts": {},
    "item_registry": {},
    "frozen_levels": []
  },
  "research": null,
  "challenge": null,
  "resolution_trace": {}
}
```

`items` in the bundle is the same array as `items.json`. When `format: md` (default), also write individual `.md` files plus `session-log.md`.

## Status merge

| Source | `final_status` |
|--------|----------------|
| All levels `ok`, success-criteria pass (static script + judgment) | `ok` |
| User stopped mid-session or accepted partial gaps | `partial` |
| Input-resolution error or unrecoverable agent failure | `failed` |

## Adapter rules

1. Never overwrite without user confirmation if files exist and `--input` did not imply refresh.
2. Include `resolution_trace` in json output.
3. Always write `session-state.json` on stop or level completion for resume.
4. Always write `items.json` after compose (md and json formats).
5. Chat log is append-friendly — new session creates new log or timestamps section if continuing.
6. Research and challenge reports are standalone files, not merged into doc files.
7. After write, skill runs `python3 scripts/validate_planning.py <output-dir>` (plugin root). FAIL blocks `final_status: ok`.
