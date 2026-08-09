# agent-index

**Owner:** Packaged agent path fallback when Task path resolution fails.

Orchestrator should prefer `agents/test/*.md` relative to plugin root. Use this index when delegation path is ambiguous.

| Agent | Path | Role |
|-------|------|------|
| init-discovery | `plugins/rrraw/agents/test/init-discovery.md` | Stack discovery, CLAUDE.md patch |
| assess | `plugins/rrraw/agents/test/assess.md` | Exhaustive quality scoring |
| identify-missing | `plugins/rrraw/agents/test/identify-missing.md` | Gap inventory + excluded routing |
| plan | `plugins/rrraw/agents/test/plan.md` | maintain / exclude / add steps |
| write | `plugins/rrraw/agents/test/write.md` | Test edits + coverage_exclude + verify |
| fix | `plugins/rrraw/agents/test/fix.md` | Repair broken tests |
| migrate | `plugins/rrraw/agents/test/migrate.md` | Framework migration |
| flaky | `plugins/rrraw/agents/test/flaky.md` | Flaky triage |
| debug | `plugins/rrraw/agents/test/debug.md` | Failing test diagnosis |
| perf-audit | `plugins/rrraw/agents/test/perf-audit.md` | Suite performance hotspots |
