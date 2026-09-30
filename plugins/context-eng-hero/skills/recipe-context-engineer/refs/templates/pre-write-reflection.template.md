# Pre-write reflection output template

Emit this block on **create**, **fix**, **redesign**, **extract** (file write), **design assist write**, and **improve** (combined draft) before the write gate. **No** numeric score. **PASS** only if every judgment, harness, and opportunity-clean row is PASS (static must already PASS).

```markdown
## Pre-write reflection

- Target: `<relative-path>`
- Type: skill | command | agent | rule | workflow
- Result: **PASSED** | **FAILED**

### Deep reflect
- Invoker simulation: <one line>
- Failure modes blocked: <one line>
- Ambiguity scan: <none | cite>
- Redundancy scan: <none | cite>
- Opportunity scan: <none | cite imp.* / pattern>

### Harness summary
- Reliable: <one line>
- Consistent: <one line>
- Deterministic: <one line>

### Judgment checks
| id | Severity | PASS/FAIL | Evidence |

### Harness checks
| id | Severity | PASS/FAIL | Evidence |

### Opportunity checks
| dimension id | Pattern | Impact | Confidence | Absorb | PASS/FAIL | Evidence |
| (eight `imp.*` dims; PASS = no ranked-eligible survivor under improve filter; FAIL row = would enter apply list) | | | | | | |

### Top patterns
- <labels from failure-patterns.md or improvement-patterns.md if any FAIL>

### Next
- PASSED: proceed to pre-ship, then write, then post-write static
- FAILED: **PRE-WRITE REFLECTION FAILED** — revise draft; re-run reflection → pre-ship; do not write; do **not** treat “run improve next” as gate satisfaction
```

**Verdict:** **PASSED** only if **all** judgment, harness, **and** opportunity-clean rows pass. Any FAIL → **FAILED** and block write.
