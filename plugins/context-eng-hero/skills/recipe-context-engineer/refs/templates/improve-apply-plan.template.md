# Improve apply plan (merge output)

Emit after `improve-3-merge` before write gates. One approve covers the whole plan.

```markdown
## Combined apply plan

### Fix lane
| Source | Id | Absorb |
|--------|-----|--------|
| compliance | `{fail_id}` | fix |
| opportunity | `{ranked_id}` | fix |

### Redesign lane
| Source | Id | Absorb |
|--------|-----|--------|
| opportunity | `{ranked_id}` | redesign |

### Dropped
- Keep notes; Absorb `defer`; Deferred table; Impact `low`

### Empty?
- Both lanes empty → skip write; diagnosis-only close (`improve-6-close`)
```

**Rules:** Fix lane = every compliance Findings FAIL id (all severities) ∪ Ranked Absorb `fix` with Impact high|medium. Redesign lane = Ranked Absorb `redesign` with Impact high|medium.
