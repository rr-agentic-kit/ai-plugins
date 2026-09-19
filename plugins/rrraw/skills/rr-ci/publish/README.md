# rr-ci / publish

Publish nested skill. Loaded by **rr-ci** for artifact upload — not cluster deploy. Not plugin-listed. Runtime: [SKILL.md](SKILL.md).

## Why

Separate static/registry publish from runtime deploy so agents pick a destination from repo precedent instead of inventing registries or laptop pushes.

## What

Chooses Pages, container/package registries, Releases, or object storage and wires CI publish jobs (auth, immutability, artifact paths).

**Out of scope:** Kubernetes/Helm/Argo rollout (→ deployment); inventing registry hosts or long-lived tokens in YAML.

## When

### Use when

- GitHub/GitLab Pages, OCI/image push, language package registries, Releases/packages, S3-compatible static uploads

### Avoid when

- Deploying a live cluster workload → sibling `deployment`
- Opening the PR/MR that contains the job → parent rr-ci + forge skill only

## Constraints

- `disable-model-invocation` — load by path from parent only
- Destination must appear in [refs/destinations.md](refs/destinations.md) or stop
- Auth/immutability/paths: [refs/ci-publish.md](refs/ci-publish.md)

## Notes

```
publish/
├── SKILL.md
├── README.md
└── refs/   # destinations.md, ci-publish.md
```
