# <!-- REQUIRED: workflow name -->

## Outcome

<!-- REQUIRED: what changes when this completes -->

## Preconditions

<!-- Inputs, branches -->

## Steps

<!-- REQUIRED: bounded list; each step has todo_id, owner, and output -->

| Step | todo_id | Owner artifact | Output contract |
|------|---------|----------------|-----------------|
| 1 | `workflow-1-…` | … | … |

## Delegation

<!-- REQUIRED: which skill/command/agent handles which step; no “only chain slashes” routing -->

## Exit and failure

<!-- REQUIRED: when to abort; what to report -->

## Orchestration

<!-- REQUIRED (workflow.orchestration.todowrite): TodoWrite (merge: false) with one todo per step using todo_id values before step 1 -->

