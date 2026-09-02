# Ref file audit rubric

For standalone `refs/*.md` (or `references/*.md`) under a skill folder. Evaluate **Judgment** in audit step 3.

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `ref-file.purpose.standalone` | critical | **Purpose** is one falsifiable sentence; reader knows what this ref adds without opening parent SKILL |
| `ref-file.standalone.value` | critical | Body adds constraints or examples not inferable from parent SKILL alone |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `ref-file.no-base-duplication` | major | Does not restate parent SKILL **Procedure** or **Purpose** (cite both if FAIL) |
| `ref-file.load.path` | major | **Load** section states parent skill path and which parent step Read this file |
| `ref-file.no-ref-chain` | major | File does not link to other refs for required context (one hop from parent SKILL only) |
| `ref-file.layer.boundary` | major | No content that belongs in parent SKILL (invariant procedure, classify tables, orchestration loop) |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `ref-file.noise.signal-ratio` | minor | No generic encouragement without testable constraint |
| `ref-file.length.proportional` | minor | Length matches scope; no essay without unique constraints |
