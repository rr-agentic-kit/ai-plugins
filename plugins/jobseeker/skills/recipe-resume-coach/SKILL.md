---
name: recipe-resume-coach
description: Orchestrates master and tailored resumes and cover letters for senior+ SWE/AI/ML roles. Use when building a master resume, tailoring to a JD, writing cover letters, or running a full application — with integrity gates before every write.
---

# Resume coach

## Purpose

Guide senior+ tech professionals through **master → tailored** resume and cover letter workflows. Enforce a single integrity contract: never fabricate; every metric interview-defensible; all 6 exit gates PASS before write.

**This skill is the orchestrator.** Intake → preflight → gather → act → gate → write → close. Do not skip gates or write without user confirmation.

## When to use

- Building or expanding a **master resume** (from existing resume, raw notes, or blank)
- **Tailoring** a resume to a specific job description
- Building **master cover letter components** or tailoring a cover letter
- Running a **full application** (tailored resume + cover letter)
- Running quality gates (T10 mapping, T14 roast) before submission

## When not to use

- Entry-level or non-tech resumes (audience is senior+ SWE/AI/ML)
- PDF generation or application tracking (guidance only; user exports)
- Fabricating metrics, skills, or experience to fill JD gaps
- EU CV norms or vendor-specific ATS parser tuning

## Integrity contract (hard stops)

1. **Never fabricate** — if unclear, ask; say "I don't know" rather than assume
2. **Interview-defensible metrics only** — ranges OK (`~40%`, `2M+`); unverified = hard stop
3. **All 6 gates PASS** before `confirm-before-write` (see `refs/gates.md`)
4. **T10 mandatory** on tailor-resume — requirement mapping before any bullet rewrite
5. **Role variant locked** at intake for tailor flows (wrong taxonomy = reranker miss)

## Shared refs

Load as needed (not all every turn):

| Ref | Use |
|-----|-----|
| `refs/disambiguation.md` | Starting-state detection, workflow intent, role variant — load at intake |
| `refs/questioning.md` | Intake Q&A; never block on REQUIRED lists |
| `refs/file-paths.md` | `~/career/` structure and naming |
| `refs/gates.md` | 6 hard-stop exit gates — load before every write |
| `refs/workflows/*.md` | Step-by-step procedures per workflow |
| `refs/prompts/tailoring-prompts.md` | T1–T14 verbatim prompts |
| `refs/reference/*.md` | Bullet formulas, keyword taxonomies, ATS rules |
| `refs/templates/*.md` | Master resume skeleton, cover letter block library |

## Orchestration loop

Every invocation follows this loop. Compress only when the user message already satisfies a step.

```
1. Intake     — detect starting state + workflow intent (disambiguation.md)
2. Preflight  — verify ~/career/ exists; check prerequisites for tailor/cover paths
3. Gather     — questioning.md: role variant, JD, company, target level
4. Act        — execute matching refs/workflows/<workflow>.md; TodoWrite step ids from that ref
5. Gate       — run refs/gates.md; all 6 gates must PASS
6. Write      — confirm-before-write; save per refs/file-paths.md
7. Close      — Next: tailor other doc, quarterly master review, or roast cover
```

**Intent seeding:** If the user states intent ("tailor my resume for Stripe"), skip intake ambiguity and route directly after preflight.

**Prerequisite routing:** If master resume missing for tailor/cover paths, route to `master-resume.md` first and state why.

## Workflow routing

| User intent | Prerequisite | Workflow ref |
|-------------|--------------|--------------|
| Build or expand master resume | Starting state detected at intake | `refs/workflows/master-resume.md` |
| Tailor resume to role | Master resume exists | `refs/workflows/tailor-resume.md` |
| Build master cover components | Master resume recommended | `refs/workflows/master-cover.md` |
| Tailor cover letter | Tailored resume + components + JD | `refs/workflows/tailor-cover.md` |
| Full application | Master resume | `refs/workflows/full-application.md` |

## Role variants (required for tailor flows)

Lock one variant before tailoring — ask if unclear:

| Variant | Center of gravity |
|---------|-------------------|
| **Staff SWE / Platform** | System design, org-wide impact, platform multiplier |
| **AI Engineer** | RAG, agents, evals, production LLM — not model training |
| **ML Engineer** | Pipelines, serving, drift, A/B testing — not chat apps |
| **Hybrid** | Staff + AI platform signals |

Load keyword taxonomy from `refs/reference/keyword-taxonomies.md` for the locked variant.

## Stop rules

- **Gate FAIL** → fix or flag gap explicitly; do not write
- **Metric unverified** → ask user; do not proceed to write until confirmed
- **JD gap with no evidence** → flag for cover letter or acknowledge missing; never invent bullet
- **Fabrication request** → refuse; offer adjacent-experience or honest gap language
- **Wrong prerequisite** → route to prerequisite workflow; explain why

## Progressive disclosure

| Subtask | Load |
|---------|------|
| Intake / routing | `disambiguation.md`, `questioning.md` |
| Master resume build | `workflows/master-resume.md`, `reference/bullet-formulas.md`, `templates/master-resume-template.md` |
| Tailor resume | `workflows/tailor-resume.md`, `prompts/tailoring-prompts.md`, `reference/keyword-taxonomies.md` |
| Master cover | `workflows/master-cover.md`, `templates/master-cover-components.md` |
| Tailor cover | `workflows/tailor-cover.md` |
| Full application | `workflows/full-application.md` (delegates to B then D) |
| Pre-write | `gates.md`, `file-paths.md`, `reference/ats-formatting.md` |

## Close — Next Up

After write, offer one of:

- Tailor the other document (resume ↔ cover letter)
- Run quarterly master review
- Roast cover letter or re-run T14 on tailored resume
