# Python runtime (static audit script)

## Version

Use **CPython 3.14+** for [`scripts/audit_static.py`](../../../scripts/audit_static.py).

## Dependencies

Runtime pins: [`scripts/requirements.txt`](../../../scripts/requirements.txt) (`pyyaml>=6.0,<7`).

## Bootstrap (before first run)

From **plugin root**, if `import yaml` fails:

```bash
python3 -m pip install -r scripts/requirements.txt
```

If `uv` is available: `uv pip install -r scripts/requirements.txt`.

Optional local venv (recommended for repeat use):

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/audit_static.py . <relative-path>
```

## Invocation

- **cwd:** plugin root (the installed `context-eng-hero` directory).
- **Paths:** plugin-relative only; first CLI arg is plugin root (usually `.`).

```bash
python3 scripts/audit_static.py . skills/context-engineer/SKILL.md
```

Use `python3.14` when that is the on-PATH interpreter.

## Agents / end users

- The skill does not execute Python — the agent shell runs the script for audit, create pre-ship, and rewrite.
- If bootstrap, install, or run fails: report **STATIC SKIPPED** in the audit output with the reason — do not silently omit static checks.

## Monorepo contributors

Contributor setup and `uv run pytest` are **not** part of the installed plugin. See `CONTRIBUTING.md` at the **ai-plugins repository root** when you have a full checkout.
