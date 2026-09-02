# Workflow audit rubric

Judgment rows only in audit step 3. Static ids (`static.sections.required`, `static.workflow.todo-id`, …) from `scripts/audit_static.py`.

## Judgment

### Critical

| id | Severity | PASS when |
|----|----------|-----------|
| `workflow.steps.bounded` | critical | **Steps** table has finite rows; any loop cites explicit exit in **Exit and failure** |
| `workflow.steps.todo-id` | critical | Every **Steps** row has non-empty `todo_id` column; ids are unique kebab strings (also `static.workflow.todo-id`) |
| `workflow.orchestration.todowrite` | critical | **Orchestration** requires TodoWrite one todo per `todo_id` before step 1; branching uses AskQuestion first |
| `workflow.delegation.owners` | critical | **Delegation** maps each step to an owning artifact type (skill/command/agent) |

### Major

| id | Severity | PASS when |
|----|----------|-----------|
| `workflow.outcome.world-change` | major | **Outcome** states observable world-change when complete (quote) |
| `workflow.steps.output-contract` | major | Each step row has non-empty **Output contract** cell |
| `workflow.exit.failure` | major | **Exit and failure** lists abort triggers and what to report |
| `workflow.routing.no-chain-only` | major | Workflow is not only a list of slashes without per-step owned work |

### Minor

| id | Severity | PASS when |
|----|----------|-----------|
| `workflow.preconditions` | minor | **Preconditions** lists inputs/branches or states “none” |
| `workflow.consistency` | minor | **Delegation** owners match **Steps** owners |
| `workflow.refs.load-efficiency` | minor | Files in this artifact's **Load** list do not duplicate each other's content; no ref is a strict subset of another co-loaded ref |
