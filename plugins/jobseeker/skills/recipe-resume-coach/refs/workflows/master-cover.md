# Workflow C — Master cover letter components

Build reusable cover letter block library. Never sent to employers as-is.

**Prerequisite:** Master resume recommended

**Input:** Master resume

**Output:** `~/career/{Name}_Master_CoverLetter_Components.md`

## TodoWrite step ids

```
cover-flagships
cover-hooks
cover-threads
cover-closes
cover-assemble
cover-gates
cover-write
```

## Steps

### cover-flagships

1. From master resume, identify top 3 flagship achievements (with metrics)
2. For each: write 2-sentence proof paragraph
3. User confirms achievements are accurate

### cover-hooks

Write 3 opening hooks (one line each):

1. SWE/platform — metric-led
2. AI production — metric-led
3. ML serving — metric-led

**Rules:** Lead with metric; never "I am writing to apply"

### cover-threads

1. Identify 2–3 narrative threads (e.g., platform multiplier, AI production, incident leadership)
2. Draft one paragraph per thread (4–6 sentences)
3. Non-dramatic tone

### cover-closes

Write 2 closing variants:

1. Direct CTA for technical conversation
2. Architecture/trade-offs walkthrough offer

### cover-assemble

Structure per `templates/master-cover-components.md`:

- Header block (match resume contact)
- Hook variants
- Proof paragraphs
- Narrative threads
- Motivation templates (placeholder for company-specific)
- Close variants

### cover-gates

- Gate 6: hooks metric-led; no hedging; no "I am writing to apply"
- Gate 3: metrics in proof paragraphs confirmed by user
- Gates 1, 2, 4, 5: N/A (no JD yet)

### cover-write

1. `confirm-before-write`
2. Write `~/career/{Name}_Master_CoverLetter_Components.md`
3. Close: offer tailor cover when JD available
