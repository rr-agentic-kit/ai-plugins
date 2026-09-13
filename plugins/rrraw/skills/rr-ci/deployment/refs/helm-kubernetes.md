# Helm and Kubernetes

**When:** The repo has charts, `values*.yaml`, Kustomize, or raw manifests. Diff **this repo** before copying patterns from elsewhere.

## Helm

- Chart `name` / release name / ingress host are independent knobs. Changing the release name can orphan secrets and PVCs.
- Values overlays: `values.yaml` + `values-<env>.yaml`. Do not fork the chart to change one replica count.
- `image.tag` must be the immutable digest or CI-built tag — not `latest` for prod.
- `helm upgrade --install --atomic` (or Argo auto-sync with prune/health) for rollbacks.

## Kubernetes

- **Readiness** gates traffic; **liveness** restarts. Do not point both at a heavy dependency check.
- PodDisruptionBudget before `maxUnavailable` on PDBs that would block rollouts.
- Resource requests required for scheduling; limits as the repo’s policy (not invented).
- Ingress/Gateway TLS and DNS belong in the same change as the Service name.

## Health before “done”

A deploy is not successful until pods are Ready **or** the GitOps app is Healthy. `kubectl apply` exit 0 is not enough.
