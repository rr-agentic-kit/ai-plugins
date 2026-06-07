# Workflow A — Master resume

Build or expand the master resume source of truth. Never sent to employers.

**Input:** Starting state from `disambiguation.md` — `existing` | `raw` | `blank`

**Output:** `~/career/{Name}_Master_Resume.md`

## TodoWrite step ids

```
master-setup
master-expand-roles
master-achievements
master-skills
master-summaries
master-assemble
master-gates
master-write
```

## Steps

### master-setup

1. Confirm `~/career/` exists (create if not)
2. Record starting state branch
3. System contract: never fabricate; ask clarifying questions; non-dramatic language

### Branch: existing

**master-expand-roles**

1. Ingest existing resume; assign bullet IDs per role (R1-B1, R1-B2, …)
2. Per role: run structured Q&A from `questioning.md` — scope, team, tools, scale, metrics, failures
3. Flag roles missing metrics for Gate 3

### Branch: raw

**master-expand-roles**

1. Extract structured fields from raw notes/LinkedIn export (title, company, dates, fragments)
2. Same per-role Q&A as `existing`
3. Build role skeleton before achievement polish

### Branch: blank

**master-expand-roles**

1. Full role-by-role Q&A from most recent backward (10 years minimum)
2. Per role: ownership, team size, tools, scale, metrics, failures overcome
3. Build structure from nothing using `templates/master-resume-template.md`

### master-achievements

Per role (all branches):

1. Convert duties to achievement bullets using `reference/bullet-formulas.md`
2. Default formula: **XYZ**; use TEAL when metric is headline; CAR when constraint defines win
3. Run T9 pattern for unclear duties: conservative / moderate / ambitious versions — user picks
4. Target 4–6 bullets per recent role in master (more than tailored export)
5. Add scope line per role: title, team size, system scale

### master-skills

1. Build categorized skills inventory: Languages, Frameworks, Cloud/Infra, Databases, AI/ML, MLOps, Tools
2. Include only interview-defensible skills
3. Full inventory stays in master (15–20+ items OK in master; tailored export trims)

### master-summaries

1. Write 4 professional summary variants (2–3 sentences each):
   - SWE/Staff
   - AI Engineer
   - ML Engineer
   - Hybrid
2. Non-dramatic tone; include years + flagship metric per variant

### master-assemble

1. Combine into master document per `templates/master-resume-template.md`
2. Header: name + swappable role tags (PRIMARY | SECONDARY | TERTIARY)
3. Contact: email, phone, LinkedIn, GitHub, location
4. Sections: Summary variants, Experience, Skills, Education, Certifications, Projects/OSS (if applicable)

### master-gates

Run `gates.md`:

- Gate 1: positioning + current role + metric bullets in top-third
- Gate 3: metrics per role + user confirmation
- Gate 4: parse integrity (master can be longer than 2 pages; structure must still parse)
- Gates 2, 5, 6: N/A for master (no JD)

### master-write

1. `confirm-before-write` with target path
2. Write `~/career/{Name}_Master_Resume.md`
3. Close: offer tailor workflow or quarterly review reminder
