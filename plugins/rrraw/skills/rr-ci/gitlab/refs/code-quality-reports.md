# CI code-quality reports

Fetch findings already published by CI (`reports:codequality`). Not a substitute for a local scanner.

**Invoke:** parent `scripts/README.md`. **Branch keys:** parent `SCRIPTS-SPEC.md`.

Run `code-quality-reports` once; parse `result.reports.count` and `result.reports.nodes`. Do not paginate GraphQL in the agent.

`count: 0` means no report on that pipeline — not an auth error. GraphQL retrieval is glab-only; see [mcp.md](mcp.md).
