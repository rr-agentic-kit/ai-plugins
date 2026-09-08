# Python Test Reference (pytest)

Load for **`.py`** test files. Production Python standards: `skills/code/coder/refs/python.md` — this ref covers **test** layout and oracles only (not HTTP/ORM production rules).

## Commands

```bash
pytest                                    # All tests (repo root or package dir)
uv run pytest                             # When pyproject.toml uses uv
uv run pytest tests/test_foo.py -k name   # Single test
uv run pytest -m integration              # k3d / cluster-marked tests only
uv run pytest -m "not integration"        # Unit tests only
```

Resolve package root from `pyproject.toml` location (repo root or `scripts/*/pyproject.toml`).

## Layout

- Tests in `tests/` sibling to `src/` or package root
- Naming: `test_*.py` or `*_test.py`
- Mirror package structure under `tests/` when the package is non-trivial
- Shared fakes/fixtures in `conftest.py` or `tests/fakes/`

## Structure (AAA)

- **Arrange** — build inputs, inject fakes (e.g. fake kubectl runner, stub cluster client)
- **Act** — call the function or CLI entry under test
- **Assert** — behavior on outputs, side effects, and raised exceptions

Prefer one logical behavior per test; use `@pytest.mark.parametrize` for input variations.

## Unit vs integration

| Marker | When |
| ------ | ---- |
| (none) | Pure logic, injected fakes, no real cluster/DB/HTTP |
| `@pytest.mark.integration` | Real cluster CLI, k3d, or other live boundary |

**Injected fakes count as unit** — do not classify injected-fake tests as integration.

## Fakes over live cluster

- Prefer injectable runners and fakes for cluster CLI / GitLab API boundaries
- Use k3d integration only when fakes cannot honestly model the behavior
- Never require a live cluster for pure resolver/oracle logic

## Property-based tests

Use **`hypothesis`** when clear invariants exist (parsers, validators, round-trips). Align with `python.md` Testing section.

## Oracle validation (fail-when-removed)

After green:

1. Break or remove the behavior under test
2. Confirm pytest **fails** for the right reason
3. If it still passes, strengthen assertions or rewrite

## CI component repos

