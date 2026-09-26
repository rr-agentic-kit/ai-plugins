# Publish destinations

Pick from what the **repo already uses** (workflow files, `.gitlab-ci.yml`, existing packages). Do not introduce a new public registry without the user asking.

| Destination | Typical when | Auth |
|-------------|--------------|------|
| GitHub Pages | Static site in a GitHub repo | `actions/deploy-pages`; `contents`/`pages` permissions |
| GitLab Pages | `public/` artifact + `pages` job | Job on default branch / tag |
| GHCR / GitLab container registry | Images | OIDC (`GITHUB_TOKEN`) or `CI_JOB_TOKEN` + `CI_REGISTRY` |
| GitHub Releases | Tagged binaries, changelogs | `contents: write` on tag workflows |
| GitLab generic/package registry | Non-container artifacts | `CI_JOB_TOKEN` |
| npm / PyPI / Maven | Language libraries | Trusted publishing / OIDC when available |
| S3-compatible | Static buckets | Short-lived OIDC roles, not AKIA in YAML |

Prefer the detected forge’s first-party store unless `package.json` / `pyproject.toml` / Helm `image.repository` already names another host.
