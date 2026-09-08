# Severity triage (shared — Challenge contract)

**Audience:** **rr-review** step 7; any session surfacing blocker-tier findings before merge, fix, or POST.

**Lane bindings:** When challenging, **`Read`** that lane's `refs/severity-triage.md` under **rr-coder**, **rr-tester**, or **rr-security-auditor**.

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

## Challenge appendix schema

```text
## Challenge
| Row | Rule | Disposition | Reason |
|-----|------|-------------|--------|
| 3 | CP004 | drop (FP) | Fail-if mismatch: … |
```

Dispositions: `keep` | `demote→Suggestion` | `drop (FP)` only.

**Appendix location:** next to lane assess artifact under `REVIEW_DIR`.

## Orchestrator duties (step 7)

1. For every lane that produced challengeable rows.
2. **`Read`** this file + lane `refs/severity-triage.md` + [maintenance-hunk-exclusion.md](maintenance-hunk-exclusion.md).
3. Record disposition; persist **Challenge** appendix.
4. **MUST NOT** proceed to merge, fix, or **`--ci`** POST until appendices exist.
5. Downstream uses **`keep` only**.

## Lane index

| Lane | Binding ref |
|------|-------------|
| code | `skills/rr-builder/rr-coder/refs/severity-triage.md` |
| test | `skills/rr-builder/rr-tester/refs/severity-triage.md` |
| security | `skills/rr-builder/rr-security-auditor/refs/severity-triage.md` |
