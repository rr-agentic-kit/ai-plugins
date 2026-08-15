# frd (Functional Requirements Document)

**Cascade level:** 5  
**Inherits from:** exec-summary + MRD + BRD + PRD  
**Narrows to:** functional behaviors, acceptance criteria, and interfaces  
**Priority method:** consequence triad + derived class — [item-schema.md](item-schema.md)

## Purpose

Specify testable functional requirements engineers can implement and QA can verify. Highest detail level in the cascade. This is the first layer that tells an implementer *how carefully* to build.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **System overview** | Context diagram or boundary description | Prose (unnumbered) |
| **Functional requirements** | Numbered shalls with triad + class | Leaves (containers for grouping only) |
| **Acceptance criteria** | Gherkin-style scenarios per requirement | Attach to the FRD leaf body |
| **Data requirements** | Key entities, attributes, validation rules | Leaves |
| **Integration points** | External systems, APIs, events | Leaves |
| **Non-functional requirements** | Performance, security, availability targets | Leaves |
| **Error handling** | Expected failure modes and system behavior | Leaves |

IDs, parent walk, split, spec/build: [item-schema.md](item-schema.md). Prefix `FRD`. Do not copy MoSCoW or P0/P1/P2 onto FRD items. `build` exists on FRD leaves only.

## Extraction method (discovery)

1. Decompose each Must PRD story into 1–N atomic functional leaves (`FRD-n.m`).
2. Default `if_absent` magnitude from parent PRD MoSCoW (Must → high, Should → moderate, Could → low). Do not compose children of Won’t.
3. Fill `if_wrong` (new at this layer) and derive `Class` per item-schema.
4. Write acceptance criteria in Gherkin: Given/When/Then.
5. Probe happy path AND primary error path per `must-correct` / `must-present` leaf.
6. Capture NFRs even if "standard" — record as assumption if deferred.

## Requirement format

Use the FRD leaf template in [item-schema.md](item-schema.md). Heading + closed metadata, then shall + AC. Do not emit `FR-001`, `Traces to:` chains, or `Priority: P0`.

## Traceability

- Cross-doc `parent:` is a `PRD-*` id (story or feature). Same-doc nest: `FRD-n` → `FRD-n.m`.
- Walk: `FRD-n.m → … → PRD-* → BRD-* → MRD-* → ES-*`.
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] Every Must PRD story has at least one functional leaf
- [ ] Every leaf has Gherkin AC (min 1 happy + 1 error path for `must-correct` / `must-present`)
- [ ] Every leaf has triad axes + derived `Class`; `build` present (`none` until `spec: ready`)
- [ ] Items use `FRD-{n}` / `FRD-{n.m}` per item-schema; compounds split
- [ ] Data requirements cover key entities for Must / `must-present` / `must-correct` features
- [ ] Integration points identified or "standalone" documented
- [ ] NFRs stated or explicitly deferred with assumption
- [ ] Error handling defined for `must-correct` / `must-present` flows
- [ ] Zero unresolved ambiguity in acceptance criteria
