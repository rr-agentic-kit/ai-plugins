# Security lane — severity triage

**Audience:** rr-review security lane assess; Challenge for security lane.

**Shared schema:** [`skills/rr-builder/rr-review/refs/severity-triage.md`](../../rr-review/refs/severity-triage.md).

**Rubric:** OWASP refs + [`confidence.md`](confidence.md).

## Challengeable rows

Critical and High table rows.

| Class | Signals | On uncertainty |
|-------|---------|----------------|
| **Hard** | Critical/High with **HIGH** confidence | **MUST NOT** demote alone |
| **Soft** | **MEDIUM** ("Needs verification") | Do not elevate to Critical; **LOW** → do not report |

## Challenge (orchestrator session)

**When:** Critical or High rows before merge, **`--ci`** POST, or final assess.

**Read:** this ref + OWASP/confidence criteria. Persist appendix under **`REVIEW_DIR/security/`**.

**`--ci`** POSTs Critical/High **keep** only.
