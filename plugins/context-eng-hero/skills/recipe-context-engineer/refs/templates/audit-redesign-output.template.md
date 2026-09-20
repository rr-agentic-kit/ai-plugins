# Audit-redesign output template

Fill from `rubrics/audit-redesign.rubric.md`. Map patterns via `improvement-patterns.md`. **No** compliance PASS/FAIL verdict; opportunities are ranked after challenge + quality filter, not capped by count.

**Stability:** Field names and section headers are reserved for the **`--improve`** apply pipeline—keep them stable. `rank` is unbounded `1…N`; `impact` is required; do not assume ≤7 ranked rows.

```markdown
# Audit-redesign: <artifact-type> — <file-or-title>

## Target
- Path: `<relative-path>`
- Type: skill | Skill+Ref | ref file | command | agent | rule | workflow

## Compliance blockers (skim only)
- None | <ids from latest compliance audit / static — do not re-score here>
- Note: Unresolved critical/major compliance FAILs should be fixed before absorbing Improve/Restructure work.

## Keep (optional)
- <stance Keep notes — fit shapes worth preserving>

## Challenge
- **FP:** <drops/demotions, or “none”>
- **FN:** <added medium/high with evidence, or “coverage: no additional.” / “scriptable/context-bloat: none”>
- **Stability:** <flips kept at lower band, or “none”>
- **Effect:** <demotions/drops for speculative or taste-only effect, or “none”>
- **Cost:** <demotions where absorb adds load without proportional gain, or “none”>
- **Delta:** <drops or defer for marginal improvement vs status quo, or “none”>

## Ranked opportunities

| Rank | id | Pattern | Stance | Impact | Confidence | Absorb | Summary |
|------|----|---------|--------|--------|------------|--------|---------|
| 1 | `imp.…` | COHESION | Improve \| Restructure | high \| medium | observed \| hypothesized | fix \| redesign \| defer | … |

### Opportunity detail

#### 1. `<id>`
- **Dimension:** `imp.…`
- **Evidence:** `<path>` — <section/quote>
- **Impact:** high | medium
- **Why it matters:** … (detect: waste / invent / context dump — not “missing scripts/”)
- **Suggested direction:** … (improve: point at CLI / index custom helper / filter stdout→value)
- **Absorb hint:** fix | redesign | defer

## Deferred (optional)
| id | Pattern | Impact | Confidence | Reason |
|----|---------|--------|------------|--------|
| `imp.…` | … | medium | hypothesized | <one-line why deferred, not ranked> |

## Recommended next step (user)
- Absorb via **fix** (Improve / absorb:fix) and/or **redesign** (Restructure / absorb:redesign)
- Defer low-ROI items; re-run compliance **audit** if blockers listed above
- Or run **`--improve`**: compliance audit → audit-redesign → apply absorb hints (fix then redesign) under write gates
```

**Filter:** Rank only `impact` ∈ {high, medium} with `confidence` = observed, or high+hypothesized. Drop opportunities without evidence. `medium`+`hypothesized` → Deferred (not ranked). `impact: low` never ranks. Do not invent a single craft FAIL that blocks ship. No numeric ceiling on ranked rows.

## Apply-consumer field contract

Parent **improve** (and manual fix/redesign absorb) reads these fields only:

| Field | Apply rule |
|-------|------------|
| `id` | Stable slug; cite in fix/redesign plans |
| `rank` | Priority among ranked rows; unbounded `1…N` |
| `absorb` | `fix` → fix lane; `redesign` → redesign lane; `defer` → **skip** |
| `impact` | Apply only `high` \| `medium`; **skip** `low` |
| `confidence` | Informational; Deferred (`medium`+`hypothesized`) already excluded from ranked apply |
| Keep / Deferred sections | **Never** auto-apply |
