# Observability (coding lane)

Cross-language Prefer/Avoid for logs, metrics, and correlation. **Not** stack SDK tutorials — language details live in stack refs (`java.md` §Logging, `java.spring.md` §Observability, `python.md` §Logging, `typescript.md` §Logging / Diagnostics, `kotlin.md` §Logging / Diagnostics, `go-1.26.md` §Logging / Diagnostics, `rust.md` §Logging with Tracing, `ai-engineer.md` §Observability).

**Overlap with CP007:** CP007 is swallow-vs-rethrow (“log with context and rethrow”). These rules cover **instrumentation quality** on existing or new edges — not whether errors propagate.

**Out of scope:** dashboard/alert design, Helm APM sidecars, security-lane OWASP logging audit (cross-link only), inventing SLOs, inventing propagation when the stack has none, naming a company-wide redact library when the repo has none.

**Operate lane:** When telemetry exists and the task is query/triage/dashboard (not instrumentation), use project observability tooling when the task is query/triage/dashboard (not instrumentation).

Map findings to **CP028** / **CP029** / **CP030** in [`compliance-rubric.md`](compliance-rubric.md).

## Prefer / Avoid

| Area | Prefer | Avoid | Why |
|------|--------|-------|-----|
| **Established logger** | Project/stack logger peers already use (SLF4J, structlog, pino/winston, slog, tracing) | Homegrown wrapper over `print`/`System.out`/`console.log`; second logging facade in the same service | One pipeline for levels, MDC/trace, redaction hooks |
| **Established redact** | Project/stack redact path when PII must appear (logback/encoder masking, structlog processors, pino redact paths, platform filters peers use) | Hand-rolled `replace`/`substring` “masking”; ad-hoc regex at call sites | Incomplete masks, inconsistent fields, easy to miss new keys |
| **Log shape** | Parameterized / structured calls with stable field names | String concat, `print` / `console.log` as the only app logger, free-form-only messages | Unstructured logs break search, sampling, and safe redaction |
| **Safety** | Redact secrets, tokens, PAN, raw PII; fail closed (omit field or use redactor output) | Passwords, bearer tokens, card data, unmasked PII; log raw then “hope” downstream scrubbing | Aggregators retain raw forever |
| **Levels** | Level matches intent (see **Level matrix**); `error`/`warn` with enough context to act | Wrong level on existing calls; `error` with no fields; failures only as `debug`/`info` | Operators cannot triage; noise hides real failures |
| **Log signal** | Actionable events only (see **Log worth-emitting**); one event → one primary log at owning boundary | Happy-path chatter, body dumps, loop spam, duplicate same-level logs up the call chain | Volume drowns signal; restates metrics |
| **Correlation** | Include trace/request id when the stack already provides MDC / OTEL / Micrometer Tracing / equivalent | Invent ad-hoc correlation ids or skip ids on request/handler paths when peers already correlate | Without shared ids, logs cannot join traces |
| **Metrics** | RED + owned saturation on critical edges when peers instrument; rare stable business counters | Silent new critical HTTP/consumer/job edges with no meter while siblings emit Micrometer/OTEL/Prometheus | Blind spots on paths that already have a metrics culture |
| **Cardinality** | Low-cardinality labels (status, operation, error class) | Unbounded ids (`userId`, `orderId`, raw URLs) as **metric label** keys | Explodes series cost and breaks aggregations |
| **Metric signal** | Series that answer an operational question (page, chart, capacity-plan) | Vanity / duplicate / high-noise meters (see **Metric vanity**) | Fewer clear series beat sprinkled `*.count` |
| **Noise** | Bounded debug; sample or summarize payloads | Hot-path `debug` of full payloads; identical logs inside tight loops | Volume drowns signal and risks PII |

## Log worth-emitting / noise

**Worth a log** when an operator or debugger can act without reading source: state transitions that change outcomes, boundary failures, retries/exhaustion, authz denials, idempotency conflicts, unexpected empty results on critical paths.

**Not worth a log** (flag as noise / Suggestion–Warning under **CP028** when present): happy-path chatter every request, restating what metrics already cover, dumping full request/response bodies, logging inside tight loops, duplicate identical messages at multiple layers for the same event at the same level.

**One event → one primary log** at the owning boundary; deeper frames add fields or rely on stack traces — do not re-log the same failure up the call chain at the same level.

## Level matrix

| Level | Use for | Do not use for |
|-------|---------|----------------|
| **error** | Operation failed; needs attention or will surface to caller as failure; include actionable context | Expected business declines (use warn/info), routine validation rejects already returned to client |
| **warn** | Degraded but handled: retries left, fallback used, approaching limit, deprecated path hit | Silent success paths |
| **info** | Coarse lifecycle: process start/stop, config mode, rare significant business milestone (not every request) | Per-request “entered method X” |
| **debug** / **trace** | Local diagnosis; gated off in prod by default; no secrets/PII even at debug | Production always-on payload dumps |

Wrong level on an **existing** statement → hygiene `fix`. Inventing new info spam sites → escalate.

## Metric worth-emitting / vanity

**Worth a metric** when it answers an operational question repeatedly: **RED** (rate, errors, duration) on critical request/consumer/job edges; saturation/queue depth when the component owns a pool/queue; business counters only when **stable, low-cardinality, and decision-driving** (e.g. `payments_authorized_total` by result class).

**Not worth a metric** (flag unnecessary / vanity under **CP029** when peers already have a clean set — or Suggestion when introducing noise): per-method “entered”, counters that duplicate HTTP server defaults without extra labels of value, high-cardinality dimensions, one-off debug counters left in production, metrics with no conceivable alert or dashboard consumer.

**Rule of thumb:** if you would never page, chart, or capacity-plan from it — do not emit it. Prefer fewer series with clear names over sprinkling `*.count` everywhere.

**Missing vs excess:** **CP029** flags **missing** meters when peers instrument **and** **unnecessary** meters (vanity / duplicate / high-noise). Escalate schema **removal**; do not silent-delete series in refactor without human (breaking dashboards).

## When not to flag

- Pure domain / library modules with **no** runtime edge (no HTTP, consumer, job, or CLI I/O) — do not demand metrics culture (**CP029** demote).
- Stack has **no** existing Micrometer / OTEL / Prometheus / structured-logger culture on peer paths — missing meters are Suggestion at most, not Critical.
- No MDC/OTEL/tracing already present — do **not** invent propagation (**CP030** do-not-flag for missing correlation).
- **No peer redactor culture** — omit the PII field; do **not** invent a redact library or facade (**CP028** do-not-flag for “missing redactor”).
- Framework auto-metrics only (HTTP server defaults) with no extra vanity labels — demote under **CP029**; do not demand removal of framework defaults.
- Dashboard, alert rule, sampling policy, or Helm sidecar gaps — out of coding-lane scope; **operate** → [`observability/SKILL.md`](../../../observability/SKILL.md) when telemetry exists.
- Same line already owned by security-auditor OWASP logging / toolchain security finding — dedupe; do not double-emit unless adding non-overlapping insight.
- CP007 already covers empty catch / log-and-ignore — do not restate as CP028 unless the **existing** log call itself is unstructured, unsafe, wrong-level, or noisy.

## Refactor disposition (Phase 8 / fix flows)

Ambition: **hygiene + flag**. Auto-apply only hygiene on **existing** log (or clearly local noise) statements. Never silently add meters, spans, `@Observed`, or **new** log sites. Never silently remove metric series.

| Finding class | Disposition | Notes |
|---------------|-------------|-------|
| Existing call: string concat → parameterized/structured; add missing params on an **existing** call | `fix` | Behavior-invariant log shape |
| Existing call: swap onto project logger when peers already use that facade | `fix` | Established-logger hygiene |
| Existing call: apply **existing** redactor API peers already use; secrets/PII → redact/remove | `fix` if clearly safe; else `escalate_human` | Introducing a new redact library / inventing a facade → `escalate_human` |
| Existing call: wrong level / missing context fields; drop clearly local noisy log | `fix` | Adjust level/fields or drop local noise on the same statement |
| Hot-path full-payload `debug` / duplicate loop logs (clearly local) | `fix` when local hygiene; `escalate_human` for high-volume product decisions | Do not invent sampling policy |
| Missing counter/timer/histogram / `@Observed` / new span on critical boundary | `clarify` or `escalate_human` | Never silent `fix` |
| Vanity / duplicate meter present; remove series or change metric schema | `escalate_human` | Breaking dashboards — never silent-delete |
| Missing trace/request id when stack already correlates peers | `clarify` or `escalate_human` | Do not invent propagation |
| Unbounded ids as **metric label** keys on existing meters | `escalate_human` | Do not rewrite metric schemas silently |
| New log site “for completeness” with no existing call | `clarify` / `escalate_human` | Not hygiene |

Disposition values: `fix` \| `clarify` \| `escalate_human`. Cite **CP028**–**CP030** when applicable; type **`observability`** on Phase 8 rows for these findings (language Prefer/Avoid that are not observability stay `language_ref`).

## Stack pointers

| Stack | Detail |
|-------|--------|
| Java | [`java.md`](java.md) §Logging |
| Spring | [`java.spring.md`](java.spring.md) §Observability |
| Python | [`python.md`](python.md) §Logging |
| TypeScript | [`typescript.md`](typescript.md) §Logging / Diagnostics |
| Kotlin | [`kotlin.md`](kotlin.md) §Logging / Diagnostics |
| Go | [`go-1.26.md`](go-1.26.md) §Logging / Diagnostics |
| Rust | [`rust.md`](rust.md) §Logging with Tracing |
| AI / LLM | [`ai-engineer.md`](ai-engineer.md) §Observability |
