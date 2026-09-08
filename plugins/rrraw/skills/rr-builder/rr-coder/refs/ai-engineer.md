# AI Engineer Standards

Production LLM/ML integration: validate untrusted model output, pin versions, keep LLM off ungated money paths. Not responsible for training models.

## LLM Integration Principles
- Treat LLM outputs as untrusted external input — always validate before use
- Design for non-determinism — same input can produce different outputs
- Design for failure — LLMs hallucinate, timeout, and return malformed responses
- Never put LLMs in the critical path of financial transactions without human gate
- Keep LLM logic decoupled from business logic — replaceable without core changes

## Prompt Engineering Standards
- Version all prompts in source control — treat as code
- Document prompt intent, expected input/output format, and known failure modes
- Use structured output (JSON mode, function calling) over free-text parsing
- Test prompts against adversarial inputs before production
- Never interpolate user-controlled data into system prompts
- Separate concerns: system prompt (behavior) vs human prompt (task) vs examples (few-shot)

## Prompt Injection Defense
- Validate that user input cannot override system instructions
- Use delimiters to clearly separate trusted and untrusted content
- Implement output validation — if output matches injection patterns, reject it
- Log and alert on suspected injection attempts

## Model Selection & Configuration
- Document model choice rationale: capability, cost, latency, data residency
- Pin model versions — never use floating aliases like `gpt-4` in production
- Set explicit: `temperature`, `max_tokens`, `timeout`, `top_p`
- For deterministic tasks (extraction, classification): `temperature=0`
- For creative tasks: document why higher temperature is acceptable

## Reliability Patterns
- Retry with exponential backoff on transient failures (429, 502, 503)
- Set circuit breakers on LLM service calls — degrade gracefully
- Implement fallback model or fallback behavior when primary LLM unavailable
- Timeout all LLM calls — never unbounded wait
- Cache deterministic LLM responses (same prompt+params → same output) with a semantic cache and TTL; skip when sampling is non-deterministic

## Cost Control
- Track token usage per feature, per user, per request
- Set hard limits — reject requests that would exceed token budget
- Use smaller/cheaper models for classification/routing, larger for generation
- Implement token counting before sending — reject oversized inputs early
- Alert on cost anomalies

## Context Management
- Never exceed context window — implement chunking, summarization, or retrieval
- Trim conversation history proactively — don't wait for context limit error
- Use RAG for knowledge that doesn't fit in context
- Track context utilization as a metric

## Data Privacy & Compliance
- Never send PII, PAN, credentials, or health data to external LLM APIs without approval
- Implement PII detection before sending to LLM (Presidio or equivalent)
- For PCI DSS scope: LLM processing of cardholder data requires explicit scope review
- Data residency: verify LLM provider region matches compliance requirements
- Audit log all LLM interactions in regulated contexts

## Evaluation & Quality
- Implement offline evals before deploying prompt changes
- Use golden dataset of inputs/expected outputs for regression testing
- Track quality metrics in production: task success rate, user corrections, fallback rate
- A/B test prompt changes — don't deploy blind
- Monitor for model drift when provider updates base model

## RAG / Retrieval
- Validate retrieval quality — low-relevance results degrade output silently
- Implement retrieval fallback — if nothing relevant found, say so rather than hallucinate
- Chunk documents with overlap — avoid splitting context across chunk boundaries
- Store metadata with vectors — enables filtering and explainability
- Re-rank retrieved results before including in context

## Agents & Autonomy
- Limit agent autonomy proportional to action reversibility
  - Read-only: higher autonomy acceptable
  - Write operations: require confirmation or human gate
  - Irreversible operations (send email, charge payment): require explicit human approval
- Implement max step/iteration limits on all agentic loops
- Log every agent action with inputs, outputs, and rationale
- Design kill switch — ability to halt agent mid-execution

## Observability (Non-Negotiable)
- Every LLM call must emit: model, tokens_in, tokens_out, latency, success/error
- Trace full request flow from user input to LLM response to final output
- Sample and store LLM inputs/outputs for offline analysis (with PII scrubbing)
- Alert on: latency p99 > threshold, error rate > 1%, cost spike > 2x baseline
- Cross-language Prefer/Avoid, disposition, **CP028**–**CP030**: [`observability.md`](observability.md) — LLM call metrics stay mandatory here; refactor still does not silent-add meters elsewhere

## Testing
- Unit test: prompt rendering, output parsing, validation logic
- Integration test: full chain against real model with controlled inputs
- Adversarial test: prompt injection, empty responses, malformed JSON, oversized input
- Load test: LLM calls under concurrency — verify rate limit handling
- Regression test: golden dataset eval on every prompt change