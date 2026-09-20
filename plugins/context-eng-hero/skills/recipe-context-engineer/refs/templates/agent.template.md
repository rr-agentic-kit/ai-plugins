---
name: your-agent-id
description: Role and when to use in one sentence ≤160. No delegation chains or _oa-* IDs here.
# --- Optional Cursor ---
# model: inherit
# readonly: true
# is_background: false
# --- Optional Claude (omit permissionMode/hooks/mcpServers in plugin agents — ignored) ---
# model: sonnet
# tools: Read, Grep
# disallowedTools: Write, Edit
# maxTurns: 20
# background: false
---

# <!-- REQUIRED: agent title -->

## Role

<!-- REQUIRED (agent.role.domain): function-style Task executor by default; domain boundary ≤3 sentences -->

## Tools and boundaries

<!-- REQUIRED (agent.boundaries.tools): portable body fence — MUST / MUST NOT; do not rely on frontmatter tools alone -->

## Stop conditions

<!-- REQUIRED (agent.stop.conditions): ≥2 concrete stop triggers -->

## Inputs

<!-- REQUIRED (agent.inputs): what invoker provides. Caller Load — list stable skill/plugin ref paths; require parent inject for variant refs (type rubric, method). Prefer refs SoT over pasting judgment into this body. See design/design-core.md Shared knowledge layout. -->

## Outputs

<!-- REQUIRED (agent.outputs.format): link the report/output template path; prefer markdown. Do not paste template sections or invent parallel JSON unless a field truly cannot live in the template (Ranked/Findings tables already carry apply fields). -->

## Orchestration

<!-- OPTIONAL (agent.orchestration.subagents): Task delegation, subagent type hints; N/A for single-shot -->
