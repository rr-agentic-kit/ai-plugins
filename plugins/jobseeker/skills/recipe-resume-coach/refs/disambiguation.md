# Disambiguation

Load at intake. Detect starting state, workflow intent, and role variant before routing.

## Starting state detection

Ask or infer from user message and attached files:

| State | Signals | Route |
|-------|---------|-------|
| **Existing resume** | User pastes or points to a formatted resume file | `master-resume.md` → branch `existing` |
| **Raw notes** | LinkedIn export, bullet fragments, project notes, no resume structure | `master-resume.md` → branch `raw` |
| **Blank** | No career artifacts; user wants to build from scratch | `master-resume.md` → branch `blank` |

**Detection order:**

1. User explicitly states state → use it
2. File in `~/career/` matching `*_Master_Resume.md` exists → likely has master; check intent
3. User pastes structured resume content → `existing`
4. User pastes unstructured career text → `raw`
5. None of the above → `blank`

If ambiguous between existing and raw, one AskQuestion: "Do you have a formatted resume to expand, or raw notes to structure first?"

## Workflow intent detection

| Intent signals | Workflow |
|----------------|----------|
| "master resume", "build resume", "expand resume", "career file" | `master-resume.md` |
| "tailor resume", "adapt for", JD pasted with resume context | `tailor-resume.md` |
| "cover letter components", "master cover", "cover blocks" | `master-cover.md` |
| "tailor cover", "write cover letter for" | `tailor-cover.md` |
| "full application", "apply to", both resume + cover | `full-application.md` |

If multiple intents, prefer the prerequisite path first (master before tailor).

## Role variant classification

**Required before tailor-resume and tailor-cover.** Lock one variant; do not proceed without it.

| Variant | When to use | JD signals |
|---------|-------------|------------|
| **staff-swe** | Platform, system design, staff/principal SWE | Microservices, API design, technical leadership, SLOs |
| **ai-engineer** | Production LLM, RAG, agents | RAG, LLM, prompt engineering, evals, LangChain |
| **ml-engineer** | Model serving, MLOps, pipelines | PyTorch, feature stores, drift, A/B testing, Kubeflow |
| **hybrid** | Staff + AI platform, AI infra | LLM platform, inference cost, multi-team enablement |

**Rules:**

- AI Engineer ≠ ML Engineer — center of gravity must match JD
- Hybrid only when JD explicitly spans platform + production AI
- If JD is ambiguous, AskQuestion with the four variants above
- Record locked variant in session; reference `reference/keyword-taxonomies.md` for that variant

## Prerequisite checks

| Target workflow | Requires |
|-----------------|----------|
| `tailor-resume.md` | `~/career/{Name}_Master_Resume.md` (or user-provided master) |
| `master-cover.md` | Master resume (recommended; can build in parallel if resume in progress) |
| `tailor-cover.md` | Tailored resume + `*_Master_CoverLetter_Components.md` + JD |
| `full-application.md` | Master resume + JD |

Missing prerequisite → route to prerequisite workflow; state what's missing and why.

## Default assumptions

- Audience: senior+ (8+ years) tech
- Output language: English
- Career directory: `~/career/` (create if missing during preflight)
- Tailored resume length: 2 pages
- Cover letter length: 250–350 words
- Non-dramatic tone unless user requests otherwise
