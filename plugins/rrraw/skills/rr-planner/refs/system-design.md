# system-design

**Owner:** Plan altitudes for mechanism and UX-shape — record decisions that change Effort or would diverge across builders. Same Plan sitting as Effort.

**Load when:** Scoring Effort, freezing a slice, or a capability needs a binding mechanism / UX-shape choice.

**Does not:** Dump full stack trees into the spine. Does not author product AC as test code. Does not use root `tech.md` for Plan AC/ADR. Does not own pixels, components, or library calls (Execute).

## Cost-driver test

Record a Plan decision only when **(a)** independent builders would diverge without it, **or** **(b)** the choice changes Effort (tech and/or UX). Happy-Path coding-only Effort fails this test.

| Capture | Where |
|---------|-------|
| Cross-feature invariant (tech or global UX baseline) | `architecture.md` spine (`Binds` / `Prevents` / `Rule`) |
| Feature-local mechanism + Effort drivers + UX-shape | `deltas/<feature-id>.md` — reference spine, do not restate |
| Product pass/fail | PRD WWAS AC — observable, not implementation |

## Three altitudes

| Altitude | Owns | Out |
|----------|------|-----|
| **Standing** | Spine + constitution invariants; global interaction / design-system baseline when Bind/Prevent would diverge | Feature mechanism |
| **Feature** | Delta Decision, Effort drivers, UX-shape (or `n/a`), ADR-lite Rejections | Pixel DoR, component trees |
| **Implementation** | Execute fused code+test | Plan — inventing wizard-vs-form, new integration boundaries, or cost-driving states here fails the altitude wall |

## Same-sitting rule

No feature RICE Effort and no slice freeze until:

1. Architecture decision for that capability exists in this pass (spine update and/or feature delta) with **Decision** + **Effort drivers** (2–5 bullets naming what made Effort = N).
2. UI-facing features include **UX-shape** (interaction pattern, surfaces/flow, cost-relevant states — or explicit `n/a` with reason for pure backend).

Draft spine rev is allowed; **draft ≠ missing** Decision / Effort drivers. Broken obligations are not.

Refuse Effort-without-architecture. Refuse Effort unless the same-sitting delta/spine cites **Effort drivers**. Fibonacci remains a relative size, not sprint capacity.

## Mapping prompts (one at a time)

1. Which requirement leaves force a boundary or change Effort?
2. What must every implementation share (`Binds`) — tech and/or UX baseline?
3. What must never happen (`Prevents`)?
4. What UX cost drivers apply (wizard vs form, permission/empty/error states) — or `n/a` why?
5. What is deferred / out of this slice?

## Anti-patterns

- Happy-Path Effort (coding-only; ignore UX or integration cost drivers)
- Restating the full spine inside a feature delta
- Routing Plan AC to `tech.md`
- Effort as a PM guess with no system judgment / no Effort drivers cite
- Execute inventing Plan-altitude shape (wizard vs form, new integration boundary)
- Hi-fi wireframes / Figma as Plan Definition of Ready
- Sprint / capacity language

## Done-when

- Capability under score has spine and/or delta entry with Decision + Effort drivers
- UI-facing: UX-shape present (or explicit out-of-slice); pure backend: UX-shape `n/a` + reason
- Delta cites spine; no spine copy-paste
- AC remains product-observable (WWAS)
