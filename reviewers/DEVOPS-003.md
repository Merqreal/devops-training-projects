# Reviewer notes — DEVOPS-003

REVIEWER_ONLY_DO_NOT_PUBLISH

This file is excluded from the generated site. Git repository readers can still access it; exclusion is not confidentiality or an access-control mechanism. Do not include it in learner pages, search, assets or handouts. This is a planned review strategy, not a deployed reference implementation. No AWS/Kubernetes runtime experiment was performed by the author.

## Evaluation criteria

Use blocking mandatory gates rather than giving optional work compensating marks. The project must be a reusable platform, not a tailored one-app Terraform demo. Demand a real final cleanup inventory and preserve failed tests in the evidence. Review a fixed learner SHA and actual plans privately before permitting any apply; design approval by itself is insufficient.

| Review area | Acceptance evidence / blocking condition |
| --- | --- |
| Shared Sandbox scope | Before/after inventory, approved account and region, ownership prefix/tags, no unrelated imports, modifications or cleanup; reject claimed administrator-proof isolation |
| Remote state | Approved S3 key isolation, access/encryption/version recovery, functioning locking and sensitive artifact handling; no takeover of the existing backend |
| Modular delivery | Clear infrastructure/platform/application stages, explicit provider targets, reproducible dependency ordering and ownership inventory; no controller/Terraform dual ownership |
| VPC | Exactly the intended public/private subnet pairs in two AZs, valid nonoverlap and routing, no NAT Gateway/instance or public-worker shortcut |
| Private dependencies | Caller/endpoint/DNS/policy/SG matrix, bootstrap image paths and actual private image pulls; a list of endpoint names alone fails |
| EKS | One cluster, one managed group, two actual Ready t3.small nodes, standard-support version and functioning compatible core add-ons; capacity budget includes platform overhead |
| Identities | Trust and permission documents reviewed for every role, service-account binding, allowed and denied evidence; no provisioned AdministratorAccess or administrator credential injection |
| Applications | Two independent namespaces/images/build identities/configuration/service accounts and complete reusable workload contracts, browser UI and functional health |
| Ingress | One owned internet-facing ALB, 443 only, valid TLS, correct targets/rules, no second ALB or public NodePort path |
| Corporate-only access | Private review of actual approved CIDRs across all attached SGs, corporate success and a correctly interpreted external transport denial; do not accept application HTTP 403 as network denial |
| Domain control | Actual ownership/permission, registrar delegation, authoritative Route 53 records, ACM validation and trusted browser chain; no corporate DNS dependency or unauthorized delegation change |
| Reuse | Before/after foundation identities and plans, application B onboarded without new shared infrastructure, B stays functional while A is updated and removed |
| Cost | Dated regional quantities/rates, endpoint-AZ hours and all incidental charges, deadline/cleanup owner, $20–30 target with contingency or explicitly reviewed deviation |
| Teardown | Controller reconciliation completed before its infrastructure disappears, service inventories clear or approved retention listed, stale DNS handled and billing follow-up owned |

### Security and IAM review checklist

- Review human SSO role separately from the Terraform execution role. A constrained runtime architecture does not constrain the existing human administrator. Document any provisioning-role exception and its consequences; do not imply a permissions boundary or budget can resist that unrestricted session.
- Read every trust policy and managed-policy default version/inline document, not just attachment names. Check service principals, OIDC audience/subject or Pod Identity association scope, confused-deputy conditions, namespace/account binding, role passing and approved resource scopes. Justify wildcard Describe actions where the API cannot scope them; reject wildcard administrative writes.
- Inspect node/control-plane roles and CNI separation, plus controller and optional build roles. Upstream controller policy supports optional integrations; unused WAF/Shield behavior is not a reason to grant unreviewed broad privileges. Validate required operations after policy reduction rather than claiming a policy diff proves least privilege.
- Verify actual Pod credential resolution. No-role apps must not inherit a privileged node profile via IMDS; restrictive application IAM is ineffective if node credentials or human tokens remain reachable. Test harmless allow/deny actions under the real workload identity without disclosing credentials.
- Check RBAC, service-account token use, namespace/config/secret boundaries and enforced network policies. IngressGroup/shared routing assumes trusted actors: unauthorized namespace users must not be able to hijack another app's route or widen shared access. Namespaces alone are not strong tenancy.
- Inspect all ALB-attached groups and backend groups. Shared-group annotations and custom SG ownership can change which CIDR settings are actually enforced. Neither a correct input variable nor an Ingress annotation substitutes for observed AWS rules and both-network tests. Include IPv6/bypass paths and default Service/controller behaviors.
- Do not request raw Secrets, state, environment dumps, real corporate CIDRs or sensitive identifiers in published evidence. Review necessary originals privately and retain only safe references in the assessment.

### Cost-control and domain review

Cost the whole live window, endpoint count multiplied by AZ placement, ALB/public addresses, root disks, registry scans/storage, CloudWatch ingestion/retention, transfer and any chosen management connectivity. Examine t3 CPU credit mode and optional storage/backup/secret charges. A 48-hour allowance is not automatically affordable; require the learner's calculation and shorten runtime when needed. Reject free-tier/credits as the only explanation of the budget and reject a continuously running platform within this target.

Confirm existing-domain authority before approving NS changes. A new Route 53 zone does not buy a domain, and an empty new zone can break existing services if delegation changes blindly. Domain purchase/renewal is annual and persistent; it may consume the entire target. Prefer approved existing ownership where possible and record continuing zone/backend costs. Do not let a lab destroy registered domain ownership or unrelated records. Actual charges may be delayed: a pending reconciliation with a named owner/date is honest; a claimed zero cost from an empty query is not.

## Common failure modes

- A community EKS module silently creates NAT, extra groups or unintended public networking. Review actual plans and service inventory, including defaults and IPv6, not just module inputs.
- Workers cannot bootstrap because the Kubernetes API is unreachable or necessary private service paths/DNS are missing. Distinguish the Kubernetes endpoint, EKS management API, identity exchange and controller dependencies. Avoid adding every possible endpoint blindly: require a justified functional/cost matrix.
- ECR auth succeeds but layers fail, public-registry platform images cannot pull, or first-use caching still requires internet. Inspect registry path, S3/private connectivity and actual new-Pod events. An app cached on a node is weak evidence of reproducible bootstrap.
- Controller discovery relies on metadata it cannot access, SDK uses the wrong identity/service endpoint, or optional service calls fail despite unused features. Inspect selected chart version, region/VPC settings, image identity, policy and logs; accept functional evidence, not indiscriminate administrator grants.
- Two small nodes saturate memory/Pod IPs or rolling-update headroom. Require requests/allocatable accounting and events. Quietly changing instance type/count or leaving Pods Pending does not meet the baseline.
- Each namespace produces an ALB, or removal of one route removes the shared entrypoint. Require ALB ARN/identity comparisons through both onboarding and app-removal tests; count all owned VPC ALBs, not merely Ingress hostnames.
- An allowlist appears in Terraform but the ALB has another permissive SG or inherited shared configuration. Test the actual attached rules and network behavior. DNS failure or TLS error off-network does not prove CIDR enforcement.
- TLS is "tested" with insecure curl, a wrong SNI name, a duplicate nonauthoritative hosted zone, or registrar delegation left unchanged. Require ordinary browser trust and authoritative resolution for both apps.
- Terraform loses cluster/provider connectivity during cleanup, or the controller is removed before finalizers delete cloud resources. Require a designed staged teardown; never accept blind finalizer deletion or account-wide cleanup as a harmless fix.
- Terraform state is empty while ALBs, target groups, ENIs, snapshots, registry images, log groups, certificates or stale aliases survive. Use saved IDs and cross-service inventory, including untagged/controller objects and approved retained assets.

## Expected technical explanations

Ask the learner:

1. What remains stable when a third application is onboarded, and what inputs are application-specific? Show the evidence rather than just a reusable module name.
2. Which principal makes each AWS call? Which trust/permission path allows it, and how do you prevent the application using the human or node identity instead?
3. How do private nodes obtain every required image and API response without NAT? Which exact failures reveal DNS, TLS, IAM, routing or endpoint-policy problems?
4. How does administration reach the Kubernetes API, and why is an EKS interface endpoint not a substitute for that path? What extra cost does your management choice add?
5. Who owns each ALB object and when does deletion occur? How can users in a second namespace influence shared routing or security-group behavior?
6. Why do public DNS and an internet-facing ALB not imply public application access? What observations distinguish network blocking from a broken app?
7. How many endpoint-AZ hours and worker/cluster hours are in your estimate? What costs survive the deadline? Why are alerts not hard caps?
8. Which resources are deliberately retained, who owns them, and how will actual charges be reconciled? How did you prove no unrelated resources changed?
9. Where do secret values still appear even when Terraform variables are sensitive? How do you protect state, plans, Helm records, bootstrap and reviewer evidence?
10. What do two small workers fail to guarantee about availability, capacity and isolation?

## Reference validation strategy

1. Conduct a non-mutating design review: read the learner implementation/scripts, account inventory, approved domain authority, ownership/state/IAM matrices, pinned sources and regional estimate. Approve an execution window and safe targets before cloud changes. Do not turn this portal authoring task into an actual reference deployment.
2. When reviewing a learner lab, observe SSO/account/region guards and actual staged plans at the stated SHA. Review all create/update/delete/import actions and secret exposure privately. Require fresh approval for meaningful changes.
3. Observe approved deployment and independently compare AWS networking, EC2 addresses, EKS/group/add-on states, identities and private image events against the documented expected values. Empty or denied results are not affirmative evidence.
4. Test normal corporate browser/health access to both independent applications and corresponding unauthorized-network transport denial. Inspect authoritative delegation/records, certificate chain/names, all attached SGs, listener rules and target health. Retain safe evidence without real corporate-address disclosure.
5. Capture the one-cluster/one-group/two-worker/one-ALB inventory before B, after B and through updating/removing A. Review continuous B checks and its stable build/configuration. Test workload IAM/RBAC/NetworkPolicy behavior with harmless operations under the actual identities.
6. Observe the reviewed cleanup order while the controller and Kubernetes API remain operational. Compare independent post-destroy service inventory with saved identities and pre-lab resources; investigate all retained/orphaned billable objects before accepting closure. Approve any intentional domain/backend retention explicitly.
7. Record each criterion as passed, failed or not executed. Final engineering review can note billing reconciliation pending with an owner/date; cost reporting remains open until actuals are available. Optional RDS, if attempted, adds separate approval, private connectivity and instance/snapshot/secret cleanup evidence without altering baseline scoring.

Source references and author-verification limits are recorded in the public versions/costs page. This file deliberately provides assessment strategy and failure discriminators rather than a finished Terraform, IAM or Helm implementation.
