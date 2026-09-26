# Severity triage (shared — Challenge contract)

**Audience:** **s-review** step 7; any session surfacing blocker-tier findings before merge, fix, or POST.

**Lane bindings:** When challenging, **`Read`** that lane's `refs/severity-triage.md` under **s-coder**, **s-tester**, or **s-security**.

**Consumers use `keep` dispositions only.** Unchallenged challengeable rows → **Stopped:** `unchallenged report`.

## Shared evidence block

Before adding any **challengeable** row:

```text
Fail-if: "<one-line quote from rubric or lane equivalent>"
Match: yes
Pass-if/Demote/Do-not-flag: none | "<bullet that almost matched and why it does not>"
Snippet: "<one-line code quote>"
Context: <docs path | peer pattern | caller | searched: path1, path2, …>
```

**Refuse to emit** blocker-tier rows if `Fail-if` is missing, `Match` is not `yes`, `Snippet` is missing, or `Context` is empty.

## Challenge sidecar schema

```text
## Challenge
| Row | Rule | Disposition | Reason |
|-----|------|-------------|--------|
| 3 | CP004 | drop (FP) | Fail-if mismatch: … |
```

Dispositions: `keep` | `demote→Suggestion` | `drop (FP)` only.

**Location:** `REVIEW_DIR/{assess-stem}-challenge.md` — locked sidecar in the same run dir (e.g. `code-assess-challenge.md`, multi-chunk `code-assess-<chunk>-challenge.md`). Paths: [artifacts.md](artifacts.md).

## Orchestrator duties (step 7)

1. For every lane that produced challengeable rows.
2. **`Read`** this file + lane `refs/severity-triage.md` + [maintenance-hunk-exclusion.md](maintenance-hunk-exclusion.md).
3. Record disposition; persist **`{assess-stem}-challenge.md`**.
4. **MUST NOT** proceed to merge, fix, or **`--ci`** POST until sidecars exist.
5. Downstream uses **`keep` only**.

## Lane index

| Lane | Binding ref |
|------|-------------|
| code | `skills/s-coder/refs/severity-triage.md` |
| test | `skills/s-tester/refs/severity-triage.md` |
| security | `skills/s-security/refs/severity-triage.md` |
