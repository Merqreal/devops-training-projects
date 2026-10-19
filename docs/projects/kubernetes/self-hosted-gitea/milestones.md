# Milestones

All requirements here are mandatory. Keep implementation decisions and evidence in your solution repository. Use the [verification procedures](verification.md) and [version contract](versions.md).

## 1 · Local Kubernetes

Provision a named Minikube profile using the Docker driver inside WSL2 Ubuntu. Document CPU, RAM, disk allocation, Docker integration, and actual tool versions. Inspect nodes, control-plane/system pods, and the default StorageClass. Explain provisioner, access mode, volume binding mode, reclaim policy, and where bytes physically reside.

Explain that Docker supplies the container driver, Minikube creates and manages the local cluster, and Kubernetes schedules and reconciles its workloads. WSL2 provides the Linux environment; the Windows host is a separate access boundary.

**Deliver:** start/stop scripts, prerequisites, readiness diagnostics, and storage explanation. Demonstrate dynamic provisioning using the application's PVCs or a disposable claim and consumer; a listed StorageClass alone is insufficient.

**Accept when:** the API responds, nodes are Ready, system pods are healthy, and a consumed PVC binds and supports a write/read. Explain that node-local storage is not replicated and cannot guarantee recovery from workstation loss or cluster deletion.

## 2 · Terraform foundation

Configure version-constrained Kubernetes and Helm providers. Select a dedicated Minikube profile and kubeconfig context explicitly in **both** providers. Do not rely on whatever context happens to be current. Add a preflight that refuses an absent or mismatched target and checks the intended API endpoint. Do not print kubeconfig credentials.

Terraform must manage a dedicated namespace and two Helm releases: PostgreSQL and Gitea. Encode dependencies, readiness waits, and timeouts. Document any documented secret bootstrap phase between namespace creation and application installation. Account for the fact that a provider needs a running cluster before planning.

Use pinned chart versions and commit the Terraform provider lock. Describe the local backend, permissions, ignored files, backups, and recovery after state loss. Do not use this exercise's Gitea instance as a dependency for its own initial Terraform state storage.

**Deliver:** Terraform source, non-secret input documentation, lock file, deployment command, and redacted plan summary.

**Accept when:** `init`, `validate`, `plan`, and `apply` succeed; a second plan has no unexpected changes; a wrong-context preflight fails safely. Run formatting checks. Do not commit state or saved plans as evidence.

## 3 · PostgreSQL

Deploy PostgreSQL through its own Terraform-managed Helm release. Use a single-instance StatefulSet, a PVC of at least 1 GiB, ClusterIP Service, Kubernetes Secret references, explicit database/user configuration, requests and limits, readiness and liveness probes.

Use a dedicated Gitea application role and database with necessary ownership/permissions, rather than connecting Gitea as the database superuser. The selected chart's bootstrap user is a superuser; arrange documented, repeatable initialization of the application role. Account for initialization scripts running only with an empty data directory and for passwords not being reset by changing an initialization input on an existing PVC.

**Deliver:** values or custom Helm source, secret-reference contract, initialization method, and diagnostics. Explain DNS hostname and port from Gitea's namespace and the exact volume mount/data directory for your PostgreSQL major version.

**Accept when:** StatefulSet is ready, PVC is Bound, probes and resource settings are present, and authenticated database access works from the intended application network path. Create a harmless marker row in a dedicated validation table, recreate the PostgreSQL pod, and prove the row remains. Do not modify Gitea-managed tables.

## 4 · Gitea

Use the official Gitea chart. Point it at the separate PostgreSQL Service using Kubernetes DNS, database name, application role, and Secret-sourced password. Disable both bundled PostgreSQL variants. Make deliberate cache, session, and queue choices; do not leave default HA dependencies running unnecessarily on a single-node workstation.

Persist Git repository files on a PVC separate from PostgreSQL's PVC. Configure application server settings, advertised URL, local Git transport, Services, probes, and resource requests/limits. Use a single Gitea replica unless you explicitly justify shared-storage behavior.

Expose HTTP through a documented local method. Make it accessible from Windows, not only from inside WSL. Choose HTTP Git or SSH Git and document authentication, advertised clone URLs, and port mappings. Never embed a token in a clone URL. SSH is optional if authenticated HTTP push and clone pass.

**Deliver:** configuration, local access script, exact browser URL and Git endpoint, and troubleshooting for WSL/Windows routing. Explain application configuration versus chart values.

**Accept when:** Windows browser access works; registration or admin provisioning works; a repository can be created; a commit can be pushed and freshly cloned using the chosen transport. Verify repository files and application metadata survive pod recreation.

## 5 · Persistence and failure testing

Execute and record this sequence:

1. Create a Gitea user and record a non-secret identifier.
2. Create a repository.
3. Commit and push a uniquely identifiable test file; record commit SHA and file checksum.
4. Restart or delete only the Gitea pod; wait for a replacement Ready pod.
5. Reconnect any forwarding, freshly clone the repository, and compare commit and file.
6. Restart or delete only the PostgreSQL pod; wait for database and application recovery.
7. Verify the original user and repository metadata, commit, and SQL marker still exist.
8. Stop and restart the same Minikube profile without deleting it.
9. Re-establish access and verify login, repository content, SQL marker, clone, and a new push.
10. Inspect PVC/PV identities and explain which data lives on each volume.

**Deliver:** dated before/after evidence with pod UIDs, PVC names, commit SHAs, checksums, expected result, actual result, and failures/recovery steps. Avoid replacing real evidence with screenshots of a Ready status alone.

**Accept when:** all required events retain the original identity and content, no manual re-seeding hides data loss, and the lifecycle table in [verification](verification.md) is explained accurately. Release removal and cluster deletion need risk analysis; destructive loss tests are not required.

## 6 · Operational tooling

Provide rerunnable commands or scripts for starting the cluster, deploying, inspecting health, exposing Gitea, viewing both application and database logs, running persistence checks, stopping the cluster, and safely destroying the environment. Include kubectl, Helm, and Terraform diagnostics.

Scripts must fail on errors, use explicit profile/context/namespace, document inputs and prerequisites, and distinguish non-destructive stop from data deletion. Cleanup must show its target and require explicit confirmation for destroying stateful resources or the cluster. Do not silently delete PVCs as part of restart.

**Deliver:** executable scripts with usage instructions, bounded readiness waits, expected outputs, and troubleshooting for Pending PVC, ImagePullBackOff, CrashLoopBackOff, bad DNS/authentication, wrong context, and failed Windows access.

**Accept when:** a reviewer can run routine operations using your README, failures return meaningful nonzero exit status, and cleanup explains release, namespace, PVC, PV, and Minikube lifecycle risks before deletion.

## 7 · Documentation and handover

Write a README covering architecture, prerequisites, deployment, configuration, access, validation, troubleshooting, persistence behavior, and cleanup. Include a Mermaid diagram showing Windows/WSL, traffic, namespace, Services, workloads, Secrets, and both data volumes.

**Deliver:** complete separate solution repository following [standards](../../../standards.md), actual version inventory, sanitized evidence, and requirement-to-evidence checklist. Cite upstream sources and identify untested assumptions and limitations.

**Accept when:** another engineer can reproduce and validate the environment from the README without undocumented mutations or your assistance, and you can explain every component and durability claim.
