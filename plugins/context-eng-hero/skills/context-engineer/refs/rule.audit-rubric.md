# Rule audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`.

## Static (script)

| id | Severity |
|----|----------|
| `static.frontmatter.delimiters` | critical |
| `static.frontmatter.parseable` | critical |
| `static.keys.required` | critical |
| `static.description.present` | critical |
| `static.paths.no-parent-segment` | critical |
| `static.paths.no-absolute` | major |
| `static.sections.required` | critical |
| `static.links.internal-resolve` | major |

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `rule.requirements.testable` | critical | **Requirements** has ≥2 MUST/MUST NOT lines that cite observable code or file patterns |
| `rule.targeting` | critical | Frontmatter or **Scope** states `alwaysApply` and/or valid `globs` / path patterns |
| `rule.routing.no-chain-only` | critical | Rule’s only “how” is not “run these slashes” without enforceable constraints |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `rule.intent.outcome` | major | **Intent** states prevented bad outcome in one paragraph |
| `rule.exceptions` | major | **Exceptions** section exists with bullets or explicit “none” |
| `rule.scope.files` | major | **Scope** matches globs/intent (no scope wider than stated intent) |
| `rule.consistency` | major | Requirements do not contradict **Exceptions** |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `rule.length.justified` | minor | Body ≤150 lines OR each extra section adds a testable constraint |
| `rule.description.enforcement` | minor | `description` states enforceable rule in one line (quote) |
