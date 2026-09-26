# Params (CLI flags)

Parse and validate `--voice` and `--tone`; reject unknown values with a one-line error.

## Enums

```
--voice  active | you | keep
--tone   plain | firm | warm
```

## Defaults

| Path | `--voice` | `--tone` |
|------|-----------|----------|
| generate (no flags) | `active` | `plain` |
| rewrite (no flags) | `keep` | extract via `suggest-register`; if mixed → `plain` |

## Examples

```
--voice active --tone plain     # README draft
--voice keep --tone firm        # MR rewrite, fewer hedges
--voice you --tone warm         # how-to (user explicit)
```

## Errors

| Input | Response |
|-------|----------|
| `--voice passive` | `humanize: unknown --voice passive` |
| `--tone neutral` | `humanize: unknown --tone neutral` |
| `--tone casual` | `humanize: unknown --tone casual` |
| Unknown flag | `humanize: unknown flag --<name>` |

## Precedence

User flags > `suggest-register` > path defaults in `refs/register.md`.
