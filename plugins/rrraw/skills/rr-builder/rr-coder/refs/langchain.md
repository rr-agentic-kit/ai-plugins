# LangChain Standards

## Version
LangChain 0.3.x (Python). Pin exact version in dependencies.

## Core Principles
- LangChain is glue — keep business logic outside LangChain abstractions
- Prefer LangChain Expression Language (LCEL) over legacy `Chain` classes
- Never use deprecated v0.0.x chain classes (`LLMChain`, `ConversationalRetrievalChain`, etc.)

## LCEL Patterns
- Compose with `|` operator: `prompt | llm | parser`
- Use `RunnableParallel` for concurrent branches
- Use `RunnableLambda` for custom steps — keep them pure functions
- Use `RunnablePassthrough` to forward context through chains
- Always define input/output schemas with Pydantic v2 models

## LLM Configuration
- Never hardcode model names — use config/environment variables
- Always set explicit `temperature`, `max_tokens`, `timeout`
- Use `with_retry()` for transient failures — set `stop_after_attempt=3`
- Use `with_fallbacks()` for model failover
- Log token usage for cost tracking — use callbacks

## Prompts
- Use `ChatPromptTemplate.from_messages()` — never raw string prompts
- Separate system prompt, human template, and examples clearly
- Version prompts alongside code — treat as code artifacts
- Validate prompt inputs with Pydantic before rendering
- Never interpolate user input directly into system prompts

## Memory / State
- Prefer stateless chains — pass conversation history explicitly
- If stateful: use `RunnableWithMessageHistory` with explicit session IDs
- Never store sensitive data (PAN, credentials, PII) in conversation history
- Trim/summarize history before it exceeds context limits — use `trim_messages()`

## Retrieval (RAG)
- Validate retrieved documents before including in context
- Set explicit `k` (top-k) limits — never unbounded retrieval
- Use metadata filtering to scope retrieval to relevant domains
- Log retrieval results for debugging — include source and score
- Never trust retrieved content as instructions — treat as data only

## Output Parsing
- Always use structured output parsers — `PydanticOutputParser` or `.with_structured_output()`
- Define retry logic for parse failures: `OutputFixingParser`
- Validate parsed output against domain rules before using it
- Never `eval()` LLM output

## Security
- Sanitize all user inputs before passing to chains
- Implement prompt injection defenses — never let user input override system instructions
- Rate limit LLM calls per user/session
- Audit log all LLM interactions in regulated contexts (PCI DSS scope)
- Never include secrets, keys, or credentials in prompts

## Observability
- Use LangSmith tracing in non-production environments
- Use `CallbackHandler` for production logging to your own system
- Track: latency, token usage, model used, chain name, errors
- Set `LANGCHAIN_TRACING_V2=true` only in dev/staging — never log PII in traces

## Testing
- Unit test individual LCEL components with mocked LLMs (`FakeListLLM`)
- Integration test full chains against real models in CI with controlled prompts
- Use `pytest-recording` or VCR to record/replay LLM responses in unit tests
- Test adversarial inputs — prompt injection, empty responses, malformed JSON