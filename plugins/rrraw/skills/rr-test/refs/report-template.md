# report-template

**Owner:** Optional long-form report layout only. No orchestration semantics.

Used when `--output report`. Data from [output-formats.md](output-formats.md).

## Template

```markdown
# rr-test Report

**Action:** {action}
**Scope:** {scope.kind}
**Status:** {final_status}

## Summary

{final_summary}

## Findings

{phase_findings}

## Changes

{artifacts_list}

## Recommendations

{recommendations}

## Exit

**Reason:** {exit_reason}
**Epochs:** {epoch_count}
```

## Section rules

- `phase_findings`: one subsection per phase in execution order
- `artifacts_list`: deduped paths from all phase `artifacts`
- `recommendations`: from init-discovery or plan phases when present
- Omit empty sections entirely
