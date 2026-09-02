# Skill+Ref audit rubric

Evaluate the **pack** (SKILL.md + `refs/`). Run **Judgment** in audit step 3. **Static** ids from `scripts/audit_static.py` on SKILL.md; ref files audited separately when paths are in scope.

Judgment rows from `rubrics/skill.rubric.md` apply to SKILL.md. Additional rows below apply to the Skill+Ref **architecture**.

## Judgment (Skill+Ref architecture)

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `skill-ref.protocol.load` | critical | SKILL **Progressive disclosure** names which ref loads for which subtask; one hop from SKILL (no ref→ref chains) |
| `skill-ref.protocol.fallback` | critical | SKILL states what to do when no matching ref exists (default behavior or stop) |
| `skill-ref.layer.separation` | critical | Base SKILL holds invariant procedure; refs hold variant/context-specific divergence only |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `skill-ref.base.no-duplication` | major | SKILL body does not repeat constraints documented in co-loaded refs (cite both if FAIL) |
| `skill-ref.refs.standalone` | major | Each ref in `refs/` passes `ref-file.*` standalone checks when read alone |
| `skill-ref.refs.unique` | major | No two refs duplicate the same constraint without unique extension |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `skill-ref.scripts.helper-cli` | minor | If `scripts/` exists: SKILL documents run lines per `helper-cli.md`; script source not pasted in body |
| `skill-ref.readme.spec` | minor | Sibling README has **Why**, **What**, **When** with `### Use when` and `### Avoid when` per `readme-spec.md`; dense sections not verbose prose; paths only in **Notes**; does not restate **Procedure**; exists or defer reason recorded |
| `skill-ref.readme.anti-triggers` | minor | **### Avoid when** under **When** lists mis-invocation cases; not duplicated in **What** out-of-scope |
| `skill-ref.readme.philosophy` | minor | **Philosophy** present when skill has eval-first, gates, or methodology; 3–6 principle bullets, no prose blocks |
| `skill-ref.readme.ux` | minor | **UX** present when skill has clarify loops, gates, or multi-step close; `###` subsections (Invoke, Intake, Clarify, Output, Close) each ≤2 lines |
| `skill-ref.readme.design-notes` | minor | **Design notes** present only when ≥2 non-obvious product tradeoffs exist; no process meta |
