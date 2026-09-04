# brd (Business Requirements Document)

**Cascade level:** 3  
**Inherits from:** executive-summary + MRD  
**Narrows to:** business objectives, stakeholders, and business-level constraints  
**Priority method:** MoSCoW on objectives, rules, and dependencies — [item-schema.md](../../../../refs/planning/doc-standards/item-schema.md)  
**Panel seats:** CFO + COO + domain practitioner (advisory) — [expert-panel.md](../expert-panel.md)  
**Blind-spots (stage-exit):** Scan only the brd row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

## Purpose

Translate market context into business outcomes the organization must achieve. Bridge strategy to product.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Business objectives** | 3–7 measurable business outcomes (revenue, cost, risk, compliance) | Ranked leaves |
| **Stakeholders** | Buyer / user / approver **plus** Power×Interest grid (communicate / satisfy / manage closely / monitor) | Prose (unnumbered) |
| **Capabilities** | Strategic build vs buy vs partner choices (not architecture) | Ranked leaves or prose bullets |
| **Business rules** | Policies, compliance, contractual obligations | Ranked leaves; compliance/contractual = Must |
| **Success criteria** | Business-level acceptance criteria per objective | Attach to the objective leaf body (not separate ids) |
| **Dependencies** | Internal teams, systems, approvals required | Ranked leaves |
| **Business risks** | Organizational, financial, reputational risks with mitigations | Prose (unnumbered); impact × likelihood bullets |

Prefix `BRD`. This is the business-negotiation layer — Must/Should/Could/Won’t is how stakeholders cut scope. Mint `BRD-n` for objectives, rules, and dependencies only.

## Extraction method (discovery)

1. For each MRD customer need, ask "what business outcome does solving this produce?"
2. Map stakeholder roles to MRD segment **prose** (not a segment id).
3. Probe for hidden approvers (legal, security, procurement). Place each stakeholder on Power×Interest.
4. Distinguish business rules (Must comply) from preferences (Should/Could).
5. Each objective gets a success criterion testable at business level, in that leaf’s body.
6. Record build / buy / partner for strategic capabilities; founder/team execution risk when venture posture.

## Traceability

- Cross-doc `parent:` is an `MRD-*` **need**. Same-doc nest: `BRD-n` → `BRD-n.m`.
- Each objective walks to an MRD need and onward to an ES metric.
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

Per-doc bars only. Gate 1, the script, shared success-criteria, and Gate 6 `in_scope` own the rest.

- [ ] At least 3 business objectives with measurable success criteria (fail: "improve efficiency")
- [ ] Buyer and user distinguished (if applicable); Power×Interest grid present
- [ ] Build/buy/partner recorded for strategic capabilities
- [ ] Business rules documented or explicit "none identified"
- [ ] Dependencies listed with owners or "TBD" flagged
- [ ] At least one business risk with mitigation or acceptance (include team/execution risk when venture)
