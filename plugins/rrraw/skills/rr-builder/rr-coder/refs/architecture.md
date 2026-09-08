# Architecture review (AR001–AR004)

**Audience:** Code lane review. Mandatory **`## Architecture`** section in the code report — separate from the CP finding table.

**Context:** When **`BRIEF_PATH`** is set, **`Read`** it once before the architecture pass.

## Activation pass (language-neutral)

Sketch **consumer entry → declared/exported/wired surface → changed implementation** when the change looks reusable (library, CI component, plugin, chart, optional module).

Illustrative paths (not exclusive):

- GitLab component job / `!reference` / image → shim → CLI/package
- npm export, Maven reactor/SPI, Go package, Python package entry point
- Helm value/subchart enabling a template
- Plugin manifest loading a skill/agent/command

Inability to prove the path on **new/changed** reusable behavior → **CP010** (dead path), **CP012** (wrong layer), or **CP033** (no followable contract). Live unwired leftovers → Suggestion.

## Rubric

| ID | Meaning | Default | Fail if | Pass if | Do not flag |
|----|---------|---------|---------|---------|-------------|
| **AR001** | Boundary / layering vs stated or implied architecture | Warning | **New/changed** code crosses a documented or established ownership/layer boundary | Change stays within documented or conventional boundary | Pure internal app code with obvious local ownership |
| **AR002** | Cannot evaluate — no architecture/boundary statement | Warning | No boundary doc in brief, repo, MR, or ticket after search | Reviewer can cite a boundary statement | No reusable/public/boundary-changing surface → **NOT_APPLICABLE** |
| **AR003** | Cross-repo / sibling change-set incomplete | Warning | Producer contract changed and named sibling consumer MR/repo not available to judge compatibility | Sibling change-set cited and reviewable, or MR explicitly scoped to this repo only | Inventing compatibility conclusions without evidence |
| **AR004** | Required resilience / limit / crypto decision coverage | Warning | **New/changed** production code matches an **AR004 trigger** below and at least one **required decision** has no cite after search | Every required decision for matched triggers is cited | See **AR004 applicability** and **Do not flag** below |

**AR002** must state searched sources and what boundary remains unknowable. **AR003** includes one scope-expansion question. Do not invent an architecture.

## AR004 — required decision coverage

**When it applies:** **New/changed** production code creates a surface that always needs an explicit resilience, limit, or crypto **decision** — including **explicit none** and why.

**NOT_APPLICABLE** when the diff has no new/changed egress, ingress, or sensitive hop.

**AR001** stays **boundary/layering**. **AR002** is **no boundary statement** for reusable surfaces. **AR004** is **missing cited decision** on ingress/egress/sensitive hops — not implementation-mode enforcement. Do not double-emit the same miss as **CP033** unless there is also no usage contract.

### What counts as covered

A **decision** is covered when the reviewer can cite **one** of:

- Accepted ADR (or equivalent in-repo architecture note)
- Org/platform standard
- Mesh/gateway config
- Brief/MR that **names the choice** (including explicit **none** and why)

Record cites in evidence (`Context: adr: <path>`, `Context: searched: …`, platform standard name).

### Triggers and required decisions

| Trigger in **new/changed** production code | Required named decisions |
|--------------------------------------------|--------------------------|
| **Egress / downstream** — call out of process (HTTP/gRPC, queue, third-party SDK, remote DB) | **Circuit** (breaker / timeout+fail-fast / explicit none) **and** **cache** (yes with outline, or explicit none) |
| **Ingress / API** — network-exposed handler (HTTP/gRPC/webhook), not an in-process interface | **Rate limit** (this service, gateway/mesh, or explicit none) **and** **load shedding** (shed/queue/429/degrade, or explicit none) |
| **New sensitive store or hop** — persist or transit secrets/PII/credentials on a path that did not already have a cited crypto story | **Encryption approach** (or “platform default / already encrypted in transit+at rest” with cite) |

**Fail if:** Trigger matches **and** after search (`Context: searched: …`) at least one required decision has **no** cite.

**Pass if:** Every required decision is cited (platform “all egress uses Resilience4j per ADR-012” counts for circuit on that egress).

### Do not flag

- In-process calls (no out-of-process egress)
- Adding a field to an API already covered by a cited gateway ADR
- Health/probes when org standard excludes them
- Live unchanged egress/ingress (Suggestion at most)
- Logging, metrics, correlation (**CP028**–**CP030**)
- Error swallow vs rethrow (**CP007**)
- Authn/authz, injection, secrets (security lane)
- Unbounded size / no max (security lane — not ADR-skippable)
- Premature cache/pool (**CP024** — whether to add a shield at all)
- Missing encryption **mechanism** where required (security lane); missing **decision record** is **AR004**

### Escalate to Critical

Money, authz, or catalog **ingress** with **no** cited rate-limit **and** load-shedding decision after search.

### Encryption vs security

- No TLS / no at-rest protection where required → **security** (not skippable by ADR).
- New S3 bucket / new PII column / new hop and **no cited crypto decision** → **AR004** (write the ADR or cite platform default).

### ADR authoring hints (not AR004 Fail-ifs)

When an ADR or brief chooses **cache = yes**, it should address usual pitfalls — cohort TTL / jitter, hot-key refill, absent keys, and origin behavior if the cache is down. See [`adr-template.md`](../../../architecture/architect/templates/adr-template.md). Architecture does **not** Warning-fail jitter if an Accepted ADR chose a fixed TTL.

Implementation bugs (empty catch) stay **CP007**. Unbounded size stays **security always-have-limits** (ADR does not waive).

**`--fix` does not invent ADRs.** Recommendation: add ADR or cite existing platform doc. Warning still blocks clean code until a decision is cited.

## Report section (mandatory)

After the CP table:

```markdown
## Architecture
Result: PASS | ISSUES | NOT_APPLICABLE
| ID | severity | target | issue | evidence | recommendation |
```

- **NOT_APPLICABLE** — one sentence (e.g. no reusable/public/boundary-changing surface; or no egress/ingress/sensitive hop for AR004).
- For **AR004**, cite the **trigger** (egress / ingress / sensitive hop), which **decision(s)** are missing, and what was searched.
- AR **Warnings** participate in Challenge and block a clean code outcome.
- AR **Suggestions** and CP009 naming Suggestions remain flag-only; **`--fix`** does not auto-remediate design/naming Suggestions or **AR004**.

## New vs live

| Surface | New/changed | Live unchanged |
|---------|-------------|----------------|
| Structural defect | CP Warning | Suggestion or omit |
| Vague naming | CP009 Suggestion; CP013 if convention violation | Do not bike-shed |
| Architecture leak | AR001 Warning | Suggestion or omit |
| Missing cited decision | AR004 Warning | Suggestion or omit |

AR remediation may add documentation or request scope — must not silently redesign public contracts.

## Overlap

- **CP033** — no followable usage/delivery contract (traceability).
- **CP017** — inline rationale on complex API (not delivery contract).
- **CP027** — tunables on an existing contract.
- **AR002** — cannot judge boundaries (not the same as missing usage doc).
- **AR004** — missing cited resilience/limit/crypto **decision** on ingress/egress/sensitive hop (not boundary leak — **AR001**; not whether to add cache — **CP024**; not unbounded size — security lane; not missing TLS/mechanism — security lane).
- **CP024** — premature optimization (whether to add cache/pool at all).
