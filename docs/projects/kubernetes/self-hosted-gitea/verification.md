# Verification and operations

## Command conventions

The following are diagnostic scaffolding, not an implementation. Run Bash inside WSL2 Ubuntu. Have the pinned tools installed and cluster running. Examples use a learner-chosen profile/context called `training-001` and namespace `training-001`; align those names with your implementation. Replace explicitly named resource placeholders with observed names. Do not copy commands into a different cluster.

```bash
export PROFILE=training-001
export CONTEXT=training-001
export NAMESPACE=training-001
minikube status -p "$PROFILE"
kubectl config get-contexts "$CONTEXT"
kubectl --context "$CONTEXT" cluster-info
kubectl --context "$CONTEXT" get nodes
kubectl --context "$CONTEXT" -n kube-system get pods
kubectl --context "$CONTEXT" get storageclass
kubectl --context "$CONTEXT" -n "$NAMESPACE" get pods,svc,pvc
kubectl --context "$CONTEXT" -n "$NAMESPACE" get events --sort-by=.metadata.creationTimestamp
helm --kube-context "$CONTEXT" -n "$NAMESPACE" list
```

Expected: the named profile runs, API is reachable, nodes are Ready, required pods are Ready, Services are correctly typed, and PVCs are Bound. Investigate scheduling/provisioning events for Pending claims; `WaitForFirstConsumer` may require a consuming pod before binding.

For logs and detailed inspection, first discover names; substitute actual values for `POD_NAME`, `PVC_NAME`, and `RELEASE_NAME`:

```bash
kubectl --context "$CONTEXT" -n "$NAMESPACE" describe pod POD_NAME
kubectl --context "$CONTEXT" -n "$NAMESPACE" describe pvc PVC_NAME
kubectl --context "$CONTEXT" -n "$NAMESPACE" logs POD_NAME --all-containers=true --tail=100
kubectl --context "$CONTEXT" -n "$NAMESPACE" logs POD_NAME --previous --tail=100
helm --kube-context "$CONTEXT" -n "$NAMESPACE" status RELEASE_NAME
```

Use previous logs only when a previous terminated container exists. Inspect both Gitea and PostgreSQL. Keep credentials out of shared diagnostics. `helm get values`, rendered manifests, Terraform plan output, and application configuration can contain secrets; inspect locally and redact before sharing.

## Terraform repeatability

From the learner's `terraform/` directory, with provider inputs and secret bootstrap prepared:

```bash
terraform fmt -check -recursive
terraform init -lockfile=readonly
terraform validate
terraform plan
terraform apply
terraform plan -detailed-exitcode
```

On the initial authoring run, use `terraform init` to create the lock file before requiring readonly mode. Review the apply prompt. For the final command, exit 0 means no changes, 2 means changes, and 1 means an error. Explain any difference. A generic shell `set -e` wrapper must handle exit 2 deliberately. Demonstrate a wrong-target preflight rejection without applying to another cluster.

## Local access and Git

A possible local access diagnostic, after replacing `GITEA_HTTP_SERVICE` and matching your Service port:

```bash
kubectl --context "$CONTEXT" -n "$NAMESPACE" port-forward   --address 127.0.0.1 service/GITEA_HTTP_SERVICE 3000:3000
```

Keep the process running. Verify `http://localhost:3000` inside WSL and from the Windows browser. WSL networking varies: document your Windows/WSL version and localhost forwarding or mirrored-network setup. If Windows cannot connect, diagnose that boundary; do not fix it by exposing PostgreSQL or blindly binding all interfaces. Ensure Gitea's advertised URL matches the reachable endpoint. Re-establish forwarding after pod replacement or cluster restart.

Use a user-created repository and authentication supplied through a prompt, credential helper, or SSH agent. Push a marker commit, then clone into a **new directory**. Compare `git rev-parse HEAD` and `sha256sum` of the test file against the originals. Check user login and repository identity after each failure event. Ready pods alone do not prove Git or database correctness.

## Persistence evidence contract

Record the same user, repository URL without credentials, commit SHA, file checksum, SQL marker, PVC/PV identities, and old/new pod UIDs for each event. Use a validation table outside Gitea's schema. Run the SQL check via an authenticated in-cluster client or documented application-network test without putting passwords on the command line.

| Event | Required observation | Evidence |
| --- | --- | --- |
| Initial deployment | User, repository, commit and SQL marker created | Baseline IDs and checksum |
| Gitea pod recreation | New pod UID, original user and fresh clone succeed | Before/after UID and SHA |
| PostgreSQL pod recreation | New pod UID, metadata and SQL marker remain | Query result, login, clone |
| Same-profile Minikube stop/start | Workloads recover; original data and new push work | Status, SHA, checksum, query |

Do not use `minikube delete` for these tests. Wait for readiness and functional recovery between failures. Use bounded waits and document actual recovery times. A failed test must remain visible with its diagnosis and rerun result.

## Final functional verification (mandatory)

Run this gate **after the persistence tests**, against the final configuration you submit. A reviewer must see a successful end-to-end result before DEVOPS-001 is complete.

1. Open the documented Gitea URL in the Windows browser. Log out of any administrator account and log in as a **normal, non-administrator user**; provision that user safely first if necessary.
2. In the web interface, create a new, uniquely named **empty** repository owned by that user. Do not initialize it with a README. Copy the advertised clone URL without credentials; check that its host, port, and transport are reachable from your Git client.
3. From a new working directory in WSL, run the following example after setting `GITEA_REPOSITORY_URL` to that credential-free URL. Use a prompt, credential helper, or SSH agent for authentication. Configure your Git author identity locally if it is not already set.

```bash
git clone "$GITEA_REPOSITORY_URL" final-functional-check
cd final-functional-check
git switch -c functional-check
printf '%s\n' 'DEVOPS-001 final functional verification' > verification.txt
git add verification.txt
git commit -m "Verify DEVOPS-001 Git workflow"
git push -u origin functional-check
git rev-parse HEAD
sha256sum verification.txt
```

Record each command's exit status immediately (for example, `echo "$?"`) and stop to investigate any failure. A warning that the newly created remote repository is empty is expected; a failed command is not. Use a unique directory if `final-functional-check` already exists.

4. Refresh the repository in the browser and select the `functional-check` branch. Open the new commit and `verification.txt`; confirm the full commit SHA and file content match the local results. Capture sanitized evidence showing the signed-in user, repository, branch, commit, and file. Do not capture tokens, credential-helper contents, browser cookies, or authentication headers.
5. Clone the same repository into another new directory, check out `functional-check`, and compare the commit SHA and file checksum. Record expected versus actual results, timestamps, configuration/submission SHA, and the credential-free repository URL.
6. If push or any other operation fails, retain its exit status and error excerpt, correlate its timestamp with Gitea current/previous container logs and PostgreSQL logs as relevant, and inspect Service endpoints and storage events. Correct the cause through your documented configuration workflow, rerun this gate, and retain both failed and successful evidence. Do not mark DEVOPS-001 complete with an unresolved failure.

A Git client decoding error or HTTP 500 is a symptom, not a root-cause diagnosis. Identify which server handled the operation and what it logged. Keep investigation evidence sanitized; do not delete persistent data or disable functionality simply to make the error disappear. Single-replica operation remains sufficient for this assignment. Application-level high availability is outside its 12–18-hour scope.

## Lifecycle and data ownership

| Operation | Expected boundary and risk |
| --- | --- |
| Delete/restart a pod | Controller recreates workload; mounted PVC normally remains. Container filesystem data can disappear. |
| Stop/start same Minikube profile | Local cluster disk normally remains; restart forwarding. Demonstrate behavior on your machine. |
| Remove a Helm release | Workloads removed; PVC behavior depends on templates, annotations, StatefulSet retention and ownership. Inspect rendered objects before assuming retention. |
| Terraform destroy / namespace deletion | Namespace deletion can remove PVCs even when a chart retains them. Reclaim policy may delete backing storage. |
| Delete PVC | Can delete the PV/backing data under a Delete reclaim policy; Retain still needs manual recovery. |
| `minikube delete` | Removes the local cluster and may remove its disks. Local PVCs do not guarantee recovery. |

Explain metadata stored in PostgreSQL versus Git objects and repository files on Gitea's PVC. Both are needed for a usable service. Retention is not backup, replication, or disaster recovery.

## Required runbook interface

Your scripts or documented commands must cover:

| Operation | Contract |
| --- | --- |
| Start | Start the chosen profile with Docker driver and documented Kubernetes/resources; verify readiness |
| Deploy | Check target, initialize Terraform, bootstrap referenced Secrets safely, plan and apply |
| Health | Inspect nodes, pods, PVCs, Services, events, Helm releases and functional endpoint |
| Access | Establish local web/Git access; document Windows URL and process lifetime |
| Logs | Select application/database, namespace and time window without leaking secrets |
| Test persistence | Create marker, collect baseline, recreate pods, stop/start, compare real data |
| Stop | Stop only the named profile, preserving its disk |
| Destroy | Display target and data-loss consequences, require confirmation, explain PVC/PV retention, then remove resources in dependency order |

Troubleshoot wrong context before mutation; resource pressure via events/requests; image failures via image references and pull events; crashes via current/previous logs; database authentication via Secret key wiring and role initialization; DNS via Service and endpoints; Windows access via the WSL boundary. Avoid printing secret values during diagnosis.
