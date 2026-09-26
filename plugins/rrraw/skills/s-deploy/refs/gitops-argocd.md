# GitOps (Argo CD and similar)

**When:** The repo (or an ops repo) has Argo `Application` / `ApplicationSet` or Flux objects.

## Source of truth

Desired state is **Git**. Agents change Git; the controller reconciles. Do not `kubectl apply` around Argo unless the user asked for an emergency out-of-band fix (then record the Git follow-up).

## Argo CD

- One Application (or ApplicationSet generator) per deployable; destination namespace explicit.
- `syncPolicy.automated` only if the repo already auto-syncs that app. Do not enable prune/selfHeal on prod without confirmation.
- Health: Deployment/StatefulSet/Rollout must go Healthy. Hook Jobs (`PreSync`/`PostSync`) must succeed.
- Images: update the Git tag/digest the Application already kustomizes or helm-values; do not edit live Application spec as the long-term mechanism.

## Promotion

Promote by merging Git (or an image-updater PR), not by clicking Sync to a laptop-built image. Prod sync without a Git SHA the user can audit → stop and ask.

## Rollback

Prefer Git revert of the last good commit, then wait for Healthy. `argocd app rollback` is emergency-only and still needs a Git fix.
