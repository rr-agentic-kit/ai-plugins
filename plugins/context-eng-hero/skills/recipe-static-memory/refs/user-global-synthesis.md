# User-global synthesis

Shared SoT = `~/.agents/AGENTS.md`. Harness overlays = `~/.agents/{HARNESS}.specific.md`. Layout: `user-global-multi-harness.md`.

## Buckets (after comm + role)

| Bucket | Typical content | Depth on design | Home |
|--------|-----------------|-----------------|------|
| **Git & commits** | When to commit; message style; no force-push | Adaptive — gap-only AskQuestion | Shared SoT |
| **Security** | Secrets, auth, OWASP habits | Adaptive | Shared SoT |
| **Environment** | Nix, wrappers, OS-specific commands | Adaptive | Shared SoT |
| **Tooling & agents** | Trigger table: phrase/task → skill/agent/MCP + mode | Mandatory interview on design (`tooling-orchestration.md`); cap ~15 rows | Shared SoT for cross-harness; model/sub-agent/harness-native → overlay |
| **Harness overlays** | Default models; Task/subagent spawn; harness MCP/skill quirks; runtime mode prefs | After tooling group C when `scope=user`; only for selected harnesses | `*.specific.md` |
| **Non-goals** | What global memory must not try to control | Adaptive | Shared SoT |

Parse the user prompt first; only ask about buckets not already answered.

## Synthesis rules

- One bullet = one testable behavior or constraint.
- Deduplicate against comm/role; do not repeat tone rules in git section.
- §6 triggers must be observable; “read CONTRIBUTING first” belongs in comm (**Context before action**), not §6.
- Put **only** harness-native constraints in `*.specific.md`; if a bullet applies in every harness, it stays in SoT.
- Mark stale indicators: “Review quarterly” on fast-changing tooling if user wants.
- Line budget: ~100 lines for shared SoT unless comm/role import split approved; overlays stay short (prefer &lt;40 lines each).
- Adapters are not synthesis targets—thin stubs only (no policy bullets).

## Inclusion bar (user scope)

Still apply the 90% bar: cross-repo prefs that almost always help—not a preference dump. Rare workflows stay out or become situational packs only when justified. Overlay content must pass 90% **for that harness**, not “nice when using Cursor once.”

## Project leak check (review / fix)

Flag in user-global SoT **or** overlays:

- Repo-specific package names, internal URLs, ticket systems
- “In this codebase we use X” → belongs in project `AGENTS.md`
- Model/subagent tables duplicated into SoT → move to the matching `*.specific.md`
