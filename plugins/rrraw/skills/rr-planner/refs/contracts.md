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
| `artifacts` | string[] | File paths written by the **skill** (informational). Agents do not write files. |

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

```json
{
  "doc_type": "prd",
  "doc_content": "# PRD\n...",
  "sections_completed": ["overview", "goals", "requirements"],
  "sections_incomplete": [],
  "clarifications_needed": [],
  "items": [{
    "id": "PRD-3.1",
    "parent": "PRD-3",
    "kind": "leaf",
    "spec": "ready",
    "build": null,
    "supersedes": null,
    "superseded_by": null,
    "priority_method": "moscow",
    "moscow": "Must",
    "kano": null,
    "triad": null,
    "title": "Guest checkout",
    "doc": "prd"
  }],
  "id_remap": {},
  "assumptions_used": ["a-001"]
}
```

Item identity, closed markdown/yaml keys, spec/build: [doc-standards/item-schema.md](doc-standards/item-schema.md). JSON Schema: [schemas/items.schema.json](schemas/items.schema.json).

| Field | Notes |
|-------|-------|
| `doc_type` | One of: `exec-summary`, `mrd`, `brd`, `prd`, `frd` |
| `doc_content` | Full document per `--format`: markdown templates, or closed-key YAML mappings. Skill writes the file; agent does not. |
| `sections_completed` | Required sections with content |
| `sections_incomplete` | Required sections with gaps |
| `clarifications_needed` | `ClarificationItem[]` — non-empty blocks `status: ok` |
| `items` | Records for this doc; skill merges into `items.json` / `item_registry`. Shape: `{ id, parent, kind, spec, build?, supersedes?, superseded_by?, priority_method, moscow?, kano?, triad?, title, doc }` |
| `id_remap` | Old id → new id when re-composing a frozen level; empty object otherwise |
| `assumptions_used` | Assumption ids referenced in doc |

Compose **requires** `session_state.project_posture` with `user_confirmed: true`. Missing → `clarifications_needed` (`severity: blocking`), `status: partial` — do not invent a legend.

Compose consumes `session_state.note_sessions[doc_type]` (and the matching `{level}.notes.yaml`) into `level_facts` **for the current `doc_type` only**. Do not mint items from notes belonging to other levels.

PRD release-phasing prose is derived from the posture MoSCoW legend ([project-posture.md](project-posture.md)). Do not assume Must = MVP.

`parent` is the immediate parent id (`null` in JSON / `—` in markdown for ES roots). `build` is omitted or `null` except FRD leaves. `priority_method` is the document type’s method (`moscow` \| `kano` \| `triad`); unranked leaves set the native field to `null`. `triad` is `{ if_present, if_absent, if_wrong, class }` with each axis `{ effect, magnitude }`.

| `status` | When |
|----------|------|
| `ok` | All required sections complete; `clarifications_needed` empty |
| `partial` | Doc written but gaps remain or clarifications needed |
| `failed` | Cannot render doc (e.g. missing parent level facts) |

### research

```json
{
  "findings": [{
    "id": "r-001",
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
| `findings` | Cited market/competitor/standards evaluation |
| `citations` | Required for each finding — no unsourced claims |
| `refinement_signals` | Suggested doc updates (skill/user applies via re-discover) |
| `clarifications_needed` | Blocking gaps that research cannot resolve without user input |

| `status` | When |
|----------|------|
| `ok` | Research complete; no blocking clarifications; user confirmed done or no new findings |
| `partial` | User stopped mid-research or unresolved clarifications remain |
| `failed` | No docs to evaluate or research scope error |

### challenge

```json
{
  "findings": [{
    "id": "bs-001",
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

`docs_reviewed` uses the actual filenames (`.yaml` when `--format yaml`).

| Field | Notes |
|-------|-------|
| `findings` | Per [blind-spots.md](blind-spots.md) taxonomy **union** — judgment only when `payload.static_validation.status` is `passed` or `failed`. Do not apply per-level `in_scope` (that is skill-inline stage-exit). Include posture and off-level-misfile findings (`temporal` / `traceability_breaks`). |
| `comparison_tables` | When single-option decisions lack alternatives analysis |
| `clarifications_needed` | Questions that block severity assessment |
| `docs_reviewed` | All docs scanned (`.md` or `.yaml` per `--format`) |

Input (on `PhaseInput.payload`, not in this `data` object): `static_validation` = `{ "status": "passed|failed|skipped", "errors": [] }` from `validate_planning.py`. If `passed`/`failed`, do not re-check refs. If `skipped`, may flag build-on-non-ready.

| `status` | When |
|----------|------|
| `ok` | Full taxonomy scan complete |
| `partial` | Some docs unreadable or clarifications pending |
| `failed` | No docs found in scope |

---

## NormalizedPayload reference

Shape and field rules: [input-resolution.md](input-resolution.md). Embedded as `PhaseInput.payload`.
