# Action: diff (internal)

## Load (Read)

- `diff-output.template.md`
- `frontmatter-schemas.md`
- `instruction-design.md` (if intent comparison needs signal/noise lens)

## Steps

### Step 1: `diff-1-read`

- **Outcome:** Both files loaded; comparability assessed.
- **Done when:** Paths **A** and **B** read; if types differ, overlapping dimensions stated once.

### Step 2: `diff-2-compare`

- **Outcome:** Dimensions compared with evidence.
- **Done when:** Intent, discovery, contracts, safety, orchestration compared per template.

### Step 3: `diff-3-report`

- **Outcome:** Tradeoff report delivered.
- **Done when:** Output matches `diff-output.template.md`; recommendation cites evidence; no file edits.

## Stop

If paths are not comparable types, say so once and compare only overlapping dimensions.
