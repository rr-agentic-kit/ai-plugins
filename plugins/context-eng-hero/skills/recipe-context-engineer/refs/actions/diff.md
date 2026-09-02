# Action: diff (internal)

## Ref index (Read at step)

| Ref | When |
|-----|------|
| `disambiguation.md` | `diff-1-read` |
| `templates/diff-output.template.md` | `diff-3-report` |
| `frontmatter-schemas.md` | `diff-2-compare` |
| `instruction-design.md` | `diff-2-compare` (if intent comparison needs signal/noise lens) |
| `close-contract.md` | `diff-3-report` |

## Steps

### Step 1: `diff-1-read`

- **Outcome:** Both files loaded; comparability assessed.
- **Done when:** Paths **A** and **B** read; if types differ, overlapping dimensions stated once.

### Step 2: `diff-2-compare`

- **Outcome:** Dimensions compared with evidence.
- **Done when:** Intent, discovery, contracts, safety, orchestration compared per template.

### Step 3: `diff-3-report`

- **Outcome:** Tradeoff report delivered.
- **Done when:** Output matches `templates/diff-output.template.md`; recommendation cites evidence; no file edits; follow-ups verb-only per `close-contract.md`.

## Stop

If paths are not comparable types, say so once and compare only overlapping dimensions.
