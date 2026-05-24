# Skill audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`—list for traceability; do not re-score manually unless script skipped.

## Static (script)

| id | Severity |
|----|----------|
| `static.frontmatter.delimiters` | critical |
| `static.frontmatter.parseable` | critical |
| `static.keys.required` | critical |
| `static.name.format` | critical |
| `static.name.path-match` | critical |
| `static.description.present` | critical |
| `static.description.max-length` | major |
| `static.paths.no-parent-segment` | critical |
| `static.paths.no-absolute` | major |
| `static.sections.required` | critical |
| `static.links.internal-resolve` | major |
| `static.links.https-only` | critical |

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `skill.scope.single-outcome` | critical | **Purpose** names one primary outcome; **Procedure** does not introduce a second unrelated outcome (cite section headings) |
| `skill.procedure.stop-points` | critical | **Procedure** uses imperative steps; each step ends with an observable done condition or explicit stop (quote at least one) |
| `skill.routing.no-chain-only` | critical | **Procedure** does not state that running other plugin slashes in sequence is the only execution path (cite lines or PASS if absent) |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `skill.discovery.when-clause` | major | `description` states WHAT the skill does and WHEN to use it (third person); quote the clause |
| `skill.anti-triggers` | major | **When not to use** section exists with ≥1 bullet, or one line cites why N/A applies to this skill |
| `skill.progressive-disclosure` | major | Body ≤~200 lines OR **Progressive disclosure** / refs name which `refs/` files load for which subtasks |
| `skill.consistency` | major | No contradictory MUST/MUST NOT between **Purpose**, **When to use**, and **Procedure** (cite both sides if FAIL) |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `skill.noise.signal-ratio` | minor | No paragraph is generic encouragement only (“be helpful”, “best practices”) without a testable constraint |
| `skill.orchestration.todo-mapping` | minor | Multi-step **Procedure** tells author to use TodoWrite for verifiable steps, or states single-shot N/A in one line |
