# domain-routing

**Owner:** Proactive placement tables when a domain topic emerges during discovery or challenge.  
**Load when:** A blind-spot category names a specific domain topic (GDPR, i18n, distribution, security, enrichment law, …) — judgment trigger, no keyword list.  
**Fires:** Once per distinct domain topic per project; user reviews/approves once, skill applies silently thereafter. A genuinely new sub-topic in the same domain re-triggers.

**Not:** a domain registry to match against. No new sidecar file — outcome lives in normal item placement/tags plus an optional `type: domain_routing` raw-history entry.

Cross-reference: [blind-spots.md](blind-spots.md) categories may trigger this ref; [exec-summary.md](doc-standards/exec-summary.md) inline triggers during ES discovery.

## Table template

Present **one row per constituent decision**. Columns = cascade levels **actually in play** for this topic (omit unused levels). Content is domain-specific judgment — no universal row schema across domains.

```markdown
| Decision | exec-summary | brd | prd | tech.md |
|----------|--------------|-----|-----|---------|
| …        | …            | …   | …   | …       |
```

After user approval, place items and tags per the table. Do not persist the table as a separate artifact.

## Example 1 — GDPR / privacy (T1)

| Decision | exec-summary | brd | prd | tech.md |
|----------|--------------|-----|-----|---------|
| **Regime** | Constraint (`regulatory` tag): "Must comply with GDPR" + `domain_context.regulatory_regime` | Business objective if compliance is a measured outcome | — | — |
| **Consent outcome** | Constraint (`regulatory` tag): "Consent required for taste profile + feedback; see/delete/change" | Business rule: lawful basis, data categories, retention policy, vendor DPA | Product backlog items for consent UX flows | Mechanism: consent capture, storage, audit trail |
| **Security outcome** | Constraint (`quality` tag): "User data protected in transit/at rest" (no mechanism) | Security policies, contractual obligations, risk acceptance | Product-facing security features | Controls, encryption specifics, key management |
| **Anonymous vs login** | Functional deliverable or constraint on **mode policy** | Stakeholder/approver rules if legal mandates identity | Mode matrix, per-mode behavior | Auth implementation detail |

**Skill rule:** ES names **whether** compliance/privacy/security is a product-success gate and **what obligation class** applies. BRD owns negotiable business rules (MoSCoW). Challenge flags GDPR **mechanism** at ES as `scope_misfiling`.

## Example 2 — Legal-risk tiers (T6-1)

When a domain topic carries legal exposure, pair the placement table with a **four-tier risk assessment** (none of these tiers auto-block — human owns the call):

| Tier | Meaning | Typical placement |
|------|---------|-------------------|
| `green` | Regime N/A | No ES constraint needed beyond `domain_context` |
| `yellow` | Compliant position exists, but regime risk stays non-zero (enforcement bias, litigation cost/benefit independent of legal merit) | ES constraint stating the obligation; BRD for negotiated risk acceptance |
| `gray` | Compliance status itself ambiguous — could go either way | ES constraint + explicit assumption in What-must-be-true; may need `research_deferred` |
| `red` | Hard procedural gate (license/inspection required) — flagged by cost/time | ES constraint; BRD dependency with timeline |

Evidence preference: real enforcement-in-practice/case statistics over literal statute reading.

**Buyer-perception risk** (T6-1b) is a **separate finding** under MRD `stakeholder_gaps`/`economic` — risk-averse buyers avoid murky-looking offerings independent of actual legal exposure.

## Example 3 — Distribution ladder (O3)

| Decision | exec-summary | brd | prd | tech.md |
|----------|--------------|-----|-----|---------|
| **Strategy** (when success-critical) | Functional deliverable or constraint: "Distributed via market-compatible channels" (e.g. iOS + Android stores) | Stakeholder/approver rules for channel commitments | — | — |
| **Path family** (lawful enrichment) | Constraint or functional deliverable: "≥1 lawful path family viable" (manual curation / licensed provider / aggregator API / policy-compliant collection) | Business rules for vendor relationships | Channel pick + integration detail | API integration, scraping policy |
| **Tactics** | — (reject at ES) | — | Beta vs alpha vs private link; web vs native; sprint order | Deployment mechanics |

**Promotion test (T6-3):** channel/tech detail defaults to PRD. Promotes to ES **only** when it is itself a hard external constraint — near-monopoly/no practical alternative, or a regulation specifically names that mechanism. Framed as a constraint/dependency, never a URL/vendor dump.

## After approval

1. Mint or refile items per the approved table.
2. Apply `_tag_:` on ES constraints where helpful (`regulatory`, `capacity`, `quality`, `technical`, …).
3. Append mechanism overflow to `tech.md` when placement column says so.
4. Log optional `type: domain_routing` entry in `raw-history/{UTC}.yaml` for judgment calls worth preserving.
