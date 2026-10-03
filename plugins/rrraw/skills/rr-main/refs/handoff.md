# rr-main handoff

**Audience:** When execute-intent is detected or user accepts a handoff offer. Confirm gate + peer SKILL invoke contract.

## Confirm gate

Before any peer invoke, AskQuestion (text fallback) with:

- Target skill id (from catalog)
- One-line purpose (what the peer should accomplish this turn)

Options shape: Accept handoff | Stay in suggest | Something else. Cap one confirm gate; do not re-ask if user already said “yes, run X for Y”.

## Peer SKILL invoke

On accept only:

1. Resolve peer path from catalog (`skills/<name>/SKILL.md`)
2. Invoke via **Task** or **Read** peer `SKILL.md` + purpose — same pattern as planner↔builder (`peer SKILL invoke` in plugin glossary)
3. **Do not** Read peer `refs/` to perform the peer’s job
4. **rr-main stops owning the turn** — no further answer/suggest Procedure after peer start

## Decline

On decline or “Stay in suggest”: return to suggest posture; optional revised Next Up. No peer load.

## Anti-triggers

| Signal | Behavior |
|--------|----------|
| Ambient “just build it” without confirm | Suggest + offer only — never silent builder |
| Unknown peer | Refuse handoff; explain nearest catalog skill |
| Purpose empty after confirm attempt | One AskQuestion for purpose, then stop if still empty |

## Anti-patterns

- Do not start Discover/Plan/Build/CI Procedure inside rr-main
- Do not chain multiple peer skills in one rr-main turn
- Do not treat handoff accept as license to skip peer entry gates — peer SKILL owns those
