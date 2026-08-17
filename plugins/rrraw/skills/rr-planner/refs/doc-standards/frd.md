# frd (Functional Requirements Document)

**Cascade level:** 5  
**Inherits from:** exec-summary + MRD + BRD + PRD  
**Narrows to:** functional behaviors, acceptance criteria, and interfaces  
**Priority method:** consequence triad + derived class — [item-schema.md](item-schema.md)  
**Panel seats:** Staff engineer + SRE/QA + domain practitioner (advisory) — [expert-panel.md](../expert-panel.md)  
**Blind-spots (stage-exit):** Scan only the frd row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

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

Prefix `FRD`. Do not copy MoSCoW or P0/P1/P2 onto FRD items. `build` exists on FRD leaves only. Triad: [item-schema.md](item-schema.md).

## Extraction method (discovery)

1. Decompose each Must PRD story into 1–N atomic functional leaves (`FRD-n.m`).
2. Default `if_absent` magnitude from parent PRD MoSCoW (Must → high, Should → moderate, Could → low). Do not compose children of Won’t.
3. Fill `if_wrong` (new at this layer) and derive `Class` per item-schema.
4. Write acceptance criteria in Gherkin: Given/When/Then.
5. Probe happy path AND primary error path per `must-correct` / `must-present` leaf.
6. Capture NFRs even if "standard" — record as assumption if deferred.

## Requirement format

Use the FRD leaf template in [item-schema.md](item-schema.md). Heading + one `_key_:` meta line; shall and Gherkin AC stay inside the blockquote body. Do not emit `FR-001`, `Traces to:` chains, or `Priority: P0`.

## Traceability

- Cross-doc `parent:` is a `PRD-*` id (story or feature). Same-doc nest: `FRD-n` → `FRD-n.m`.
- Walk: `FRD-n.m → … → PRD-* → BRD-* → MRD-* → ES-*`.
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

Per-doc bars only. Gate 1, the script, shared success-criteria (including compound leaves and the vague-term table), and Gate 6 `in_scope` own the rest.

- [ ] Every Must PRD story has at least one functional leaf
- [ ] Every `must-correct` / `must-present` leaf has Gherkin AC (min 1 happy + 1 error path) (fail: "works correctly")
- [ ] Data requirements cover key entities for Must / `must-present` / `must-correct` features (fail: "the database")
- [ ] Integration points identified or "standalone" documented
