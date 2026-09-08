# agent-index

**Owner:** Packaged agent path fallback when Task path resolution fails.

Orchestrator should prefer `agents/test/*.md` relative to plugin root. Use this index when delegation path is ambiguous.

| Agent | Path | Role |
|-------|------|------|
| init-discovery | `agents/test/init-discovery.md` | Stack discovery, CLAUDE.md patch |
| assess | `agents/test/assess.md` | Exhaustive quality scoring |
| identify-missing | `agents/test/identify-missing.md` | Gap inventory + excluded routing |
| plan | `agents/test/plan.md` | maintain / exclude / add steps |
| write | `agents/test/write.md` | Test edits + coverage_exclude + verify |
| fix | `agents/test/fix.md` | Repair broken tests |
| migrate | `agents/test/migrate.md` | Framework migration |
| flaky | `agents/test/flaky.md` | Flaky triage |
| debug | `agents/test/debug.md` | Failing test diagnosis |
| perf-audit | `agents/test/perf-audit.md` | Suite performance hotspots |
