# Workflow D — Tailor cover letter

JD + company-specific cover letter from components.

**Prerequisite:** Tailored resume + master cover components + JD

**Input:** Tailored resume, JD, master cover components, company name

**Output:** `~/career/applications/{Company}_{RoleFocus}_{Date}/{Name}_CoverLetter_{Company}_{Date}.md`

## TodoWrite step ids

```
cover-input
cover-compose
cover-gaps
cover-gates
cover-write
```

## Steps

### cover-input

1. Load tailored resume (not full master), JD, master cover components
2. Confirm company name and hiring manager if known
3. Review T10 gap list — gaps may need honest cover letter treatment

### cover-compose

1. Select hook matching JD theme from master components
2. Compose proof paragraph tying flagship achievement → JD stated problem
3. Add **one company-specific sentence** (product, eng blog, stack, initiative)
4. Mirror JD keywords in natural sentences
5. Target 250–350 words; non-dramatic tone

**Teal tailor pattern:**

> Using non-dramatic language, write a [length]-word cover letter using my resume and the job description. Focus on skills relevant to the job.

### cover-gaps

If T10 flagged gaps:

1. Address missing skill honestly — adjacent experience + learning path
2. No fabrication
3. One sentence per gap maximum

### cover-gates

Run from `gates.md`:

- Gate 6: cover quality (all checks)
- Gate 2: if JD requirement only addressable in cover, confirm it's addressed
- Gate 3: any metrics in cover confirmed by user

### cover-write

1. All gates PASS
2. `confirm-before-write`
3. Write to application folder
4. Close: offer full-application review or PDF export guidance
