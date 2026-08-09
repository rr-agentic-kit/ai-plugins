# Gates — exit contract

**Hard stops.** All 6 gates must PASS before `confirm-before-write`. Gate FAIL = do not write; fix or flag explicitly.

Run gates in order. Document PASS/FAIL for each in the session before proceeding.

---

## Gate 1 — Top-third scan

**Test:** Human identifies level + domain + one achievement in ≤6 seconds.

| Check | PASS criteria |
|-------|---------------|
| Positioning line | Present; JD-aligned for tailored; role tags visible |
| Current role | Title, company, dates immediately visible |
| Top bullets | First 2 bullets of current role are **metric bullets** (contain quantified outcome) |
| Scan order | Name → positioning → current role → top 2 bullets → skills (if technical) |

**Psychology rules (distilled):**

- Top-third dominates first impression; front-load level + domain + best metric
- F-pattern scan: strongest content top-left
- Replace "objective" with one-line positioning statement
- Education at bottom for 8+ years experience

**FAIL actions:** Reorder summary; elevate metric bullets to positions 1–2; add positioning line.

---

## Gate 2 — Requirement coverage (T10 gate)

**Test:** Every **required** JD skill traces to a bullet OR skills section (exact term).

| Check | PASS criteria |
|-------|---------------|
| T10 mapping complete | Numbered JD requirements mapped to bullet IDs or skills |
| Required terms | Each required skill appears verbatim in bullet or skills section |
| Gaps flagged | No silent gaps — each unmapped requirement flagged with placement (cover letter, skills, or acknowledged missing) |
| No stuffing | Keyword density natural; terms embedded in achievement context |

**FAIL actions:** Run T11 for evidence bullets from master facts only; add synonym coverage (T13); flag honest gaps for cover letter.

---

## Gate 3 — Metrics integrity

**Test:** Every role (last 10 years) has ≥1 quantified bullet. User confirms all metrics interview-defensible.

| Check | PASS criteria |
|-------|---------------|
| Coverage | Each role in last 10 years has ≥1 bullet with number, %, scale, or $ |
| Defensibility | User explicitly confirmed every metric in pre-write review |
| Ranges OK | `~40%`, `2M+`, `$180K/year` acceptable when exact unknown |
| No fabrication | Zero invented metrics, team sizes, or outcomes |

**FAIL actions:** Ask structured Q&A per role for missing metrics; remove unverified numbers; hard stop on fabrication.

---

## Gate 4 — Parse integrity

**Test:** Resume parses cleanly as plain text; ATS-safe structure.

| Check | PASS criteria |
|-------|---------------|
| Layout | Single column; no tables, sidebars, text boxes, graphics |
| Headers | Standard: Summary, Experience, Skills, Education (Certifications if applicable) |
| Contact | In document body, not header/footer only |
| Skills | Plain text list or categorized text — no bars, icons, graphics |
| Plain-text test | Read without formatting — sections detectable, content readable |
| Length | ~2 pages of content for senior (when exported) |

Load full rules: `reference/ats-formatting.md`

**FAIL actions:** Restructure sections; remove tables/graphics; move contact to body.

---

## Gate 5 — LLM roast (T14)

**Test:** Run T14 prompt. All FAIL items resolved before write.

**Prompt:** See `prompts/tailoring-prompts.md` → T14.

| Check | PASS criteria |
|-------|---------------|
| Parsing risks | None flagged unresolved |
| Evidence gaps | Each flagged gap addressed or honestly flagged |
| Keyword gaps | Resolved via T13 synonym coverage or acknowledged |
| Unnatural density | No keyword stuffing |
| Seniority match | Scope language matches target level |

**FAIL actions:** Fix each T14 FAIL item; re-run T14 until clean or gaps explicitly acknowledged.

---

## Gate 6 — Cover quality (co-equal)

**Applies when:** Writing or reviewing a cover letter (master components or tailored).

| Check | PASS criteria |
|-------|---------------|
| Hook | Metric in line 1 — no "I am writing to apply" |
| Company-specific | ≥1 sentence about company/product/stack |
| Tone | No hedging ("I believe I might...", "perhaps") |
| Length | 250–350 words (tailored) |
| Complement | Does not repeat resume bullets verbatim |
| Confidence | Direct CTA for technical conversation |

**Psychology rules (distilled):**

- Hook = System 1 interrupt (metric first)
- One company-specific sentence fights generic-app detection
- Complement resume; don't duplicate scan-friendly facts

**FAIL actions:** Rewrite hook with metric; add company sentence; cut hedging; dedupe resume bullets.

---

## Gate summary template

Report before write:

```
Gate 1 Top-third scan:        PASS | FAIL — [note]
Gate 2 Requirement coverage: PASS | FAIL — [note]
Gate 3 Metrics integrity:     PASS | FAIL — [note]
Gate 4 Parse integrity:       PASS | FAIL — [note]
Gate 5 LLM roast (T14):       PASS | FAIL — [note]
Gate 6 Cover quality:         PASS | N/A | FAIL — [note]
```

All applicable gates PASS → proceed to `confirm-before-write`.
