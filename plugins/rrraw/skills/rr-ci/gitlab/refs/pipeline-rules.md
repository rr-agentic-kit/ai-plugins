# GitLab `rules:` and artifacts

GitLab `rules:` are first-match-wins. Full syntax: [job control](https://docs.gitlab.com/ci/jobs/job_control/).

## Artifact paths

Runners mount the build dir at different paths. `$CI_PROJECT_DIR` in `artifacts.paths` is unreliable. Use **relative** paths only.

**Bad:** `artifacts.paths: [$CI_PROJECT_DIR/my-file.txt]`  
**Good:** write under `output/` and `artifacts.paths: [output/]`
