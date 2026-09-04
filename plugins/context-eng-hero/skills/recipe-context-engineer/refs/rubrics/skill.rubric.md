# Skill audit rubric

Map judgment FAILs to labels in `failure-patterns.md` for narrative. Evaluate **Judgment** only in audit step 3. **Static** ids are produced by `scripts/audit_static.py`—do not re-score manually unless script skipped.

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
| `skill.invoke.mode-flags` | major | Invoke mode (Auto / Self / Background) matches `disable-model-invocation` and `user-invocable` per `skill-invocation.md` |
| `skill.invoke.no-wrong-lever` | major | Internal/action-like skills do not use `user-invocable: false` **alone**; self-invoke skills have `disable-model-invocation: true` when ambient block intended |
| `skill.description.invoke-fit` | major | `description` shape matches invoke mode (trigger keywords vs outcome-first); no ambient action verbs on self-invoke |
| `skill.description.recommended-length` | major | `description` ≤160 characters one sentence, or user explicitly accepted over-budget in this session |
| `skill.anti-triggers` | major | **When not to use** section exists with ≥1 bullet, or one line cites why N/A applies to this skill |
| `skill.progressive-disclosure` | major | Body ≤~200 lines OR SKILL has **Progressive disclosure** *or* **Shared refs** *or* **Ref index** naming which ref for which step/action; one hop from that table (critical routing verdict lives on `skill-ref.protocol.load` for Skill+Ref packs — do not dual-count narrative) |
| `skill.consistency` | major | No contradictory MUST/MUST NOT between **Purpose**, **When to use**, and **Procedure** (cite both sides if FAIL) |
| `skill.refs.no-body-echo` | major | Skill body does not restate constraints from refs it loads via Action **Run:** or progressive disclosure (cite both sides if FAIL) |
| `skill.refs.unique-contribution` | major | Each ref named in progressive disclosure or Action **Load** adds at least one constraint not present in the skill body or other co-loaded refs for the same action |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `skill.noise.signal-ratio` | minor | No paragraph is generic encouragement only (“be helpful”, “best practices”) without a testable constraint |
| `skill.orchestration.todo-mapping` | minor | Multi-step **Procedure** tells author to use TodoWrite for verifiable steps, or states single-shot N/A in one line |
| `skill.refs.load-efficiency` | minor | Files in this artifact's **Load** list do not duplicate each other's content; no ref is a strict subset of another co-loaded ref |
