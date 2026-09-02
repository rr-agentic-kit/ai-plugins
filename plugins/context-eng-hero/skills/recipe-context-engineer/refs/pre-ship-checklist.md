# Pre-ship checklist (binary)

Run after **pre-write reflection** passes and before **write** on **create**, **fix**, **redesign**, **design**, and **extract** (file write). Judgment rubric depth is in `pre-write-reflection.md`—do not re-score rubric ids here.

For each item: **PASS** or **FAIL** with one line of evidence (quote or line ref).

**Stop rule:** any **FAIL** → emit `PRE-SHIP FAILED` and **do not** write the target file.

---

## 1. Schema

| # | Check |
|---|--------|
| 1.1 | Reuse last **STATIC PASS** from shared write gates on same draft hash—all static rows **PASS** (re-run shell only if draft changed after static) |
| 1.2 | Required keys and naming match `frontmatter-schemas.md` (covered by static script; re-check only if script skipped) |
| 1.3 | Skill/command/agent `description` length ≤1024 (static `static.description.max-length` when applicable) |
| 1.4 | `description` ≤160 recommended unless user accepted over-budget this session |

## 2. Discovery

| # | Check |
|---|--------|
| 2.1 | Folder/file naming matches conventions (skill folder = `name`, command stem = `name`, etc.) |
| 2.2 | Skill `description` matches invoke mode (`skill-invocation.md`); no ambient action verbs when `disable-model-invocation: true` |
| 2.3 | Paths in doc are relative; no `..` |
| 2.4 | Skill README (if folder ships): has **Why**, **What**, **When** with `### Use when` and `### Avoid when`; orchestrator README has **Actions** table; no anti-trigger duplication across **What** and **Avoid when**; does not restate **Procedure** (`readme-spec.md`) |

## 3. Contracts

| # | Check |
|---|--------|
| 3.1 | Template-required sections exist or are explicitly marked N/A with reason (`template-required-map.md`) |
| 3.2 | Inputs (what invoker provides) stated where template expects |
| 3.3 | Outputs and stop rules stated where template expects |

## 4. Safety

| # | Check |
|---|--------|
| 4.1 | No command-chaining-only routing as sole procedure for commands/workflows |
| 4.2 | No absolute filesystem paths in authored content |
| 4.3 | No dead internal markdown links to missing plugin files |

## 5. Orchestration

| # | Check |
|---|--------|
| 5.1 | Workflows: every step has `todo_id`; **Orchestration** requires TodoWrite before execution |
| 5.2 | Multi-step commands/skills: **Progress** or procedure maps steps to TodoWrite ids **or** one-line single-shot N/A |
| 5.3 | If N/A claimed: section states why—not empty |

---

## Result format

```text
PRE-SHIP: PASSED | FAILED
Table: (id) PASS|FAIL — evidence
```

If **FAILED**, output the draft in chat only (or as clearly labeled **draft**), not at the final path.
