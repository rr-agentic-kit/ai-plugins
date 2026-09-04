# Ref file audit rubric

For skill-private `refs/*.md` (or `references/*.md`) under a skill folder. Refs are **not** entry points — the parent SKILL (or an action Ref index) names when to Read them. Evaluate **Judgment** in audit step 3.

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `ref-file.value` | critical | Body adds constraints or examples not inferable from parent SKILL alone |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `ref-file.no-base-duplication` | major | Does not restate parent SKILL **Procedure** or **Purpose** (cite both if FAIL) |
| `ref-file.no-ref-chain` | major | FAIL only when the file **requires** another ref as the sole way to get a constraint **and** that peer is not co-named by the parent SKILL / action Ref index. Sibling links for navigation or cross-cite PASS |
| `ref-file.layer.boundary` | major | No content that belongs in parent SKILL (invariant procedure, classify tables, orchestration loop) |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `ref-file.noise.signal-ratio` | minor | No generic encouragement without testable constraint |
| `ref-file.length.proportional` | minor | Length matches scope; no essay without unique constraints |
