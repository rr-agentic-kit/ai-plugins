# brd (Business Requirements Document)

**Cascade level:** 3  
**Inherits from:** exec-summary + MRD  
**Narrows to:** business objectives, stakeholders, and business-level constraints  
**Priority method:** MoSCoW on objectives, rules, and dependencies — [item-schema.md](item-schema.md)  
**Panel seats:** CFO + COO + domain practitioner (advisory) — [expert-panel.md](../expert-panel.md)  
**Blind-spots (stage-exit):** Scan only the brd row in [blind-spots.md](../blind-spots.md) (`in_scope` + `inherit_check`). Do not copy the taxonomy here.

## Purpose

Translate market context into business outcomes the organization must achieve. Bridge strategy to product.

## Required sections

| Section | Content | Items |
|---------|---------|-------|
| **Business objectives** | 3–7 measurable business outcomes (revenue, cost, risk, compliance) | Ranked leaves |
| **Stakeholders** | Roles, interests, influence; buyer vs user vs approver | Unranked leaves (`_moscow_: —`) |
| **Business rules** | Policies, compliance, contractual obligations | Ranked leaves; compliance/contractual = Must |
| **Success criteria** | Business-level acceptance criteria per objective | Attach to the objective leaf body (not separate ids) |
| **Dependencies** | Internal teams, systems, approvals required | Ranked leaves |
| **Business risks** | Organizational, financial, reputational risks with mitigations | Unranked leaves; impact × likelihood in body |

Prefix `BRD`. This is the business-negotiation layer — Must/Should/Could/Won’t is how stakeholders cut scope.

## Extraction method (discovery)

1. For each MRD customer need, ask "what business outcome does solving this produce?"
2. Map stakeholders to segments from MRD.
3. Probe for hidden approvers (legal, security, procurement).
4. Distinguish business rules (Must comply) from preferences (Should/Could).
5. Each objective gets a success criterion testable at business level, in that leaf’s body.

## Traceability

- Cross-doc `parent:` is an `MRD-*` id (need or segment). Same-doc nest: `BRD-n` → `BRD-n.m`.
- Each objective walks to an MRD need and onward to an ES metric.
- Full chain is a parent walk — do not repeat it on every item.

## Done-when checklist

- [ ] At least 3 business objectives with measurable success criteria
- [ ] Buyer and user personas distinguished (if applicable)
- [ ] Business rules documented or explicit "none identified"
- [ ] Dependencies listed with owners or "TBD" flagged
- [ ] At least one business risk with mitigation or acceptance
- [ ] Rankable leaves have `_moscow_`; compliance rules are Must; ranked leaves have `_rationale_`
- [ ] Items use `BRD-{n}` / `BRD-{n.m}` per item-schema
- [ ] All objectives walk to exec-summary success metrics
- [ ] No contradiction with exec-summary non-goals
