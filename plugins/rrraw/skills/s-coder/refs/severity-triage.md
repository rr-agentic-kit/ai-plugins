# Code lane — severity triage

**Audience:** s-review code lane assess; Challenge for code lane.

**Shared schema:** `s-review/refs/severity-triage.md`.

**Rubric:** [`compliance-rubric.md`](compliance-rubric.md). Do not invent severities outside that file.

## Challengeable rows

Critical and Warning (`CPNNN` / `CWE-NNN` / `ARNNN`).

| Class | IDs / signals | On uncertainty |
|-------|----------------|----------------|
| **Hard** | **CWE-20**; **CP007** escalate; **CWE-532**; **AR001** boundary cross; **CP032** on new reusable surface; **AR004** when Escalate applies (money/authz/catalog ingress with no cited rate-limit and load-shedding decision) | **MUST NOT** demote alone — `keep` with `uncertain-hard` |
| **Soft** | Prefer/Avoid without Fail-if; cohesion-gray (**CP022**); mild CP\* when Fail-if unclear; **AR002**/**AR003** when boundary doc missing but surface is internal-only; **AR004** Warning (default) | **MUST demote** or drop |

## Precedence (fixed)

1. **Fail-if match** — else no Critical/Warning for that `CPNNN`
2. **Do not flag** — drop
3. **Pass if / Demote** — Suggestion only
4. **Escalate** — after 1–3
5. **Default severity**

## Hard fences

| Fence | Rule |
|-------|------|
| Docs / markdown prose | No CP003/CP004 as Warning |
| CP004 keep-alive | **MUST NOT** for process-lifetime glue when bin owns lifetime |
| CP026 | Cite documented invariant or `Context: searched: …` before Warning |
| AR004 | **Soft** Warning unless Escalate (money/authz/catalog ingress with no cited rate-limit and load-shedding decision). Cited decision per [`architecture.md`](architecture.md) → **Do not flag** — not Challenge-demote-after-the-fact. **MUST NOT** demote on “maybe they meant to” without a cite naming the choice (including explicit none) and why |
| Project-local style | Suggestion unless Escalate applies |
| `.gitignore` maintenance | **Drop** per `s-review/refs/maintenance-hunk-exclusion.md` — security lane owns secret exclusions |
| Unmapped MR-process | **Drop** per `s-review/refs/maintenance-hunk-exclusion.md` — not Suggestion |

## Challenge (orchestrator session)

**When:** Any Critical/Warning before Plan, Gate A, refactor, push Gate, MR WARNING/CRITICAL POST.

**Read:** this ref + cited `CPNNN` rows + `s-review/refs/maintenance-hunk-exclusion.md`. Re-apply Precedence. Persist sidecar **`REVIEW_DIR/code-assess-challenge.md`** (or `code-assess-<chunk>-challenge.md`). Paths: `s-review/refs/artifacts.md`. Drop rules and sweep timing live in the exclusion ref — do not restate them here.

## MR inline publish

Require Challenge sidecar (`{assess-stem}-challenge.md`). POST **keep** rows only with full evidence block. Refuse incomplete WARNING/CRITICAL bodies.

## Metrics (skill fail if violated)

Kept Warning without evidence; Challenge skipped before refactor/POST; CP003/CP004 on docs; CP026 when invariant documented; soft IDs as Warning; hard IDs demoted without Pass-if/Do-not-flag.
