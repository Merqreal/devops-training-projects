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

Run this gate **after deployment and persistence verification**, against the **final Terraform-deployed Gitea environment** and configuration you submit. A reviewer must see a successful end-to-end result before DEVOPS-001 is complete. Healthy Pods or an accessible home page cannot substitute for this test.

1. Using the explicit context and namespace from [command conventions](#command-conventions), confirm that Gitea and PostgreSQL Pods are Ready, inspect their Services and Ready endpoints, and verify connectivity through the intended paths. Check Gitea through your documented local access method and authenticated PostgreSQL connectivity from the application network path. A Service existing is not evidence of reachability; keep PostgreSQL internal rather than exposing it to your workstation.
2. Open the documented Gitea URL in the Windows browser. Log out of any administrator account and log in as a **normal, non-administrator user**; provision that user safely first if necessary.
3. In the web interface, create a new, uniquely named **empty** repository owned by that user. Do not initialize it with a README. Copy its advertised **HTTP or SSH clone URL** without credentials; check the reachable host, port and chosen transport.
4. From a new working directory in the local WSL development environment, use the example below. Replace the placeholder URL with the copied URL; for SSH, replace the entire value with the advertised SSH URL. Authenticate using a prompt, credential helper, or SSH agent. Configure your local Git author identity if needed.

Run **one command at a time**, immediately record its exit status with `echo "$?"` before executing the next command, and stop to investigate any nonzero result. Record each command and its result, not just the last exit status of the block. These examples use the explicit test branch `functional-check` rather than relying on the repository's default branch.

```bash
GITEA_REPOSITORY_URL='http://localhost:3000/USER/REPOSITORY.git'
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

A warning that the new remote repository is empty is expected. Use unique local directory names if these already exist; do not overwrite an earlier attempt.

5. Refresh the repository in the browser and select `functional-check`. Open the pushed commit and `verification.txt`; compare the full commit SHA and file content with the local results. Capture sanitized evidence showing the signed-in user, repository, branch, commit, and file. Exclude tokens, credential-helper contents, cookies, and authentication headers.
6. Return to the parent working directory, clone that branch into a **fresh directory**, and verify the same commit SHA, file content and checksum. Record exit statuses for these commands too:

```bash
cd ..
git clone --branch functional-check "$GITEA_REPOSITORY_URL" final-functional-check-fresh
git -C final-functional-check-fresh rev-parse HEAD
cat final-functional-check-fresh/verification.txt
sha256sum final-functional-check-fresh/verification.txt
```

7. Submit a dated expected-versus-actual record: final configuration/submission SHA, Pod/Service reachability checks, normal-user browser login and repository creation evidence, credential-free clone URL, command transcript with exit statuses, full commit SHA, file checksum, browser confirmation, and fresh-clone comparison. Preserve any failed attempt, its investigation and correction, and a successful repeat of the complete workflow.

**Completion gate:** normal-user login, repository creation, clone, commit, push, browser confirmation and the fresh-clone comparison must all succeed. Any earlier failure must be investigated, corrected and successfully retested. Do not mark DEVOPS-001 complete while a failure remains unresolved. Single-replica operation remains sufficient; advanced availability work is outside its 12–18-hour scope.

### Investigating a rejected push or internal-hook authentication error

A real reviewer test reported the following client failure (the `main` branch below belongs to that incident, not the example test branch):

```text
remote: error: Internal Server Error Decoding Failed
! [remote rejected] main -> main (pre-receive hook declined)
```

The corresponding Gitea server log recorded an internal hook request and authentication rejection. The repository path is anonymized here:

```text
POST /api/internal/hook/pre-receive/USER/REPOSITORY
403 Forbidden @ private.authInternal
```

Investigation found that the running web server and Git hook both referenced `/data/gitea/conf/app.ini`, but the file's modification timestamp was later than the web process's startup time. This is consistent with a **possible difference in the internal authentication token loaded by the long-running server and the later hook process**. Matching paths and timestamps alone do **not** establish which values were loaded or prove the exact root cause. This incident is supplied reviewer evidence, not a failure reproduced during portal authoring.

- Correlate the push timestamp, repository, serving Pod/container and restart history with Gitea current/previous logs using the [diagnostic commands](#command-conventions). Inspect the internal pre-receive HTTP response and authentication message; a generic client decoding error alone does not identify the cause. Check PostgreSQL logs, endpoints and storage events where relevant.
- Inspect the web process's configured path and the repository hook's Gitea invocation, including any `--config` argument, and confirm the actual file/mount they resolve to. A shared pathname does not prove identical file contents across containers or over time. Compare the **web process startup time**, not merely Pod creation, with file modification metadata and the deployment/change timeline.
- Trace `[security] INTERNAL_TOKEN` to its persistent authoritative configuration or Secret reference, including chart initialization, mounted configuration and environment-derived overrides. Investigate whether startup or later deployment changes regenerated or rewrote configuration after the server loaded it. Assess consistency locally through the documented secret-handling workflow; record only non-secret findings. Do not publish the token, full configuration, process environment or secret-bearing command arguments. Consult the [Gitea 1.27 security configuration contract](https://docs.gitea.com/1.27/administration/config-cheat-sheet/#security-security), checked on 2026-10-21.
- Correct the demonstrated configuration issue through Terraform, Helm, or your documented deployment/bootstrap workflow, then perform any required controlled rollout so the server and hooks use the intended persistent configuration. Preserve evidence supporting the correction; recovery alone does not retrospectively prove the original hypothesis. Do not disable Git hooks, delete repository data, remove LevelDB lock files, or regenerate secrets blindly.
- Repeat the **entire final functional verification**, including normal-user login, new repository, clone, commit, push, browser confirmation and fresh clone. Keep both the failed observation and the successful retest with sanitized server-side evidence.

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
