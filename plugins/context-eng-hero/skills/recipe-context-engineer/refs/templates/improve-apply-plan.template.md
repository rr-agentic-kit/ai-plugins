# Improve apply plan (merge output)

Emit after `improve-3-merge`. Persist as `.ai/learning/ce-improve/<run-id>/apply-plan.md`. Present **link + tables** in chat — not full audit dumps. **approve-apply-plan** must run before any target-path mutation. Write-gate Approve later still required before promoting draft → target.

```markdown
## Combined apply plan

### Reports (required)
- Compliance: `.ai/learning/ce-improve/<run-id>/compliance.md`
- Opportunity: `.ai/learning/ce-improve/<run-id>/opportunity.md`
- This plan: `.ai/learning/ce-improve/<run-id>/apply-plan.md`

### Fix lane
| Source | Id | Absorb | Intent (≤1 line) |
|--------|-----|--------|------------------|
| compliance | `{fail_id}` | fix | `{what changes}` |
| opportunity | `{ranked_id}` | fix | `{what changes}` |

### Redesign lane
| Source | Id | Absorb | Intent (≤1 line) |
|--------|-----|--------|------------------|
| opportunity | `{ranked_id}` | redesign | `{what changes}` |

### Dropped
- Keep notes; Absorb `defer`; Deferred table; Impact `low`

### Empty?
- Both lanes empty → skip write; diagnosis-only close (`improve-6-close`)
```

**Rules:** Fix lane = every compliance Findings FAIL id (all severities) ∪ Ranked Absorb `fix` with Impact high|medium. Redesign lane = Ranked Absorb `redesign` with Impact high|medium. **Reports** block is mandatory before **approve-apply-plan** / **approve-revise-abort** — missing links → do not AskQuestion; fix the packet first.
