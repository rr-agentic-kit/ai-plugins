# Workflow B — Tailor resume

JD-aligned subset from master. **T10 is mandatory before any bullet rewrite.**

**Prerequisite:** Master resume exists

**Input:** Master resume + full JD + locked role variant

**Output:** `~/career/applications/{Company}_{RoleFocus}_{Date}/{Name}_Resume_{RoleFocus}_{Company}_{Date}.md`

## TodoWrite step ids

```
tailor-context
tailor-t1-t2
tailor-t10
tailor-transform
tailor-optimize
tailor-gates
tailor-write
```

## Steps

### tailor-context

1. Paste master resume + full JD in session
2. Lock role variant (see `disambiguation.md`)
3. Load keyword taxonomy for variant from `reference/keyword-taxonomies.md`
4. Confirm ≥70–80% qualified (warn if not)

### tailor-t1-t2

Run prompts from `prompts/tailoring-prompts.md`:

1. **T1** — JD keyword extract (required skills, preferred, soft, responsibilities, metrics language, acronyms)
2. **T2** — Gap analysis (missing terms, incorporation points, reword candidates, stuffing risks)

### tailor-t10 (MANDATORY — do not skip)

**T10** — Requirement mapping:

1. Extract numbered requirements from JD
2. Map each to master resume bullet ID
3. List gaps with suggested placement (resume bullet, skills, or cover letter)
4. Save mapping artifact to application folder as `t10-mapping.md` (optional but recommended)

**Hard stop:** Do not proceed to transform until T10 mapping is complete and gaps are visible.

### tailor-transform

Run in order:

1. **T3** — Full tailor: reorder bullets, mirror JD terms, rewrite summary (3–4 sentences), adjust skills, 2 pages
2. **T7** — Oliver JD adapt if summary too generic
3. **T8** — Skills highlight: 8 most relevant skills with exact JD terminology
4. Reorder bullets: JD-relevant × metric strength first
5. Classify and apply role variant keyword priorities

### tailor-optimize

1. **T12** — Reranker optimization: rewrite top 4 bullets for seniority, domain, implicit skills
2. **T13** — Synonym coverage for core stack (JD term + common alternate)
3. Condense older roles; expand relevant roles

### tailor-gates

Run all applicable gates from `gates.md`:

- Gate 1: top-third scan
- Gate 2: T10 requirement coverage
- Gate 3: metrics integrity + user confirmation
- Gate 4: parse integrity
- Gate 5: T14 LLM roast — resolve all FAILs
- Gate 6: N/A

### tailor-write

1. Gate summary all PASS
2. `confirm-before-write`
3. Write tailored resume to application folder
4. Close: offer tailor cover or T14 re-run
