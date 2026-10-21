# Reviewer notes — DEVOPS-001-HA

REVIEWER_ONLY_DO_NOT_PUBLISH

These notes and the separate learner handout are excluded from Pages, not confidential in Git. Never send this evaluation file as the learner brief. No reference deployment or fault drill has been run by the portal author; the strategy below is planned reviewer testing.

## Evaluation criteria

Evaluate this as an advanced follow-up of permanent DEVOPS-001, not a new catalog project. Its display identifier is DEVOPS-001-HA and its handout version is 1.0.0. The main project's required workload remains 12–18 hours; this follow-up estimates another 16–24 hours. Do not require HA implementation to accept the base assignment.

### Reviewer-controlled release procedure

The learner handout is [followups/DEVOPS-001-HA.md](followups/DEVOPS-001-HA.md). Store it outside `docs/`; never add a hidden URL, nav item, catalog entry, include, site asset, search entry or client-side unlock for it. There is no account, progress store, or automatic eligibility check. This is a human release gate using the existing reviewer publication boundary.

1. Review all baseline milestones at an immutable submission SHA, including the final ordinary-user browser workflow. Verify the functional test was attempted and passed after any corrections. A failed-only attempt does not satisfy base completion.
2. Keep an eligibility/release record in the team's existing private review channel or local review records, outside the portal: base ID and assignment version, submission SHA, timestamped functional-test evidence reference, initial failure/retest references if applicable, baseline decision, reviewer, decision date, recipient, and follow-up handout version. Record `eligible` only after base completion and the successful final gate are demonstrated. Record `not eligible` and missing gates otherwise. Do not commit personal review records here.
3. For an eligible learner, provide **only** the learner handout through the team's agreed direct handoff channel (for example as an attached Markdown file). Inspect the artifact before sending; it must contain the outcome-based brief, not this evaluation document or any other reviewer notes. Do not copy the directory wholesale. The handout's HTML exclusion marker may remain: it warns against adding the artifact to Pages.
4. Record the release date and handout version in the same review record. A later handout revision requires an explicit updated handoff. No website deployment is needed for an individual release.

Repository readers can inspect both files before eligibility. This procedure controls when reviewers assign the work; it cannot prevent public-source discovery. If actual confidentiality is required, maintain the handout in genuinely private storage instead. Never claim nav omission is authorization or access control.

### Acceptance checklist

- [ ] Base accepted SHA, final successful functional evidence and manual release record exist.
- [ ] Incident explanation distinguishes observed failure, inferred cause and any unexecuted reproduction.
- [ ] Versioned Gitea/chart contracts support the selected queue, sessions, caching, storage and enabled features.
- [ ] Two concurrent application replicas serve the same data through a stable Service with correct readiness.
- [ ] Session continuity and fresh login are verified across both serving replicas; consistent shared security material is referenced safely.
- [ ] Shared Git files use a compatible concurrent filesystem and permissions; old/new commits and checksums agree after each test.
- [ ] Queue-dependent work completes; no continued LevelDB contention or silent loss hidden by restarting Pods.
- [ ] Each application replica is independently targeted for loss; the survivor serves all required operations before replacement readiness.
- [ ] Database promotion is automatic, uses a different instance, and updates a stable writable-primary endpoint without Gitea configuration changes.
- [ ] The old database primary is fenced or otherwise prevented from divergent writes, later rejoins as a follower, and replication returns to healthy.
- [ ] Acknowledged Git and independent database markers survive; new application/database writes succeed after recovery.
- [ ] Budgets, retries, outages, timestamps, primary identities and actual limitations are recorded accurately.
- [ ] Terraform/Helm ownership, migration/backup/rollback, chart pins, provider locks and image digests are reproducible without undocumented configuration edits.
- [ ] Secret exposure and all remaining shared dependencies/failure domains are described; no training-workstation test is called production/node HA.

Any failed mandatory checklist item blocks follow-up completion, not already-earned baseline completion. Unexecuted drills remain unverified; descriptive diagrams cannot substitute for failure evidence.

## Common failure modes

The supplied incident suggests multiple Gitea processes opening one queue database directory. LevelDB is an embedded store with process ownership/locking; sharing its bytes does not turn it into a multi-process queue server. Verify both workloads' effective settings, mounts, paths, process overlap and logs. Do not conclude that every Git decoding error has this cause: inspect the request's actual server-side failure and database/backend status.

Moving each process's queue to a separate local path may hide contention but does not fulfill the distributed-queue requirement. Removing the lock file while a process holds the database, disabling locks or deleting the shared queue risks data loss and is not an accepted repair.

The chart 12.7.0 archive was inspected on 2026-10-21, including Chart.yaml, values.yaml and templates/gitea/config.yaml. Its multi-replica assertions reject the default first access mode ReadWriteOnce and constrain local indexers and scheduled Git GC. Passing chart rendering is only a prerequisite; it does not prove runtime integrity. Do not bypass assertions or assume the chart's optional legacy-image dependencies are available or maintained.

Kubernetes ReadWriteOnce means mounting by one node, not necessarily one Pod. Two same-node Pods may mount it and still conflict at the application layer. ReadWriteMany permits a mount pattern, not replicated storage or safe arbitrary concurrent writes. Confirm actual storage capabilities and Git-operation consistency rather than editing the label alone.

Other discriminating failures include local sessions or differing security keys causing cross-replica logouts; per-Pod repositories producing missing commits; local index databases or concurrent maintenance creating new locking hazards; role-blind database Services routing writes to followers; two primaries accepting writes after recovery; and bootstrap migrations overwriting accepted baseline data. Require explicit data ownership and recovery evidence for each component.

An ordinary port-forward through a Service selects a Pod and does not provide connection failover when that target disappears. Require a stable test access path through the Service that does not pin the experiment to the failed Pod. Treat a forwarding reconnection as a measured client-path interruption, not transparent application HA. Fresh connections and bounded retries may be appropriate, but cannot be relabeled zero downtime.

## Expected technical explanations

Ask the learner to distinguish queue coordination from repository file sharing; session storage from shared cryptographic identity; cache invalidation from persistence; primary election from replication; failover from restarting the same primary; fencing from liveness probes; acknowledged durability from an optimistic RPO; and a replica endpoint list from actual requests served by both Pods.

Require an explicit inventory of single-instance queue/cache services, storage servers, access proxies, control plane, local PV backing disks, Docker and the workstation. Explain that completing the required application/database drills supports a bounded Pod-resilience claim. A remaining single-point backend or one host prevents an unqualified end-to-end/node-HA claim even when the challenge's required drills pass.

## Reference validation strategy

Use architecture families as review criteria, not a copied deployment recipe: multi-process Gitea with compatible shared state, concurrent repository filesystem semantics, a distributed queue service, and PostgreSQL managed failover with a role-aware write endpoint. Accept any supported pinned selection satisfying every gate. PostgreSQL core replication alone does not supply automated failure detection and election. A compatible operator/manager must own promotion and recovery; for an operator, inspect CRD installation order, Helm ownership and Terraform-managed cluster resources.

1. Inspect the immutable baseline and follow-up SHAs, toolchain, scripts, secrets handling, diagram, version citations and state ownership. Establish safe cluster targets, backup and rollback before any drill. Do not execute unreviewed fault commands.
2. From documented prerequisites, validate Terraform, render learner Helm configuration privately, provision, inspect secret references without dumping their values, verify actual storage/backend compatibility, and obtain a no-drift baseline.
3. Create a normal-user test repository, push a uniquely named file and record full SHA/checksum, database marker, roles, Pod UIDs, readiness, Service endpoints and timestamps. Verify traffic reaches both application processes without publishing sessions or credentials.
4. Target application Pod A. Observe its loss and requests served by B during the degraded interval, including an existing browser session, separate fresh login, browse, new push and fresh clone. Require evidence before a replacement becomes Ready; agree on a safe extended observation window if necessary. Check queue work and content, recover, then repeat with B as the failed target.
5. Restore full application topology before the separate database drill. Record current primary and lag, inject a bounded fault into that primary, observe automatic promotion of a different instance and endpoint routing, and verify marker/data integrity and new application writes without manual hostname changes.
6. Observe former-primary recovery as a non-writable follower, check replication and two-application-replica functionality, and inspect for unexplained Terraform drift. Distinguish intentional operator-managed runtime role changes from undeclared configuration.
7. Compare measured interruption and durability with the agreed budgets. Retain failed observations and successful reruns. Mark every gate passed, failed or not executed. Review teardown and data retention without demanding destructive PV or host-loss tests.

### Upstream sources checked on 2026-10-21

- [Gitea v1.27.0 local queue implementation](https://github.com/go-gitea/gitea/blob/v1.27.0/modules/queue/base_levelqueue.go) and [versioned example configuration](https://github.com/go-gitea/gitea/blob/v1.27.0/custom/conf/app.example.ini).
- [Gitea 1.27 configuration reference](https://docs.gitea.com/1.27/administration/config-cheat-sheet/) and [chart 12.7.0 package](https://dl.gitea.com/charts/gitea-12.7.0.tgz); the downloaded package, not an unversioned values example, informed the chart assertions above.
- [LevelDB concurrency model](https://github.com/google/leveldb/blob/main/doc/index.md#concurrency); Gitea's Go LevelDB dependency and its own error path still govern diagnosis on the selected build.
- [PostgreSQL 18 failover](https://www.postgresql.org/docs/18/warm-standby-failover.html) describes promotion, old-primary isolation and return to redundancy. [CloudNativePG 1.27 failover documentation](https://cloudnative-pg.io/docs/1.27/failover/) is one example manager contract, not a prescribed or compatibility-tested selection.
- [Kubernetes 1.34 persistent volume access modes](https://v1-34.docs.kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes).

Only documentation/package inspection and portal checks were performed by the author. Learner runtime compatibility, Kubernetes HA and database failover remain demonstrations to be executed during review.
