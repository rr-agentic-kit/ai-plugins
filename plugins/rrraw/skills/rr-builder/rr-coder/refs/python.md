# Python Standards

## Version
Python 3.12+ required. No legacy syntax.

## Type Safety
- Type hints mandatory on all functions, methods, and class attributes
- `mypy --strict` must pass — no `Any`, no `# type: ignore` without explanation
- Use `Final`, `Literal`, `TypedDict`, `Protocol` for tighter contracts
- Prefer `dataclasses` or Pydantic v2 models over plain dicts for structured data

## Validation
- Pydantic v2 for all data at system boundaries (API input, config, external responses)
- Never trust raw dict input — always parse through a model
- Use `model_config = ConfigDict(strict=True)` by default

## ORM / Data Access

| Context | Use | Why |
|---------|-----|-----|
| Default | SQLAlchemy 2.0+ with `Mapped[]` annotations | Type-safe, async support, mature ecosystem |
| FastAPI projects | SQLModel | Pydantic + SQLAlchemy fusion, less boilerplate for CRUD |
| Heavy Postgres | `asyncpg` with raw SQL | Max performance, skip ORM overhead |

- Alembic for all schema migrations — never manual DDL
- Always use 2.0-style API (`select()`, `Session.execute()`) — never legacy `Query` API
- Async sessions via `async_sessionmaker` for async code paths

## Security
- Never use `eval()`, `exec()`, `pickle` on untrusted input
- Use `secrets` module for tokens, nonces, IDs — never `random`
- Never hardcode secrets — use environment variables via `pydantic-settings`
- Validate and sanitize all external inputs
- Use `pathlib.Path` — reject `../` path traversal explicitly
- Parameterize all SQL — never f-string or format() into queries
- Never log secrets, tokens, PII, or card data

## HTTP / Networking
- Use `httpx` — not `requests` for any new code
- Always set explicit timeouts: `httpx.Client(timeout=httpx.Timeout(connect=5.0, read=30.0))`
- Verify SSL by default — never `verify=False`
- Handle `httpx.TimeoutException` and `httpx.HTTPStatusError` explicitly

## Error Handling
- Catch specific exceptions only — never bare `except:` or `except Exception:` without re-raise
- Log with `logger.exception()` not `logger.error(str(e))` — preserves traceback
- Define custom exception hierarchies for domain errors
- Never swallow exceptions silently

## Logging
- Use `structlog` — never `print()` for application output
- Structured logs only — key-value pairs, not free-form strings
- Never log: passwords, tokens, API keys, PAN, CVV, PII
- Cross-language Prefer/Avoid, disposition, **CP028**–**CP030**: [`observability.md`](observability.md)

## Async
- Prefer `asyncio` for I/O-bound work
- Use `asyncio.Lock` / `asyncio.Semaphore` to protect shared mutable state
- Never mix sync blocking calls inside async functions — use `run_in_executor`
- Always set timeouts on async network calls

## Dependencies
- Use `uv` for all project/dependency management — replaces pip, poetry, pyenv
- `pyproject.toml` + `uv.lock` — commit lockfile to source control
- Separate dev dependencies: `uv add --dev pytest mypy ruff bandit`
- Run `uv audit` when adding or updating dependencies
- Docker builds: `uv export --no-hashes -f requirements.txt` for the image — do not install uv in the container
- Prefer stdlib over third-party when equivalent

## Testing
- `pytest` for all tests
- `hypothesis` for property-based tests on boundary/validation logic
- Minimum coverage targets: 80% unit, 60% integration
- Test unhappy paths and security edge cases explicitly

## Tooling (enforce in CI)
- Formatter/linter: `ruff` (replaces black + isort + flake8)
- Type checker: `mypy --strict`
- Security scanner: `bandit -ll`
- Dependency audit: `uv audit`

## Cross-References
- `python.secure.md` — Python-specific security patterns
- `secure.owasp.md` — OWASP Top 10 patterns
- `secure.principles.md` — secrets management, PII protection
- `code.principles.md` — cross-language principles (**CP032**: bind repeated helper calls once per scope)
