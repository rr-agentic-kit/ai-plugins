---
name: your-skill-id
description: One sentence ≤160. Auto-invoke: third-person WHAT + WHEN + trigger keywords. Self-invoke: outcome only—no audit/fix verbs.
# disable-model-invocation: true   # Self-invoke / slash-or-parent (uncomment when chosen)
# user-invocable: false              # Claude Code: hide / menu (optional; never sole control)
# allowed-tools: Bash(python3 scripts/audit_static.py*)  # Claude turn grant only when needed
---

# <!-- REQUIRED (static.sections.required): skill title -->

## Purpose

<!-- REQUIRED (skill.scope.single-outcome): one paragraph -->

## When to use

<!-- REQUIRED (skill.discovery.when-clause): bullets -->

## When not to use

<!-- REQUIRED (skill.anti-triggers): anti-triggers -->

## Procedure

<!-- REQUIRED (skill.procedure.stop-points): imperative steps; link refs with skill-relative paths -->

## Progressive disclosure

<!-- OPTIONAL (skill.progressive-disclosure): which refs load for which subtasks — one hop from this file -->

<!-- Skill+Ref: link variant refs here; ref files use templates/ref-file.template.md -->

<!-- If scripts/ exists: document run lines per helper-cli.md; do not paste script source here -->

## Orchestration

<!-- REQUIRED when clarify/close uses AskQuestion or enumerable gates (skill.clarify.delivery-channels): Prefer AskQuestion; mandatory text-mode same options — questioning.md Delivery channels. If no gates: one-line N/A (“no AskQuestion gates”). -->
<!-- OPTIONAL (skill.orchestration.todo-mapping): AskQuestion/Todo/Task per chat-orchestration.md -->
