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

**Orchestrator hard-stop:** if any phase returns `data.enumeration_complete === false`, stop chain immediately with `exit_reason: enumeration_incomplete` and `final_status: failed` — do not invoke subsequent phases or start next epoch.

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
  "enumeration_complete": true,
  "scope_manifest": {
    "production_files": [],
    "test_files": [],
    "unassessed": []
  },
  "verdict": "pass|warn|fail",
  "scopes": [{
    "path": "",
    "verdict": "pass|warn|fail",
    "signals": [{
      "kind": "weak_assertion|over_assertion|redundancy|maintainability|multi_behavior|implementation_coupling|mock_boundary|over_mock_verify|boundary_leak|flakiness_risk|missing_coverage|ai_artifact|mutation_gap|missing_test",
      "severity": "low|medium|high",
      "evidence": "",
      "smell_id": ""
    }]
  }],
  "counts": { "pass": 0, "warn": 0, "fail": 0, "redundant": 0, "overtest": 0 },
  "redundant_tests": [{ "path": "", "reason": "" }],
  "overtest_tests": [{ "path": "", "reason": "", "calibration": "over", "smell_id": "" }]
}
```

| Field | Notes |
|-------|-------|
| `enumeration_complete` | `true` only when `scope_manifest.unassessed` is empty |
| `scope_manifest` | Every production and test file in normalized scope; `unassessed` lists paths not scored |
| `signals[].kind` | Standard enum — [shared-heuristics.md](shared-heuristics.md) § Signal kind enum |
| `signals[].smell_id` | Optional testsmells.org id (e.g. `SensitiveEquality`) |
| `overtest_tests[]` | Over-assertion / implementation-coupling cases per shared-heuristics § Overtest signals |
| `counts.overtest` | Length of `overtest_tests[]` (denormalized for adapters) |

Verdict rules: bidirectional calibration scoring in [shared-heuristics.md](shared-heuristics.md). Scope `fail` when critical path has `missing_test` or `ai_artifact` high; scope `warn` when overtest or weak assertion dominates without critical gaps.

`status: partial` when `scope_manifest.unassessed.length > 0` (sets `enumeration_complete: false`).

### identify-missing

```json
{
  "enumeration_complete": true,
  "items": [{
    "id": "m1",
    "priority": 1,
    "production_path": "",
    "suggested_test_path": "",
    "rationale": "",
    "risk": "low|medium|high"
  }],
  "summary_counts": { "high": 0, "medium": 0, "low": 0 },
  "uncovered_production_paths": []
}
```

| Field | Notes |
|-------|-------|
| `enumeration_complete` | `true` only when `uncovered_production_paths` is empty |
| `uncovered_production_paths` | Production paths from assess `scope_manifest` without adequate coverage and without matching `items[]` entry |

### plan

```json
{
  "maintain": [{ "id": "p1", "action": "", "path": "", "priority": 1, "rationale": "" }],
  "add": [{ "id": "p2", "action": "", "path": "", "priority": 1, "rationale": "" }],
  "constraints_applied": [],
  "steps_total": 0,
  "maintain_before_add": true
}
```

| Field | Notes |
|-------|-------|
| `steps_total` | `maintain.length + add.length` |
| `maintain_before_add` | Required `true` in complete-missing chains; write blocks `add` until maintain queue cleared or `wontfix` |

Merge/sort rules: [determinism.md](determinism.md).

### write

```json
{
  "changes": [{ "path": "", "operation": "create|modify", "description": "" }],
  "steps_completed": [{ "plan_id": "p1", "track": "maintain|add" }],
  "steps_skipped": [{ "plan_id": "p2", "track": "maintain|add", "reason": "" }],
  "execution": { "command": "", "exit_code": 0, "passed": true },
  "oracle_check": { "passed": true, "failures": [] },
  "validation_pipeline": {
    "compile": { "passed": true },
    "run": { "passed": true },
    "oracle": { "passed": true },
    "mutation_spot_check": { "passed": null, "skipped": true, "note": "" }
  },
  "write_mode": "standard|test-data|parameterized"
}
```

| Field | Notes |
|-------|-------|
| `steps_completed` | Plan steps executed this epoch, in execution order |
| `steps_skipped` | Plan steps not executed; if any skip lacks `wontfix` in plan constraints → `status: partial` |

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
