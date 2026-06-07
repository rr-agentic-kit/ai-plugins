# User-global synthesis

## Buckets (after comm + role)

| Bucket | Typical content | Depth on design |
|--------|-----------------|-----------------|
| **Git & commits** | When to commit; message style; no force-push | Adaptive — gap-only AskQuestion |
| **Security** | Secrets, auth, OWASP habits | Adaptive |
| **Environment** | Nix, wrappers, OS-specific commands | Adaptive |
| **Tooling & agents** | Trigger table: phrase/task → skill/agent/MCP + mode | Mandatory interview on design (`tooling-orchestration.md`); cap ~15 rows |
| **Non-goals** | What global memory must not try to control | Adaptive |

Parse the user prompt first; only ask about buckets not already answered.

## Synthesis rules

- One bullet = one testable behavior or constraint.
- Deduplicate against comm/role; do not repeat tone rules in git section.
- §6 triggers must be observable; “read CONTRIBUTING first” belongs in comm (**Context before action**), not §6.
- Mark stale indicators: “Review quarterly” on fast-changing tooling if user wants.
- Line budget: ~100 lines total unless comm/role import split approved.

## Project leak check (review / fix)

Flag in user-global:

- Repo-specific package names, internal URLs, ticket systems
- “In this codebase we use X” → belongs in project `CLAUDE.md`
