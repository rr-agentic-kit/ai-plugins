# Bullet formulas

Three formulas for resume bullets. STAR/PAR/SOAR are interview formats — not default resume formats.

**Test:** Every bullet answers "So what?"

## XYZ (default)

**Structure:** Accomplished [X] measured by [Y] by doing [Z]

**Best for:** Default technical achievement; SWE/AI/ML bullets

**Example:**
> Accomplished 99.95% uptime on payment API measured by zero P1 incidents in 18 months by implementing circuit breakers, automated failover, and SLO-based alerting.

**Example (SWE):**
> Reduced authentication API p99 latency from 340ms to 80ms (76% improvement) by redesigning connection pooling and adding Redis caching, serving 2.4M requests/day.

## TEAL (metric-led)

**Structure:** [Result] + [Metric] + [Context]

**Best for:** When the metric is the headline (cost, latency, scale)

**Example:**
> 40% inference cost reduction ($180K/year) on production RAG pipeline serving 2.4M queries/day through model quantization and batch serving optimization.

## CAR (constraint-defined)

**Structure:** Challenge → Action → Result

**Best for:** Incidents, migrations, legacy constraints, zero-downtime wins

**Example:**
> Challenge: Monolith deployment blocked 6 teams weekly. Action: Led strangler-fig extraction of auth service to event-driven microservices. Result: Independent deploys for all teams; deploy frequency 2x/week → 4x/day.

**Example (migration):**
> Migrated legacy LDAP auth to OAuth2/OIDC under zero-downtime constraint during peak season; completed in 6 weeks with no customer-facing incidents across 12 dependent services.

## Selection guide

| Scenario | Formula | Rationale |
|----------|---------|-----------|
| Default technical achievement | **XYZ** | Scannable; metric embedded naturally |
| Impressive number is the hook | **TEAL** | Metric-first for eye-tracking anchor |
| Overcame hard constraint | **CAR** | Challenge frames the win |
| Staff/platform multiplier | **CAR** or compressed STAR | Scope + obstacle visible |

## Teal verb pattern

Success Verb + Noun + Metric + [Strategy Optional] + Outcome

Example: `Reduced` + `API latency` + `76% (340ms→80ms)` + `via Redis caching and connection pooling` + `for 2.4M daily requests`

## Master resume prompt pattern

```
Using non-dramatic language, write 3–5 resume achievements based on my work experience as [title] at [company]. Use XYZ format. Ask if any metric is unclear.
```
