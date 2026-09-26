---
name: s-deploy
disable-model-invocation: true
description: /s-deploy — deploy via Helm, Kubernetes, and GitOps (Argo CD); no employer cluster catalogs.
---

# s-ci / deployment

Loaded from parent **s-ci** `SKILL.md` when the task is **deploying a runtime** to a cluster or VM, not only uploading a static artifact.

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

1. **Identify** — Detect in-repo: Helm (`Chart.yaml`, `values*.yaml`), Kustomize, raw YAML, Argo `Application` manifests, Flux Kustomization. Done: deploy mechanism named from disk, not guessed.

**Fallback:** neither Helm/K8s nor GitOps detected → stop; do not deploy from generic patterns. Clarify with the user and/or load only the matching rule set (Helm-only / Argo-only / both) after evidence appears on disk.

2. **Load ref** — [refs/helm-kubernetes.md](refs/helm-kubernetes.md) and/or [refs/gitops-argocd.md](refs/gitops-argocd.md). Done: ref(s) loaded for the detected mechanism.
3. **Follow ref** — Image contract, health probes, promotion, and rollback live in the loaded ref(s). Done: change drafted or applied per those refs.
4. **Stop** — Do not `kubectl apply` / `helm upgrade` / Argo sync to **production** without explicit user confirmation. Prefer changing Git and letting GitOps reconcile when that is the repo’s model.

## Invariants

- Image tags, probes, Helm release naming, and secrets handling: loaded refs only — do not restate encyclopedia rules here.
- Do not invent employer/internal cluster catalogs.
