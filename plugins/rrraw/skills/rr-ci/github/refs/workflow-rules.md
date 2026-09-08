# GitHub Actions rules

- `if:` is not first-match GitLab `rules:`; every job/step evaluates independently unless you `needs:` a gate job.
- Artifact upload paths are relative to `GITHUB_WORKSPACE`. Do not embed absolute runner paths.
- `pull_request` vs `push` vs `workflow_run`: debug “job never ran” by reading `on:` and `if:` in the workflow file, not by guessing.
- Required checks are configured in branch protection / rulesets — a green optional job does not mean mergeable.
