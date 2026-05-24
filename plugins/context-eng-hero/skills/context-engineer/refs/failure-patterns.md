# Failure patterns (audit taxonomy)

Use these labels in **audit** narrative findings. Map each failed check **id** (e.g. `skill.scope.single-outcome`, `static.paths.no-parent-segment`) to one or more patterns.

| Pattern | Meaning | Typical check ids |
|---------|---------|-------------------|
| **STRUCTURE** | Frontmatter, naming, or required sections break discovery or parsing | `static.*`, `*.sections.*` |
| **SCOPE** | Responsibility too broad, merges unrelated concerns, or leaks domain | `*.scope.*`, `workflow.steps.bounded` |
| **VAGUE** | Goals, inputs, outputs, or stop rules not operational | `*.procedure.*`, `*.requirements.testable` |
| **REDUNDANT** | Duplicates another artifact without extension or deprecation pointer | (judgment narrative) |
| **DISCOVERY** | `description` too generic; false positives/negatives likely | `*.discovery.*` |
| **CONTRACT** | Missing or ambiguous input/output/stop for invokers | `command.input.*`, `agent.outputs.*` |
| **SAFETY** | Absolute paths, `..`, command-chaining-only routing, or unsafe defaults | `static.paths.*`, `*.routing.no-chain-only` |
| **ORCHESTRATION** | Multi-step flow without TodoWrite/AskQuestion mapping where required | `*.orchestration.*`, `workflow.steps.todo-id` |
| **NOISE** | Long prose with little constraint value; should be ref or deleted | `*.noise.signal-ratio` |
| **FORMAT** | Output shape not pinned; hard to verify success | `command.output.shape`, `agent.outputs.format` |

Group multiple bullets under one pattern when they share a root cause.
