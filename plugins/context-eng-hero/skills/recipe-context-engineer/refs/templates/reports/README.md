# Lean emit + schema + render (CE reports)

**When:** An agent would otherwise paste large report/scaffold markdown, reinvent severity math, or re-emit the same table shape every turn.

**Contract**

| Role | Does |
|------|------|
| Task / subagent | Emits **lean JSON** only (plus one-line status) |
| `*.schema.json` | Output contract — agents **Read** this |
| Parent + `scripts/render_ce_report.py` | Validate → Jinja-render human markdown |
| `*.md.j2` | Scaffolding SoT — **never** load into agent context |

**Layout (this folder):** `<kind>.schema.json` + `<kind>.md.j2` for `compliance`, `opportunity`, `apply-plan`, `reflection`.

**Invoke** (plugin root = context-eng-hero):

```bash
python3 scripts/render_ce_report.py <kind> --in <payload.json> --out <report.md>
```

| Exit | Meaning |
|------|---------|
| 0 | Wrote `<path>` on stdout |
| 2 | Schema validation (or I/O/JSON) failed — fix lean JSON and re-run; do **not** Write full markdown |

Stderr on validation failure: `render_ce_report validation error:` plus `path: message` lines.

**Target skills absorbing SCRIPTABLE report waste:** copy this pattern under that skill’s `refs/templates/reports/` (+ thin `scripts/render_*.py`, or shared plugin helper when appropriate). Document invoke + exit 2 in the skill Procedure / `helper-cli.md` recipe. See skill `refs/helper-cli.md` **Lean emit + schema + render**.
