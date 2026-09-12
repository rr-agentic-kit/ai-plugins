# nature-expectation-packs

**Owner:** Plan-only **reflective method** — given capabilities + `domain_context`, mint the natural Plan expectations that class of system usually owes. Method SoT lives here only.

**Load when:** Interview / capability naming ([plan-interview.md](plan-interview.md)); nature reflection after capabilities or `domain_context` signal product class (auth, identity, tenancy, ops-altitude, siblings). Challenge probes reflection owed vs landed ([challenge-method.md](challenge-method.md)).

**Does not:** Act as a mandatory Plan checklist or closed catalog. Does not name vendor IdP products. Does not invent Execute ops runbooks. Does not live in shared `refs/planning/` this pass. Does not wait for a founder process dump before reflecting.

## Capability

Given capabilities + `domain_context`, **reflect on product nature** and derive Plan expectations that class of system usually owes — requirement / AC / cost-relevant state / UX-shape / spine invariant. Same judgment class as open-fail / retry / circuit once a surface exists: the duty is reflective, not tip-optional. Auth and ops/cross-cut rows below are **worked examples of the class**, not a fire-table or universal checklist.

## Relevance gate

Caching / logging / audit / metrics / recover / verify / IdP / … are **not** required on every Plan. Each **may** be owed when nature/capability signals make it load-bearing. Reflection decides in/out; silence without judgment fails. Do **not** dump a universal checklist; do **not** force-fit every example family into every PRD.

## Procedure

1. **Name nature surface(s)** in play from capabilities + `domain_context` (and which clearly are not).
2. **Derive** which expectation classes apply **for this project** — and which explicitly do not (non-goal or skip with stated reason when ambiguity).
3. **Elicit** or `[ASSUMPTION]` / explicit defer — Coach asks; Fast still covers derived expectations ([plan-interview.md](plan-interview.md)).

Do **not** wait for a founder process dump. Do **not** “fire matching packs from a table.”

## Example families (illustrative only — not SoT, not mandatory)

### Access / identity

When access surfaces are in play, typical expectations include recover, verify, IdP/SSO, B2B tenant access, mailbox OAuth, and failure states (empty, denied, expired, mismatch) — as Plan requirement/state altitude only, not SRE runbooks. Keep axes separate:

`invite` ≠ `register-tenant` ≠ `session login` ≠ `IdP SSO` ≠ `mailbox OAuth`

Placement: [domain-routing.md](domain-routing.md) **Example — Access / identity axes**. Mechanism per axis: [system-design.md](system-design.md).

### Cross-cutting / ops-altitude at Plan

Caching, logging, audit trail, metrics/observability, and siblings of that class — **in** when the bet’s nature implies them (multi-tenant, regulated, high-churn reads, etc.); **out** when nature does not. Plan altitude only (requirement / AC / Effort-driver / UX-shape state) — not Execute procedures.

## Done-when

- Derived-in-scope expectations covered (elicited, per-axis assumed, or explicit defer)
- Out-of-scope classes named as non-goal or skipped with stated reason when ambiguity
- No silent axis conflation across invite / register-tenant / login / IdP / mailbox OAuth when those axes are in play
- Silent omission / waiting-for-dump / blind checklist dump all fail
- Method SoT is this file only — interview / domain / challenge link + check
- **Freeze enforcement:** unmet Done-when (no explicit per-axis HOLD) → Fail freeze ([execute-handoff.md](execute-handoff.md)) — not interview-intent only
