# Template REQUIRED → rubric id map

Use when replacing `<!-- REQUIRED -->` markers and when quoting evidence in reflection or audit. Static ids come from `scripts/audit_static.py`; judgment ids from the type rubric.

## Skill (`templates/skill.template.md`)

| Marker / section | Rubric id(s) |
|------------------|--------------|
| Title heading | `static.sections.required` |
| **Purpose** | `skill.scope.single-outcome` |
| **When to use** | `skill.discovery.when-clause` (with frontmatter `description`) |
| **When not to use** | `skill.anti-triggers` |
| **Procedure** (imperative steps) | `skill.procedure.stop-points`, `skill.routing.no-chain-only` |
| **Progressive disclosure** | `skill.progressive-disclosure`, `skill.refs.no-body-echo` |
| **Orchestration** | `skill.orchestration.todo-mapping`, `skill.clarify.delivery-channels` (Delivery channels stub or N/A when gates), `workflow.orchestration.todowrite` (if multi-step) |
| Frontmatter `description` | `skill.description.recommended-length`, `skill.description.invoke-fit`, `static.description.*` |
| Invoke flags | `skill.invoke.mode-flags`, `skill.invoke.no-wrong-lever` |

## Skill+Ref

Same as Skill, plus audit `skill-ref.*` / `ref-file.*` rows when editing the pack.

## Ref file (`templates/ref-file.template.md`)

| Marker / section | Rubric id(s) |
|------------------|--------------|
| Title + body constraints | `ref-file.value`, `ref-file.no-base-duplication` |
| Optional owned-by / load-via prose | (authoring aid only — not a static section check) |
| No sole-path peer dependency | `ref-file.no-ref-chain` |

## Command

| Section | Rubric id(s) |
|---------|--------------|
| **Input contract** | `command.input.required` |
| **Execution** (Action delegation) | `command.delegation.action-id`, `command.routing.no-chain-only` |
| **Output** | `command.output.shape` |
| AskQuestion / clarify gates (when present) | `command.clarify.delivery-channels` |
| Frontmatter `argument-hint` | `command.argument-hint.when-args` |

## Agent

| Section | Rubric id(s) |
|---------|--------------|
| **Role** | `agent.role.domain` |
| **Tools and boundaries** | `agent.boundaries.tools`, `agent.fence.body-required`, `agent.fm.tools-align-body` |
| **Stop conditions** | `agent.stop.conditions` |
| **Inputs** | `agent.inputs` |
| **Outputs** | `agent.outputs.format` |
| Frontmatter extras | `agent.fm.no-false-security`, `agent.access.portable-default` |
| `description` | `agent.description.recommended-length`, `agent.description.invoke-fit` |

## Inline executor (`templates/executor.template.md`)

Parent-only `refs/executors/<role>.md`. Reuses agent judgment ids; skip frontmatter-only rows.

| Marker / section | Rubric id(s) |
|------------------|--------------|
| No YAML frontmatter | `inline-executor.no-frontmatter` |
| **Role** | `agent.role.domain` |
| **Tools and boundaries** | `agent.boundaries.tools`, `agent.fence.body-required` |
| **Stop conditions** | `agent.stop.conditions` |
| **Inputs** | `agent.inputs` |
| **Outputs** | `agent.outputs.format`, `agent.outputs.no-template-echo` |
| **Orchestration** | `agent.orchestration.subagents` |

## Rule

| Section | Rubric id(s) |
|---------|--------------|
| **Intent** | `rule.intent.clear` |
| **Requirements** | `rule.requirements.testable` |
| **Scope** | `rule.scope.globs` |
| **Exceptions** | `rule.exceptions.explicit` |

## Workflow

| Section / table column | Rubric id(s) |
|------------------------|--------------|
| **Outcome** | `workflow.outcome.world-change` |
| **Steps** `todo_id` column | `workflow.steps.todo-id`, `static.workflow.todo-id` |
| **Steps** output column | `workflow.steps.output-contract` |
| **Delegation** | `workflow.delegation.owners` |
| **Exit and failure** | `workflow.exit.failure`, `workflow.steps.bounded` |
| **Orchestration** | `workflow.orchestration.todowrite`, `workflow.clarify.delivery-channels` (when AskQuestion/gates present; else N/A) |

## Skill README (`templates/readme.template.md`)

Sibling `skills/<name>/README.md`. Frontmatter optional. Static requires **Why**, **What**, **When** headings; **Actions** when orchestrator (sibling SKILL has Actions table or ≥3 action ids).

| Marker / section | Rubric id(s) |
|------------------|--------------|
| H1 + one sentence | `static.sections.required`, `skill-ref.readme.spec` |
| **Why** | `skill-ref.readme.spec` |
| **What** | `skill-ref.readme.spec` |
| **What → Verification** | `skill-ref.readme.spec` |
| **Actions** (orchestrator) | `static.sections.orchestrator-actions`, `skill-ref.readme.spec` |
| **When → Use when** | `skill-ref.readme.spec` |
| **When → Avoid when** | `skill-ref.readme.spec`, `skill-ref.readme.anti-triggers` |
| **Philosophy** | `skill-ref.readme.philosophy` |
| **UX** (`###` subsections) | `skill-ref.readme.ux` (Clarify/Close include Delivery channels fallback) |
| **Design notes** | `skill-ref.readme.design-notes` |
| **Constraints** | `skill-ref.readme.spec` |
| **Notes** | `skill-ref.readme.spec` |
| No Procedure echo | `SPEC_DEFINITION_DRIFT` (judgment + pre-ship 2.4) |
| No paths above Notes | `skill-ref.readme.spec` |

## ACRONYMS (`templates/acronyms.template.md`)

Plugin root (or skill sibling). Always required; empty table or `None yet` OK.

| Marker / section | Rubric id(s) |
|------------------|--------------|
| H1 + table | `static.acronyms.present`, `static.acronyms.shape`, `skill.acronyms.present` |
| Domain rows / coverage | `skill.acronyms.coverage` (judgment); pre-ship 2.5 |

## GLOSSARY (`templates/glossary.template.md`)

Same placement as ACRONYMS. Always required; empty table or `None yet` OK.

| Marker / section | Rubric id(s) |
|------------------|--------------|
| H1 + table | `static.glossary.present`, `static.glossary.shape`, `skill.glossary.present` |
| Overloaded-term coverage | `skill.glossary.coverage` (judgment); pre-ship 2.6 |
