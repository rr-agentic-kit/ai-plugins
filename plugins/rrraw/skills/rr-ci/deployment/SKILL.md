---
name: deployment
disable-model-invocation: true
description: Deploy artifacts to healthy servers via Helm, Kubernetes, Argo CD, and related GitOps. Loaded by rr-ci — not a top-level plugin skill. No company cluster catalogs.
---

# rr-ci / deployment

Loaded from parent **rr-ci** `SKILL.md` when the task is **deploying a runtime** to a cluster or VM, not only uploading a static artifact.

## Purpose

Apply generic deploy patterns: image immutability, health probes, Helm vs raw manifests vs GitOps (Argo CD / Flux), environment promotion. Read the **repo’s** charts and GitOps apps; do not assume a named company cluster.

## When to use

- Helm chart values, release names vs app names
- Kubernetes Deployments, Services, Ingress/Gateway, probes, PDBs
- Argo CD Application / ApplicationSet, sync waves, health
- Promotion test → staging → prod
- Rollback (`helm rollback`, Argo sync to previous, Git revert)

## When not to use

- Static site / registry **publish only** → sibling **publish** skill
- Debugging CI that never deploys → forge nested skill + `debug-pipeline`
- Inventing cluster names, kubeconfig contexts, or registry hosts the repo does not already use

## Procedure

1. **Source of truth** — Detect in-repo: Helm (`Chart.yaml`, `values*.yaml`), Kustomize, raw YAML, Argo `Application` manifests, Flux Kustomization. Done: deploy mechanism named from disk, not guessed.
2. **Load ref** — [refs/helm-kubernetes.md](refs/helm-kubernetes.md) and/or [refs/gitops-argocd.md](refs/gitops-argocd.md).
3. **Image contract** — Pipeline builds and pushes an immutable tag; runtime pulls that tag. Do not rebuild the app inside the runtime image unless the repo already does.
4. **Health** — Require liveness/readiness (or Argo health) before calling the deploy successful. Prefer the repo’s existing probe paths.
5. **Stop** — Do not `kubectl apply` / `helm upgrade` / Argo sync to **production** without explicit user confirmation. Prefer changing Git and letting GitOps reconcile when that is the repo’s model.

## Invariants

- Helm **release name** is not necessarily the ingress hostname; override names in values, do not rename releases casually.
- `latest` tags are not a promotion strategy.
- Secrets: reference existing ExternalSecrets/SealedSecrets/CSI — never commit secret values.
