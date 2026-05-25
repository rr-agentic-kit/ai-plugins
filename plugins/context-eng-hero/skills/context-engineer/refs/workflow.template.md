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

<!-- REQUIRED: when this workflow runs, executor calls TodoWrite (merge: false) with one todo per step using todo_id values before step 1; mark completed before advancing. Branching: AskQuestion first, then spawn branch-specific todos. -->

## Validity

Validate against `frontmatter-schemas.md`; before ship run static → `pre-write-reflection.md` → `pre-ship-checklist.md` (see `shared-write-gates.md` in **context-engineer** refs).
