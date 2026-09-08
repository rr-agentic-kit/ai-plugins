# Pipeline security reports

Fetch findings already on the GitLab **pipeline security** tab. Not a substitute for an application security review.

**Invoke:** parent `scripts/README.md`. Branch on `result.status`, `result.merge_blocked`, `result.findings.blocking_count`, `result.findings.blocking_nodes`.

When `merge_blocked` is true, list blocking nodes and stop merge until the user decides.
