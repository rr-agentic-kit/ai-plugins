# system-design

**Owner:** When a requirement forces a service / API / data-model decision, record it in the standing spine or a feature delta — same Plan sitting as Effort.

**Load when:** Scoring Effort, freezing a slice, or a capability needs a binding mechanism choice.

**Does not:** Dump full stack trees into the spine. Does not author product AC as test code. Does not use root `tech.md` for Plan AC/ADR.

## Decision test

Record a system-design decision only when **independent builders would diverge** without it (same BMAD spine test as architecture):

| Capture | Where |
|---------|-------|
| Cross-feature invariant | `architecture.md` spine (`Binds` / `Prevents` / `Rule`) |
| Feature-local mechanism | `deltas/<feature-id>.md` — reference spine, do not restate |
| Product pass/fail | PRD WWAS AC — observable, not implementation |

## Same-sitting rule

No feature RICE Effort and no slice freeze until the architecture decision for that capability exists in this pass (spine update and/or feature delta). Draft spine allowed; broken obligations are not.

## Mapping prompts (one at a time)

1. Which requirement leaves force a boundary?
2. What must every implementation share (`Binds`)?
3. What must never happen (`Prevents`)?
4. What is deferred / out of this slice?

## Anti-patterns

- Restating the full spine inside a feature delta
- Routing Plan AC to `tech.md`
- Effort as a PM guess with no system judgment
- Sprint / capacity language

## Done-when

- Capability under score has spine and/or delta entry
- Delta cites spine; no spine copy-paste
- AC remains product-observable (WWAS)
