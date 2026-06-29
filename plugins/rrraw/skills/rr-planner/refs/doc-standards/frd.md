# frd (Functional Requirements Document)

**Cascade level:** 5  
**Inherits from:** exec-summary + MRD + BRD + PRD  
**Narrows to:** functional behaviors, acceptance criteria, and interfaces

## Purpose

Specify testable functional requirements engineers can implement and QA can verify. Highest detail level in the cascade.

## Required sections

| Section | Content |
|---------|---------|
| **System overview** | Context diagram or boundary description |
| **Functional requirements** | Numbered reqs with unique ids |
| **Acceptance criteria** | Gherkin-style scenarios per requirement |
| **Data requirements** | Key entities, attributes, validation rules |
| **Integration points** | External systems, APIs, events |
| **Non-functional requirements** | Performance, security, availability targets |
| **Error handling** | Expected failure modes and system behavior |

## Extraction method (discovery)

1. Decompose each P0 PRD story into 1–N functional requirements.
2. Write acceptance criteria in Gherkin: Given/When/Then.
3. Probe happy path AND primary error path per requirement.
4. Ask for data validation rules when user describes inputs.
5. Capture NFRs even if "standard" — record as assumption if deferred.

## Requirement format

```markdown
### FR-001: [Short title]

**Traces to:** prd-story-3, prd-goal-1, brd-obj-2

**Description:** The system shall...

**Acceptance criteria:**
- Given [context], When [action], Then [outcome]
- Given [error context], When [invalid action], Then [error behavior]

**Priority:** P0 | P1 | P2
```

## Traceability

- Assign ids: `fr-N` or `FR-NNN`.
- Every requirement traces to `prd-story-N` (minimum).
- Full chain: `fr-N` → `prd-story-N` → `prd-goal-N` → `brd-obj-N` → `exec-metric-N`.

## Done-when checklist

- [ ] Every P0 PRD story has at least one functional requirement
- [ ] Every requirement has Gherkin acceptance criteria (min 1 happy + 1 error path for P0)
- [ ] All requirements have unique ids and traceability chain
- [ ] Data requirements cover key entities for P0 features
- [ ] Integration points identified or "standalone" documented
- [ ] NFRs stated or explicitly deferred with assumption
- [ ] Error handling defined for P0 flows
- [ ] Zero unresolved ambiguity in acceptance criteria
