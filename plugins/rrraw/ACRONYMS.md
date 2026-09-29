# Acronyms

| Acronym | Expansion | Notes |
|---------|-----------|-------|
| ES | Elevator Statement | Discover cascade stem |
| MRD | Market Requirements Document | Discover cascade stem |
| BRD | Business Requirements Document | Discover cascade stem; freeze → Plan handoff |
| PRD | Product Requirements Document | Plan compose; after Discover freeze |
| RICE | Reach, Impact, Confidence, Effort | Scoring; Effort honesty in Plan |
| RIC | Reach, Impact, Confidence | RICE without Effort when Effort deferred |
| WWAS | When / Who / Action / Success | Acceptance criteria shape |
| AC | Acceptance Criteria | Often WWAS-shaped |
| MoSCoW | Must / Should / Could / Won't | Priority method |
| NFR | Non-Functional Requirement | Standing / spine constraints |
| GTM | Go-To-Market | Market framing |
| ICP | Ideal Customer Profile | Market framing |
| JTBD | Jobs To Be Done | Market framing |
| TAM | Total Addressable Market | Market sizing |
| SAM | Serviceable Addressable Market | Market sizing |
| SOM | Serviceable Obtainable Market | Market sizing |
| SoT | Source of Truth | Version / freeze law |
| ADR | Architecture Decision Record | **Tech only** under architecture/`adrs/` — ids `ADR-n`; not product deltas |
| DEC | Decision (product / feature-delta) | decision-lite ids on `deltas/`; not `ADR-*` |
| OMTM | One Metric That Matters | Discover north-star metric for goal-likelihood |
| INTENT | Plugin Spec file (`INTENT.md`) | Process-ownership UX SoT — not README overview |
| PR | Pull Request | GitHub forge ship unit; pair with MR |
| MR | Merge Request | GitLab forge ship unit; pair with PR |
| CPNNN | Coder Principles rule ID (`CP` + 3 digits) | Builder code-lane findings; e.g. `CP013` — not `CP-13` |
| OWASP | Open Worldwide Application Security Project | Builder security lane Top 10 patterns |
| ARNNN | Architecture review rule ID (`AR` + digits) | Builder code-lane architecture section; e.g. `AR004` |
| L1 | Prepare layer 1 — ordered `task-summary` | s-prepare; capability atoms + depends_on |
| L2 | Prepare layer 2 — detailed `{NNNN}.md` task | s-prepare; one atom at a time |
| L3 | Prepare layer 3 — PR division map | s-prepare; no forge open |
| WBS | Work Breakdown Structure | s-prepare ordered task tree under `docs/rr/tasks/` |
| NL | Natural Language | Parent/user invoke without an explicit path or flag |
| TBD | To Be Defined | Reserved for unspecified future builder stages — **refactor** is implemented via **s-refactor** |
| Sonar | SonarQube / SonarCloud analysis | s-ci `--fix --sonar` + `sonar-list-issues` |
