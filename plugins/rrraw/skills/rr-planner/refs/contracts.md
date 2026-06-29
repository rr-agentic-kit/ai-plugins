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
| `session_state` | object | Accumulated facts, decisions, assumptions from [cascade.md](cascade.md) |

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
| `artifacts` | string[] | File paths written (informational) |

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
  "traceability": [{
    "req_id": "prd-req-1",
    "traces_to": "brd-obj-2",
    "goal_ref": "exec-vision"
  }],
  "assumptions_used": ["a-001"]
}
```

| Field | Notes |
|-------|-------|
| `doc_type` | One of: `exec-summary`, `mrd`, `brd`, `prd`, `frd` |
| `doc_content` | Full markdown document per [doc-standards/](doc-standards/) |
| `sections_completed` | Required sections with content |
| `sections_incomplete` | Required sections with gaps |
| `clarifications_needed` | `ClarificationItem[]` — non-empty blocks `status: ok` |
| `traceability` | Parent links for requirements/objectives |
| `assumptions_used` | Assumption ids referenced in doc |

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

| Field | Notes |
|-------|-------|
| `findings` | Per [blind-spots.md](blind-spots.md) taxonomy |
| `comparison_tables` | When single-option decisions lack alternatives analysis |
| `clarifications_needed` | Questions that block severity assessment |
| `docs_reviewed` | All docs scanned |

| `status` | When |
|----------|------|
| `ok` | Full taxonomy scan complete |
| `partial` | Some docs unreadable or clarifications pending |
| `failed` | No docs found in scope |

---

## NormalizedPayload reference

Emitted by input-resolution; embedded in `PhaseInput.payload`:

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
  "resolution_trace": {}
}
```

Full schema: [input-resolution.md](input-resolution.md).
