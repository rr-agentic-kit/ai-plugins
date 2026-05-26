# Pre-write reflection output template

Emit this block on **create**, **fix**, **redesign**, and **design assist write** before the write gate. **No** numeric score. **PASS** only if every judgment and harness row is PASS (static must already PASS).

```markdown
## Pre-write reflection

- Target: `<relative-path>`
- Type: skill | command | agent | rule | workflow
- Result: **PASSED** | **FAILED**

### Harness summary
- Reliable: <one line>
- Consistent: <one line>
- Deterministic: <one line>

### Judgment checks
| id | Severity | PASS/FAIL | Evidence |

### Harness checks
| id | Severity | PASS/FAIL | Evidence |

### Top patterns
- <labels from failure-patterns.md if any FAIL>

### Next
- PASSED: proceed to pre-ship, then write
- FAILED: **PRE-WRITE REFLECTION FAILED** — revise draft; re-run static → reflection → pre-ship; do not write
```

**Verdict:** **PASSED** only if **all** judgment and harness rows pass. Any FAIL → **FAILED** and block write.
