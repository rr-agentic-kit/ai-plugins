# report-template

**Owner:** Markdown report layout for `--output md` (and deprecated `--output report` alias). No orchestration semantics.

Used via [output-formats.md](output-formats.md). Data from phase `PhaseOutput` and chain metadata.

## Header (metadata, not table)

```markdown
# rr-test Report

**Action:** {action} | **Scope:** {scope.kind} | **Verdict:** {aggregate_verdict} | **Epoch:** {current_epoch}/{max_epochs}
**Status:** {final_status}
```

## Primary findings table

Work-queue artifact for agents and humans. Status semantics: [determinism.md](determinism.md) § Finding status lifecycle.

```markdown
## Findings

| ID | Path | Kind | Severity | Status | Evidence | Action |
|----|------|------|----------|--------|----------|--------|
| F1 | OrderServiceTest::shouldShip | over_assertion | medium | flagged | SensitiveEquality: 12-field deep-equal on OrderDTO | assert status+id only |
| F2 | src/foo/Bar.java | missing_coverage | high | flagged | no error-path test | add BarErrorTest |
| F3 | PaymentTest | flakiness_risk | high | fixed | sleep(500) | replaced with awaitility |
```

### Column rules

| Column | Source |
|--------|--------|
| ID | `F{n}` findings, `M{n}` missing, `P{n}` plan steps — stable within run |
| Path | test file, production file, or `file::method` |
| Kind | standardized `signals[].kind` or phase-specific (see output-formats) |
| Severity | `low` \| `medium` \| `high` |
| Status | `flagged` \| `solved` \| `fixed` \| `wontfix` |
| Evidence | concrete pattern from assess signal or agent rationale |
| Action | recommended fix or plan step summary |

## Section tables (omit empty)

### Assess

Redundant and overtest rows may also appear in Findings; optional duplicate subsection:

```markdown
## Assess

| Path | Verdict | Overtest | Redundant |
|------|---------|----------|-----------|
```

Populate `Overtest` / `Redundant` counts from `counts.overtest`, `counts.redundant`.

### Missing

```markdown
## Missing

| ID | Production path | Risk | Suggested test | Status |
|----|-----------------|------|----------------|--------|
```

### Plan

```markdown
## Plan

| ID | Track | Path | Priority | Status | Rationale |
|----|-------|------|----------|--------|-----------|
```

Track: `maintain` \| `add`. Status `flagged` until step executed.

### Changes

```markdown
## Changes

| Path | Operation | Status | Description |
|------|-----------|--------|-------------|
```

Status `solved` on write/fix; `fixed` after verify+reassess.

## Footer

```markdown
## Exit

**Reason:** {exit_reason}
**Epochs completed:** {epoch_count}
```

## Legacy sections

- `Summary`: one paragraph from final phase `summary` — optional above Findings
- `Recommendations`: from init-discovery or plan when present
- `artifacts_list`: deduped paths from all phase `artifacts` — may fold into Changes table

Omit empty sections entirely.
