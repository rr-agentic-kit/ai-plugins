# Security lane — severity triage

**Audience:** s-review security lane assess; Challenge for security lane.

**Shared schema:** `s-review/refs/severity-triage.md`.

**Rubric:** OWASP refs + [`confidence.md`](confidence.md).

## Challengeable rows

Critical and High table rows.

| Class | Signals | On uncertainty |
|-------|---------|----------------|
| **Hard** | Critical/High with **HIGH** confidence | **MUST NOT** demote alone |
| **Soft** | **MEDIUM** ("Needs verification") | Do not elevate to Critical; **LOW** → do not report |

## Challenge (orchestrator session)

**When:** Critical or High rows before merge, **`--ci`** POST, or final assess.

**Read:** this ref + OWASP/confidence criteria. Persist sidecar **`REVIEW_DIR/security-audit-challenge.md`** (or `security-audit-<chunk>-challenge.md`). Paths: `s-review/refs/artifacts.md`.

**`--ci`** POSTs Critical/High **keep** only.
