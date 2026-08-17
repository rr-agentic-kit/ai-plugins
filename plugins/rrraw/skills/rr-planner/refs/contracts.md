# contracts

**Owner:** Shared input/output/error schemas for all phase agents and the skill orchestrator.

## Core types

### PhaseInput

Base envelope passed to every agent (via Task prompt + JSON block).

```json
{
  "payload": {},
  "phase": "compose",
  "level": "prd",
  "epoch": 1,
  "round": 1,
  "prior_outputs": {},
  "session_state": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `payload` | `NormalizedPayload` | From [input-resolution.md](input-resolution.md) |
| `phase` | string | Current agent phase name |
| `level` | string | Cascade level (`exec-summary`, `mrd`, `brd`, `prd`, `frd`) or null for research/challenge |
| `epoch` | integer | 1-based; 1 for single-shot flows |
| `round` | integer | Clarification iteration counter within a level (informational; no cap) |
| `prior_outputs` | object | Keyed by phase name; prior structured outputs in chains |
| `session_state` | object | Accumulated facts, decisions, assumptions, `item_registry`, `frozen_levels`, `project_posture`, `note_sessions` from [cascade.md](cascade.md) |

### PhaseOutput

```json
{
  "phase": "compose",
  "status": "ok",
  "summary": "string",
  "artifacts": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Agent that produced this output |
| `status` | `ok` \| `partial` \| `failed` | Completion state |
| `data` | object | Phase-specific contract (below) |
| `summary` | string | One-line human summary |
| `artifacts` | string[] | Paths **this agent** wrote this invocation. Compose: the cascade doc, `items.json`, rewritten child docs. Research/challenge: empty — skill persists those reports. |

### PhaseError

```json
{
  "code": "AMBIGUOUS_ACTION",
  "message": "human-readable",
  "details": {}
}
```

Used by input-resolution and orchestrator hard-stops. Agents return `status: failed` with `data.error` matching this shape when execution cannot continue.

### ClarificationItem

Shared across compose, research, and challenge agents:

```json
{
  "id": "c-001",
  "question": "Who is the primary buyer vs user?",
  "context": "BRD lists two personas with conflicting priorities",
  "severity": "blocking|high|medium|low",
  "suggested_options": ["Enterprise IT buyer", "End-user team lead", "Both equally"],
  "level": "brd",
  "section": "stakeholders"
}
```

Agents **never** prompt the user directly. They return `clarifications_needed[]`; the skill surfaces per `payload.question_mode` (`ask` → `AskQuestion`, `text` → inline chat). Loop until list is empty or user says done.

## Parsing policy

1. Agent final message must be valid JSON matching `PhaseOutput` for its phase.
2. One retry on parse failure.
3. Second failure → orchestrator hard-stop with `code: AGENT_OUTPUT_PARSE_FAILED`.

---

## Per-agent output contracts (`data` field)

### compose

Compose **must** persist `{level}.md` and merge this level into `items.json`, then return a slim receipt. Compose PhaseOutput must never include `doc_content`, `items[]`, or a document body; a fat receipt means the contract failed.

```json
{
  "doc_type": "prd",
  "doc_path": "prd.md",
  "sections_completed": ["overview", "goals", "requirements"],
  "sections_incomplete": [],
  "clarifications_needed": [],
  "id_remap": {},
  "items_removed": [],
  "assumptions_used": ["a-001"]
}
```

Item identity, closed `_key_:` markdown, spec/build: [doc-standards/item-schema.md](doc-standards/item-schema.md). JSON Schema: [schemas/items.schema.json](schemas/items.schema.json). Records live in `items.json` on disk — not in this receipt. Skill refreshes `item_registry` by reading `items.json`.

| Field | Notes |
|-------|-------|
| `doc_type` | One of: `exec-summary`, `mrd`, `brd`, `prd`, `frd` |
| `doc_path` | Path of the file this agent just wrote (`{level}.md`) |
| `sections_completed` | Required sections with content |
| `sections_incomplete` | Required sections with gaps |
| `clarifications_needed` | `ClarificationItem[]` — non-empty blocks `status: ok` |
| `id_remap` | Old id → new id when re-composing a frozen level; empty object otherwise. Same invocation rewrites child-doc `parent:` and `items.json`. |
| `items_removed` | Ids dropped from this `doc` in `items.json` this invocation (kill/burial). Empty list otherwise. Skill already wrote `graveyard` / `reserved_ids` before compose, or updates from this list. |
| `assumptions_used` | Assumption ids referenced in doc |

`artifacts[]` on the envelope lists paths this agent wrote (`doc_path`, `items.json`, rewritten child docs).

Execution (posture required, notes ingest, sidecar prune): [project-posture.md](project-posture.md), [note-sessions.md](note-sessions.md). Must≠MVP / MoSCoW legend: [project-posture.md](project-posture.md). `reserved_ids` / ledger read-only: [decision-ledger.md](decision-ledger.md). Item records: [doc-standards/item-schema.md](doc-standards/item-schema.md).

| `status` | When |
|----------|------|
| `ok` | All required sections complete; `clarifications_needed` empty; files persisted |
| `partial` | Doc persisted but gaps remain or clarifications needed |
| `failed` | Cannot render doc (e.g. missing parent level facts) — do not persist |

### research

```json
{
  "findings": [{
    "id": "rf-001",
    "topic": "Competitive landscape",
    "summary": "",
    "citations": [{ "title": "", "url": "", "accessed": "ISO-8601" }],
    "impact": "confirms|contradicts|extends",
    "affected_docs": ["mrd", "prd"],
    "refinement_signals": [{
      "doc_ref": "mrd.md § competitors",
      "signal": "Add emerging competitor X",
      "severity": "medium"
    }]
  }],
  "clarifications_needed": [],
  "rounds_completed": 1
}
```

| Field | Notes |
|-------|-------|
| `findings` | Cited market/competitor/standards evaluation. Finding ids use `rf-` (not `r-`, which is ledger rationale) |
| `citations` | Required for each finding — no unsourced claims |
| `refinement_signals` | Suggested doc updates (skill/user applies via re-discover) |
| `clarifications_needed` | Blocking gaps that research cannot resolve without user input |

| `status` | When |
|----------|------|
| `ok` | No new material findings this invocation; no blocking clarifications |
| `partial` | Unresolved clarifications remain |
| `failed` | No docs to evaluate or research scope error |

### challenge

```json
{
  "findings": [{
    "id": "bs-001",
    "doc": "frd",
    "category": "failure_modes",
    "severity": "high",
    "doc_ref": "frd.md § 3.2",
    "finding": "",
    "evidence": "",
    "recommendation": "",
    "alternatives": []
  }],
  "comparison_tables": [{
    "decision_ref": "prd § approach",
    "options": [],
    "recommendation": ""
  }],
  "clarifications_needed": [],
  "docs_reviewed": ["exec-summary.md", "mrd.md", "brd.md", "prd.md", "frd.md"]
}
```

`docs_reviewed` uses the actual filenames (always `.md`).

| Field | Notes |
|-------|-------|
| `findings` | Per [blind-spots.md](blind-spots.md) taxonomy **union** (not per-level `in_scope`). Judgment only when `payload.static_validation.status` is `passed` or `failed`. Ledger scan: [decision-ledger.md](decision-ledger.md) Challenge. |
| `findings[].doc` | Cascade stem (`exec-summary` … `frd`). Required. Skill stamps per-doc `challenge.status` and routes Address now from this field. |
| `findings[].doc_ref` | Human locator (`frd.md § 3.2`). Keep even when `doc` is set. |
| `comparison_tables` | When single-option decisions lack alternatives analysis |
| `clarifications_needed` | Questions that block severity assessment |
| `docs_reviewed` | All docs scanned (`.md`) |

Input (on `PhaseInput.payload`, not in this `data` object): `static_validation` = `{ "status": "passed|failed|skipped", "errors": [] }` from `validate_planning.sh`. Static vs judgment: [success-criteria.md](success-criteria.md).

| `status` | When |
|----------|------|
| `ok` | Full taxonomy scan complete |
| `partial` | Some docs unreadable or clarifications pending |
| `failed` | No docs found in scope |

---

## NormalizedPayload reference

Shape and field rules: [input-resolution.md](input-resolution.md). Embedded as `PhaseInput.payload`. Includes `route` (`from-0` / `resume` / `continue-discover` / `start-change` / `continue-change` / `continue-next-track` / `ask`) and `--change` selectors `change_section` / `change_target`.
