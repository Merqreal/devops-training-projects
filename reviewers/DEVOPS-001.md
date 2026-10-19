# Reviewer notes — DEVOPS-001

REVIEWER_ONLY_DO_NOT_PUBLISH

Not included in the site. These notes remain visible to anyone with repository access; no confidentiality is implied. The strategy below has not been executed against a learner deployment.

## Evaluation criteria

All mandatory gates must pass; stretch goals cannot offset failures.

| Area | Required evidence / gate |
| --- | --- |
| Local platform | Correct WSL2/Docker profile, Ready nodes/system pods, real PVC write/read |
| Terraform | Namespace and two releases owned in state; explicit context in both providers; clean validate and second plan |
| PostgreSQL | StatefulSet, >=1 GiB Bound PVC, ClusterIP, Secret references, app role/database, probes/resources, marker survives |
| Gitea | Official pinned chart, both bundled DBs disabled, external DB DNS/credentials, separate repository PVC, correct URL |
| Functionality | Windows browser access, user/repository creation, authenticated push and fresh clone |
| Durability | New pod UIDs, unchanged identity/SHA/checksum/SQL marker after each required event, new push after cluster restart |
| Operations | Complete scripts/runbook, bounded failure checks, explicit targets, safe cleanup |
| Security / handover | No committed secrets/state/plans, documented injection/risks, reproducible README and diagram |

Reject missing mandatory behavior, fabricated evidence, unintended context targeting, real committed credentials, database public exposure, or a claim that local PVCs survive cluster deletion by guarantee. Ask for remediation and new evidence rather than assigning completion from screenshots alone.

## Common failure modes

- Bundled HA PostgreSQL/Valkey left enabled: excess pods/resources or application wired to the wrong database. Inspect rendered dependencies and effective app configuration without exposing secrets.
- CloudPirates auth.username mistaken for an ordinary role: app runs as superuser. Check role attributes and database owner. Require separate initialization of an application account.
- Password changed in a Secret but existing database not rotated: initialization only runs on empty PGDATA. Check bootstrap idempotence and explicit rotation procedure.
- PostgreSQL 18 volume path copied from an old tutorial: data written outside the intended mount. Inspect actual PGDATA/mount and test real pod replacement.
- Terraform sensitive variables assumed absent from state: inspect source data flow, local state and Helm storage privately. Never upload state as review evidence.
- Ephemeral Git files mistaken for metadata persistence: require fresh clone and checksum as well as login/repository listing.
- Port-forward stops with target pod: require reconnection in runbook; do not misclassify this as database loss.
- Windows localhost differs from WSL localhost: inspect WSL networking and local bind rather than opening all interfaces.
- PVC Pending under delayed binding: inspect consuming pod, provisioner/events and actual StorageClass before changing defaults.
- Release uninstall assumed to retain all data: inspect PVC ownership, StatefulSet retention, keep annotations, namespace ownership and PV reclaim policy.
- Empty plan produced against a different cluster: compare explicit contexts/API endpoint and profile before mutation.

## Expected technical explanations

Learner should trace Windows request through local forwarding/Service to Gitea, then DNS/ClusterIP to PostgreSQL. They should distinguish Docker driver, Minikube lifecycle and Kubernetes reconciliation; database rows from Git objects; pod/container storage from PVC/PV; workload removal from namespace/PVC/cluster deletion; readiness from functional correctness; state redaction from secret elimination; and local persistence from backup/HA.

Ask why Terraform can plan only after cluster availability, how both providers select a target, why sensitive values can still reach state/Helm records, why bootstrap must not rotate secrets blindly, why initialization scripts cannot repair an existing database automatically, and why privileged containers are unnecessary here. Accept justified alternatives that satisfy every mandatory outcome.

## Reference validation strategy

1. Review the submitted immutable SHA and README on a clean local workstation meeting prerequisites. Inspect history as well as current files for secrets; handle any discovered credential without reproducing it in review comments.
2. Read scripts before execution, identify destructive operations, and confirm profile/context/API endpoint. Run wrong-target guard tests without applying to unrelated clusters.
3. Verify tool versions, chart pulls, image references, lock files, Terraform formatting/init/validate/plan/apply. Review ownership and secret references; inspect state only locally with learner consent and redact all output.
4. Check actual workloads, security contexts, probes, resources, Service types, PVC mounts, database role attributes and external database connection. Verify from the application network path.
5. Use Windows browser and an authenticated Git client to create a unique user/repository and push a marker. Save SHA/checksum plus non-secret metadata. Create a separate SQL validation marker.
6. Recreate Gitea then PostgreSQL pods individually. Compare new UIDs, same PVCs, user login, metadata, fresh clone and marker. Do not re-seed missing data.
7. Stop/start the same Minikube profile, restore forwarding, repeat assertions and push a second commit. Record actual times/errors.
8. Obtain a no-change second plan after recovery. Review cleanup behavior and data retention without requiring destructive loss testing. Explain deletion risk before any voluntary teardown.
9. Report each gate as passed, failed, or not executed. Keep sanitized review results separate from the published assignment.
