# contracts

**Owner:** Shared input/output/error schemas for all phase agents and the skill orchestrator.

## Core types

### PhaseInput

Base envelope passed to every agent (via Task prompt + JSON block).

```json
{
  "payload": {},
  "phase": "assess",
  "epoch": 1,
  "prior_outputs": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `payload` | `NormalizedPayload` | From [input-resolution.md](input-resolution.md) |
| `phase` | string | Current agent phase name |
| `epoch` | integer | 1-based; 1 for single-shot flows |
| `prior_outputs` | object | Keyed by phase name; prior structured outputs in chains |

### PhaseOutput

```json
{
  "phase": "assess",
  "status": "ok",
  "data": {},
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
| `artifacts` | string[] | Optional file paths touched (informational) |

### PhaseError

```json
{
  "code": "AMBIGUOUS_ACTION",
  "message": "human-readable",
  "details": {}
}
```

Used by input-resolution and orchestrator hard-stops. Agents return `status: failed` with `data.error` matching this shape when execution cannot continue.

## Parsing policy

1. Agent final message must be valid JSON matching `PhaseOutput` for its phase.
2. One retry on parse failure (see [determinism.md](determinism.md)).
3. Second failure → orchestrator hard-stop with `code: AGENT_OUTPUT_PARSE_FAILED`.

---

## Per-agent output contracts (`data` field)

### init-discovery

```json
{
  "stack": { "languages": [], "frameworks": [], "runners": [], "build_tools": [] },
  "conventions": { "test_dirs": [], "naming": "", "patterns": [] },
  "philosophy_inferred": "string",
  "open_questions": [{ "id": "q1", "question": "", "blocking": false }],
  "recommendations": [{ "priority": 1, "text": "" }],
  "claude_md_patch": { "section": "## rr-test Project Testing Context", "body": "" }
}
```

### assess

```json
{
  "verdict": "pass|warn|fail",
  "scopes": [{
    "path": "",
    "verdict": "pass|warn|fail",
    "signals": [{ "kind": "", "severity": "low|medium|high", "evidence": "" }]
  }],
  "counts": { "pass": 0, "warn": 0, "fail": 0, "redundant": 0 },
  "redundant_tests": [{ "path": "", "reason": "" }]
}
```

Verdict rules: [shared-heuristics.md](shared-heuristics.md).

### identify-missing

```json
{
  "items": [{
    "id": "m1",
    "priority": 1,
    "production_path": "",
    "suggested_test_path": "",
    "rationale": "",
    "risk": "low|medium|high"
  }],
  "summary_counts": { "high": 0, "medium": 0, "low": 0 }
}
```

### plan

```json
{
  "maintain": [{ "id": "p1", "action": "", "path": "", "priority": 1, "rationale": "" }],
  "add": [{ "id": "p2", "action": "", "path": "", "priority": 1, "rationale": "" }],
  "constraints_applied": []
}
```

Merge/sort rules: [determinism.md](determinism.md).

### write

```json
{
  "changes": [{ "path": "", "operation": "create|modify", "description": "" }],
  "execution": { "command": "", "exit_code": 0, "passed": true },
  "oracle_check": { "passed": true, "failures": [] },
  "write_mode": "standard|test-data|parameterized"
}
```

Oracle and verify gates: [determinism.md](determinism.md).

### fix

```json
{
  "fixes": [{ "path": "", "description": "", "risk": "low|medium|high" }],
  "rerun": { "command": "", "exit_code": 0, "passed": true },
  "risk_notes": []
}
```

### migrate

```json
{
  "steps_executed": [{ "step": 1, "description": "", "paths": [] }],
  "compatibility_notes": [],
  "rerun": { "command": "", "exit_code": 0, "passed": true }
}
```

### flaky

```json
{
  "likely_root_cause": "",
  "severity": "low|medium|high|critical",
  "stabilization_actions": [{ "action": "", "priority": 1 }],
  "quarantine_advice": { "recommended": false, "reason": "" }
}
```

Severity categories: [shared-heuristics.md](shared-heuristics.md).

### debug

```json
{
  "diagnosis": "red|green|inconclusive",
  "root_cause": "",
  "fix_plan": [{ "step": 1, "action": "" }],
  "evidence": []
}
```

### perf-audit

```json
{
  "hotspots": [{ "path": "", "duration_ms": 0, "share_pct": 0 }],
  "optimization_plan": [{ "priority": 1, "action": "", "expected_gain": "" }],
  "suite_total_ms": 0
}
```
