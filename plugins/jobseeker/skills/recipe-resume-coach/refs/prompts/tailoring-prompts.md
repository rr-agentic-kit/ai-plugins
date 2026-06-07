# Tailoring prompts — T1 through T14

Verbatim prompt patterns. Run in the order specified by each workflow. Do not paraphrase the core instruction.

| # | Name | When to run |
|---|------|-------------|
| T1 | JD keyword extract | Start of tailor-resume (analysis) |
| T2 | Gap analysis | After T1 |
| T3 | Full tailor | After T10 (transform) |
| T4 | Industry translation | Optional; cross-industry applications |
| T5 | Seniority calibration | When level mismatch suspected |
| T6 | Culture alignment | When company values provided |
| T7 | Oliver JD adapt | When summary too generic |
| T8 | Skills highlight | During transform |
| T9 | Achievement conversion | Master resume build (per duty) |
| T10 | Requirement mapping | **Mandatory before transform** |
| T11 | Evidence bullets | After T10 gaps identified |
| T12 | Reranker optimization | After transform |
| T13 | Synonym coverage | After transform |
| T14 | ATS+LLM roast | Pre-write gate |

---

## T1 — JD keyword extract

**Source:** Interview Guys P10

```
Analyze this job description and extract: (1) required hard skills, (2) preferred skills, (3) soft skills, (4) key responsibilities, (5) metrics/outcomes they care about, (6) industry terminology and acronyms. Format as a structured list.
```

---

## T2 — Gap analysis

**Source:** Interview Guys P11

```
Compare my resume to this job description. List: (1) skills/terms in JD missing from resume, (2) where each could be incorporated, (3) bullets that could be reworded to mirror JD language, (4) keyword stuffing risks if we add everything.
```

---

## T3 — Full tailor

**Source:** Interview Guys P14 / Teal

```
Tailor my resume for this job description. Reorder bullets so most relevant appear first. Mirror JD terminology naturally. Rewrite summary (3–4 sentences, non-dramatic). Adjust skills to lead with JD priorities. Expand relevant roles; condense irrelevant. Keep to 2 pages.
```

---

## T4 — Industry translation

**Source:** Interview Guys P15

```
Reframe my experience using language common in [target industry]. Keep all facts accurate; only change framing and terminology.
```

---

## T5 — Seniority calibration

**Source:** Interview Guys P16

```
Adjust scope language and bullet framing to match [senior/staff/principal] level expectations in this JD. Emphasize org-wide impact where appropriate.
```

---

## T6 — Culture alignment

**Source:** Interview Guys P17

```
Identify 3–5 bullets that best align with [company]'s stated values: [paste values]. Suggest minor rewording to surface alignment without fabricating.
```

---

## T7 — Oliver JD adapt

**Source:** Oliver

```
Adapt my resume for [title] at [company], emphasizing keywords from this job description: [paste JD].
```

---

## T8 — Skills highlight

**Source:** Teal

```
Showcase the 8 most relevant skills from my resume for this job description. Use exact JD terminology where I have the skill.
```

---

## T9 — Achievement conversion

**Source:** Interview Guys P5

```
Transform this duty into 3 quantified achievement bullets: conservative, moderate, and ambitious versions. Use only facts I provide; ask if metrics are unclear.
```

---

## T10 — Requirement mapping

**Source:** AI-classification

```
Extract numbered requirements from this JD. Map each to a bullet in my resume by ID. List gaps with suggested placement (resume bullet, skills, or cover letter).
```

---

## T11 — Evidence bullets

**Source:** AI-classification

```
For each unmapped JD requirement, suggest a bullet using XYZ format from my master resume facts only. Do not fabricate.
```

---

## T12 — Reranker optimization

**Source:** AI-classification

```
Rewrite my top 4 bullets so an LLM reranker can match: seniority level, domain specificity, and implicit skills in this JD.
```

---

## T13 — Synonym coverage

**Source:** AI-classification

```
Given this JD, list synonym phrases for key skills so semantic retrieval catches vocabulary variation. Show where to embed each in my resume.
```

---

## T14 — ATS+LLM roast

**Source:** AI-classification

```
Roast this resume as an ATS+LLM screening pipeline. Flag: parsing risks, missing evidence for requirements, keyword gaps, unnatural density, seniority mismatches.
```

---

## Fine-tuning follow-ups

**Source:** Oliver

- Summary too generic → `Make summary specific to [industry] and [technologies from JD]`
- Format → `Adjust spacing; move skills section higher`
- Bullets → `Rewrite [role] bullets for quantifiable results and leadership scope`
