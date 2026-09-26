# CI publish wiring

## Rules

1. Build in CI; publish jobs consume **that pipeline’s** artifacts or the image digest just pushed.
2. Publish on **tags** (libraries) or **default branch** (docs/Pages) — match the repo; do not silently add `push:` to every branch.
3. Pin actions/orbs by SHA or a documented version tag the repo already uses.
4. Fail the job if the version already exists (no silent overwrite) unless the user wants a moving tag (`edge`).
5. Auth via OIDC or CI job tokens only — never long-lived tokens in YAML. Do not log tokens. Prefer `permissions:` least privilege on GitHub Actions; `CI_JOB_TOKEN` scope on GitLab.
6. Tags are immutable after publish; fix-forward with a new version.
7. GitLab `artifacts.paths` must be **relative** (no `$CI_PROJECT_DIR` in paths). See also GitLab nested `refs/pipeline-rules.md`.

## GitHub Actions sketch

```yaml
permissions:
  contents: read
  packages: write
  id-token: write
```

Use `docker/login-action` against GHCR with `GITHUB_TOKEN`, or language trusted-publishing.

## GitLab CI sketch

```yaml
publish:
  rules:
    - if: $CI_COMMIT_TAG
  script:
    - # build then push using $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG
  artifacts:
    paths:
      - dist/   # relative only
```
