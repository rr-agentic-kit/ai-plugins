# brd (Business Requirements Document)

**Cascade level:** 3  
**Inherits from:** exec-summary + MRD  
**Narrows to:** business objectives, stakeholders, and business-level constraints

## Purpose

Translate market context into business outcomes the organization must achieve. Bridge strategy to product.

## Required sections

| Section | Content |
|---------|---------|
| **Business objectives** | 3–7 measurable business outcomes (revenue, cost, risk, compliance) |
| **Stakeholders** | Roles, interests, influence; buyer vs user vs approver |
| **Business rules** | Policies, compliance, contractual obligations |
| **Success criteria** | Business-level acceptance criteria per objective |
| **Dependencies** | Internal teams, systems, approvals required |
| **Business risks** | Organizational, financial, reputational risks with mitigations |

## Extraction method (discovery)

1. For each MRD customer need, ask "what business outcome does solving this produce?"
2. Map stakeholders to segments from MRD.
3. Probe for hidden approvers (legal, security, procurement).
4. Distinguish business rules (must comply) from preferences (nice to have).
5. Each objective gets a success criterion testable at business level.

## Traceability

- Assign ids: `brd-obj-N`, `brd-stakeholder-N`, `brd-rule-N`, `brd-risk-N`.
- Each objective traces to `mrd-need-N` and `exec-metric-N`.
- Stakeholders map to `mrd-segment-N`.

## Done-when checklist

- [ ] At least 3 business objectives with measurable success criteria
- [ ] Buyer and user personas distinguished (if applicable)
- [ ] Business rules documented or explicit "none identified"
- [ ] Dependencies listed with owners or "TBD" flagged
- [ ] At least one business risk with mitigation or acceptance
- [ ] All objectives trace to exec-summary success metrics
- [ ] No contradiction with exec-summary non-goals
