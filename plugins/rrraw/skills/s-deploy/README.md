# s-ci / deployment

Deployment nested skill. Loaded by **s-ci** for runtime rollout — not static/registry publish. Not plugin-listed. Runtime: [SKILL.md](SKILL.md).

## Why

Apply generic Helm/K8s/GitOps patterns from **this repo’s** charts and apps — without employer cluster catalogs or guessing kube contexts.

## What

Detects Helm vs raw manifests vs Argo/Flux, loads the matching ref(s), and follows image immutability, health, promotion, and rollback rules there.

**Out of scope:** Pages/registry publish only (→ publish); inventing cluster names, kubeconfig contexts, or registry hosts absent from the repo.

## When

### Use when

- Helm values/releases, Kubernetes probes/Ingress, Argo CD/Flux sync, env promotion, rollback

### Avoid when

- Static site / registry publish only → sibling `publish`
- CI that never deploys → forge nested skill + `debug-pipeline`
- Neither Helm/K8s nor GitOps evidence on disk → stop (do not deploy from generic patterns)

## Constraints

- `disable-model-invocation` — load by path from parent only
- No production `kubectl`/`helm`/Argo sync without explicit user confirmation
- Policy lives in [refs/helm-kubernetes.md](refs/helm-kubernetes.md) / [refs/gitops-argocd.md](refs/gitops-argocd.md)

## Notes

```
deployment/
├── SKILL.md
├── README.md
└── refs/   # helm-kubernetes.md, gitops-argocd.md
```
