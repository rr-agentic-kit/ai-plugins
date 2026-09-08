# init-discovery

Function-style executor for `--init`. No routing logic.

## Input

`PhaseInput` with `phase: "init-discovery"` and normalized `payload.action === "init"`.

## Execution

1. Run discovery depth checklist from [init-mode.md](../../skills/rr-builder/rr-tester/refs/init-mode.md).
2. Infer stack, conventions, and philosophy from repo evidence.
3. Emit questions per question protocol; recommendations per suggestion protocol.
4. Discover existing coverage exclusion config and non-testable patterns per [coverage-exclusions.md](../../skills/rr-builder/rr-tester/refs/coverage-exclusions.md).
5. Build `claude_md_patch` per [claude-md-schema.md](../../skills/rr-builder/rr-tester/refs/claude-md-schema.md) including Coverage exclusions field.

## Output

Return `PhaseOutput` JSON only. `data` contract: [contracts.md](../../skills/rr-builder/rr-tester/refs/contracts.md) § init-discovery.

| `status` | When |
|----------|------|
| `ok` | Checklist complete, no blocking questions, patch ready |
| `partial` | Blocking questions remain |
| `failed` | Cannot read repo or unrecoverable error |

## Constraints

- Do not invoke other phase agents.
- Do not write `CLAUDE.md` directly; return patch for orchestrator.
