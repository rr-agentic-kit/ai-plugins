# domain-routing

**Owner:** Proactive placement tables when a domain topic emerges during Plan or challenge.  
**Load when:** A blind-spot category names a specific domain topic (GDPR, i18n, distribution, security, …) — judgment trigger, no keyword list.  
**Fires:** Once per distinct domain topic per project; user reviews/approves once, skill applies silently thereafter. A genuinely new sub-topic in the same domain re-triggers.

**Not:** a domain registry to match against. No new sidecar file — outcome lives in normal item placement/tags plus an optional `type: domain_routing` raw-history entry.

Cross-reference: [blind-spots.md](blind-spots.md); Discover ES triggers stay in Discover standards.

## Table template

Present **one row per constituent decision**. Columns = surfaces **actually in play** for this topic.

```markdown
| Decision | executive-summary | brd | prd | architecture / delta |
|----------|-------------------|-----|-----|----------------------|
| …        | …                 | …   | …   | …                    |
```

After user approval, place items and tags per the table. Do not persist the table as a separate artifact.

**Plan rule:** Product AC and WWAS live on PRD. Standing invariants → `architecture.md` (+ constitution). Feature mechanism → `deltas/<feature-id>.md`. Root `tech.md` is Discover parking only — do not route Plan AC/ADR there.

## Example 1 — GDPR / privacy

| Decision | executive-summary | brd | prd | architecture / delta |
|----------|-------------------|-----|-----|----------------------|
| **Regime** | Constraint (`regulatory` tag) + `domain_context.regulatory_regime` | Business objective if compliance is measured | — | — |
| **Consent outcome** | Constraint: consent outcome (see/delete/change) | Lawful basis, categories, retention, DPA | WWAS AC for consent UX | Capture/storage/audit mechanism in delta |
| **Security outcome** | Constraint (`quality` tag): protected in transit/at rest | Policies, contractual obligations | Product-facing security features | Controls / encryption in spine or delta |
| **Anonymous vs login** | Mode policy constraint | Approver rules if legal mandates identity | Mode matrix + AC | Auth implementation in delta |

**Skill rule:** ES names **whether** compliance is a success gate. BRD owns negotiable rules. Challenge flags GDPR **mechanism** at ES as `scope_misfiling` → Plan delta/spine or PRD outcome — not `tech.md` AC.

## Example 2 — Legal-risk tiers (T6-1)

| Tier | Meaning | Typical placement |
|------|---------|-------------------|
| `green` | Regime N/A | No ES constraint beyond `domain_context` |
| `yellow` | Compliant position exists; residual risk | ES constraint; BRD risk acceptance |
| `gray` | Compliance status ambiguous | ES constraint + assumption; may need `research_deferred` |
| `red` | Hard procedural gate | ES constraint; BRD dependency with timeline |

**Buyer-perception risk** is a separate MRD finding under `stakeholder_gaps`/`economic`.

## Example 3 — Distribution ladder

| Decision | executive-summary | brd | prd | architecture / delta |
|----------|-------------------|-----|-----|----------------------|
| **Strategy** (when success-critical) | Functional deliverable or constraint: market-compatible channels | Approver rules for channel commitments | — | — |
| **Path family** | ≥1 lawful path family viable | Vendor relationship rules | Channel pick + product AC | Integration mechanism in delta |
| **Tactics** | — (reject at ES) | — | Beta vs alpha vs private link; web vs native; **slice/phase order** (never sprint order) | Deployment mechanics in delta |

**Promotion test:** channel/tech detail defaults to Plan. Promotes to ES **only** when it is itself a hard external constraint.

## After approval

1. Mint or refile items per the approved table.
2. Apply `_tag_:` on ES constraints where helpful.
3. Route Plan mechanism to spine/delta — **not** Plan AC into `tech.md`.
4. Log optional `type: domain_routing` entry in `raw-history/{UTC}.yaml`.
