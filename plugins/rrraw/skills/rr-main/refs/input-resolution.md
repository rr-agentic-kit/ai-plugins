# rr-main input resolution

**Audience:** Every `rr-main` invocation. Normalize bare / NL / flags into one action payload before load/answer/handoff.

## Primary actions

| Signal | `payload.action` |
|--------|------------------|
| Bare invoke, `--help`, “what is this”, “what is RRRaw” | `orient` |
| “how does X work”, skill/flag/phase/concept named without execute | `explain` |
| “where am I”, “status”, “what’s frozen”, “current phase” | `situate` |
| “what next”, stuck, “recommend next” (no execute) | `suggest` |
| Unambiguous “do X now” / run / invoke peer with clear target | `handoff` (still confirm before peer invoke) |

Exactly one primary action per invocation. Prefer AskQuestion with ≤2 options when NL fits two answer actions (e.g. situate vs suggest); do not invent a third.

## Selectors / filters

| Signal | Effect |
|--------|--------|
| `--role founder-pm` \| `engineer` \| `operator` (or NL role) | Sets `payload.role` for orient filter |
| `--skill <name>` or skill name in NL | Sets `payload.topic` for explain |
| `--text-mode` | Delivery: text options; same choices as AskQuestion |

`--help` is an orient selector, not a separate action.

## NL fallback order

1. Explicit execute-intent with clear peer target → `handoff`
2. Status / frozen / where → `situate`
3. What next / stuck → `suggest`
4. How/what-is about a skill/flag/phase/concept → `explain`
5. Else → `orient`

## Anti-triggers (do not silent-run)

| Intent | Resolution |
|--------|------------|
| Ambient “just build it” / “just discover” without confirm | `suggest` + handoff **offer** — not silent `handoff` execute |
| Overlap with peer Procedure (cascade, slice, CI ship) | `explain` or `suggest` with route; do not reimplement |
| Unlisted skill name (not in catalog / `plugin.json` `skills[]`) | Say unknown; suggest nearest catalog peer — do not invent |

## Project root

`PROJECT_ROOT`:

1. `git rev-parse --show-toplevel` if git repo.
2. Else workspace / cwd root.

Used only for read-only situate paths — never for writes from this skill.

## Output payload

```yaml
action: orient | explain | situate | suggest | handoff
role: null | founder-pm | engineer | operator
topic: null | string          # skill id, flag, phase, or concept for explain
peer: null | string           # catalog skill id when handoff/offer
purpose: null | string        # one-line why for peer invoke
execute_intent: true | false  # true only when user clearly asked to run now
resolution_trace: string[]    # short classify notes
```

Done: payload emitted. Stop with one-line error on conflicting flags that map to two primaries (e.g. `--help` + explicit `--handoff` without NL) — AskQuestion ≤2 instead when recoverable.
