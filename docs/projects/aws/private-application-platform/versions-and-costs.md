# Versions, costs and upstream contracts

## Verification status

Documentation and the AWS Load Balancer Controller **3.6.1** chart archive were inspected on **2026-10-27**. This is a **source-checked starting baseline**, not an AWS-deployed compatibility matrix. No account discovery, regional price API query, Terraform execution against AWS, Kubernetes deployment, domain registration or runtime test was performed during assignment authoring. Current eu-west-1 unit prices have **not** been verified here; learners must obtain dated regional quotes before approval.

## Version contract

| Component | Starting pin / required selection | Evidence required before deployment |
| --- | --- | --- |
| Terraform CLI | **1.13.3** | Explicit CLI constraint/tool pin; [tagged release](https://github.com/hashicorp/terraform/releases/tag/v1.13.3) and support/advisory review |
| AWS provider | **hashicorp/aws 6.18.0** | [Tagged EKS resource contract](https://github.com/hashicorp/terraform-provider-aws/blob/v6.18.0/website/docs/r/eks_cluster.html.markdown), exact constraint/checksums in provider lock; verify selected EKS/access/add-on features |
| Kubernetes provider, if used | **hashicorp/kubernetes 2.38.0** | [Versioned provider authentication/staging contract](https://github.com/hashicorp/terraform-provider-kubernetes/blob/v2.38.0/docs/index.md); explicit target, separate management lifecycle |
| Helm provider, if used | **hashicorp/helm 3.0.2** | [Tagged configuration](https://github.com/hashicorp/terraform-provider-helm/blob/v3.0.2/docs/index.md); object-form Kubernetes configuration and explicit target |
| Helm CLI | **3.19.0** | [Helm documentation](https://helm.sh/docs/); record exact installed version and compatible APIs |
| EKS Kubernetes | **1.35** starting minor | Recheck [EKS standard-support calendar](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html) and eu-west-1 availability immediately before planning; use a standard-support minor, never extended support for this lab |
| kubectl | **1.35.0** starting patch with the above minor | Record an exact security-reviewed patch and [supported version skew](https://kubernetes.io/releases/version-skew-policy/); review any replacement with the reviewer |
| AWS Load Balancer Controller | Chart **3.6.1**, application **v3.6.1** | [Versioned chart package](https://aws.github.io/eks-charts/aws-load-balancer-controller-3.6.1.tgz), [release](https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases/tag/v3.6.1), matching CRDs/IAM contract; do not equate an unversioned chart with this pin |
| CoreDNS, kube-proxy, VPC CNI, identity/CSI add-ons as selected | Exact compatible versions selected for the chosen EKS minor | `describe-addon-versions`, architecture/support review, recorded add-on versions and image identities; include their footprint in two-node capacity |
| Node image and all application/platform images | Exact node AMI/release plus immutable image digests | Regional AMI/architecture, all registry paths, successful private pulls; no guessed AMI IDs, public-registry assumptions or floating `latest` |
| AWS CLI v2, Docker and diagnostic tools | Exact patches recorded in the learner version manifest | Current supported tooling; availability of the verification API fields/commands and output comparison |

These pins establish reproducible source inputs; they are not a mandate to keep vulnerable patches. If unavailable, insecure or incompatible, propose exact replacements with official release/support citations, a compatibility plan, cost impact and reviewer agreement **before applying**. Commit provider locks and chart dependencies/locks where applicable. Pin the application chart too, even when learner-authored. Do not change unrelated portal dependencies.

The inspected controller package's `Chart.yaml` maps chart 3.6.1 to v3.6.1. Its values include image source/tag, service-account configuration, cluster name, region, VPC ID and optional service integrations. Its default image source is public ECR: verify your private image path rather than assuming it is reachable. Inspect the chart, render privately and review CRD handling for the exact version. Official [versioned controller IAM policy](https://github.com/kubernetes-sigs/aws-load-balancer-controller/blob/v3.6.1/docs/install/iam_policy.json) is an upstream capability reference, **not** blanket approval to grant every optional action.

For isolated EKS installations without NAT, optional WAF, WAFv2 and Shield integrations may need explicit disabling. The inspected **3.6.1** chart's `values.yaml` leaves their values unset and documents enabled controller defaults; its `templates/deployment.yaml` emits the corresponding flags when given explicit Boolean values. Those defaults can cause reconciliation failures when optional service APIs are unreachable. The [upstream isolated-cluster installation requirements](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/deploy/installation/#additional-requirements-for-isolated-cluster) call for disabling these integrations. For this pinned chart, the relevant Helm values are:

```yaml
enableWaf: false
enableWafv2: false
enableShield: false
```

These are targeted chart inputs, not a complete controller configuration. Additional IAM permissions do not repair an unreachable API and are not necessarily the right response to such failures. Inspect controller logs, render the selected chart and confirm the effective flags. Recheck keys, defaults and isolated-cluster requirements whenever changing releases; do not assume they remain unchanged.

## Design contracts to inspect

| Concern | Official source and learner responsibility |
| --- | --- |
| No-NAT paths | [EKS private clusters](https://docs.aws.amazon.com/eks/latest/userguide/private-clusters.html), [ECR VPC endpoints](https://docs.aws.amazon.com/AmazonECR/latest/userguide/vpc-endpoints.html): derive caller-by-caller dependencies, including registry/layers, controller APIs, image bootstrap and private DNS; verify your selected identity and add-ons |
| API separation | [EKS cluster endpoint](https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html): distinguish private Kubernetes API access, optional constrained public management access, AWS management APIs and administrative network reachability |
| Pod credentials | [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html), [IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html): select supported SDK/agent/endpoint paths, narrowly bound trust and prevent privileged node-role fallback |
| Controller integration | [Ingress annotations and IngressGroup](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/ingress/annotations/), [security groups](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/deploy/security_groups/): inspect the corresponding tagged release for your pin; review shared-route trust, merged/exclusive settings, listener/CIDR behavior and backend reachability |
| Remote state | [S3 backend and locking](https://developer.hashicorp.com/terraform/language/backend/s3): use the approved existing backend with an isolated key, supported locking and restricted state/lock access; document recovery and residual secret exposure |
| DNS and TLS | [Route 53 public zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html), [registrar delegation](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-name-servers-glue-records.html), [Alias to ALB](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-elb-load-balancer.html), [ACM DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html): control the real domain and authoritative zone, validate certificates and define retained DNS ownership |
| Kubernetes isolation | [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/), [NetworkPolicies](https://kubernetes.io/docs/concepts/services-networking/network-policies/), [Helm charts](https://helm.sh/docs/topics/charts/): make reusable app inputs, constrain operators and verify enforcement, not just object existence |

## Cost worksheet and approval

**$20–30 is a target for total incremental AWS expenditure, not a guaranteed cap.** A continuously running EKS platform is incompatible with that target. Complete design, code, image builds and external approvals before beginning a billable lab. Prefer a **24–48-hour deployment window** only if the full estimate fits; price both durations and justify your selected shorter window if endpoints or other charges make 48 hours exceed the target. Do not assume a full 48 hours is affordable.

For every row, record **eu-west-1 unit price, currency, date/source, quantity, billing unit/minimum, usage assumption, estimated subtotal and teardown/retention owner**. Use [AWS Pricing Calculator](https://calculator.aws/), official service rates and your approved account billing view. Do not substitute another region's examples, promotional credits, Free Tier or shared discounts for the gross incremental estimate. Include uncertainty, billing lag, tax/FX treatment where applicable, and an explicit contingency.

| Charge | What the estimate must include | Pricing source |
| --- | --- | --- |
| EKS | One cluster, standard-support cluster hours from creation through deletion; avoid extended-support rates | [EKS pricing](https://aws.amazon.com/eks/pricing/) |
| Workers and disks | Two t3.small node-hours, CPU-credit exposure under chosen credit mode, root EBS type/size/retention and any extra volumes/snapshots | [EC2 On-Demand](https://aws.amazon.com/ec2/pricing/on-demand/), [EBS](https://aws.amazon.com/ebs/pricing/) |
| ALB | One ALB-hours, LCU/usage assumptions and all applicable public IPv4 address-hours | [ELB](https://aws.amazon.com/elasticloadbalancing/pricing/), [VPC](https://aws.amazon.com/vpc/pricing/) |
| Private connectivity | Every interface endpoint per provisioned AZ/hour, data processed, gateway-endpoint pricing, cross-AZ paths and optional administration connectivity | [PrivateLink](https://aws.amazon.com/privatelink/pricing/), [VPC](https://aws.amazon.com/vpc/pricing/) |
| Registry | Private ECR image storage, transfer and scanning mode if enabled; include mirrored platform images | [ECR](https://aws.amazon.com/ecr/pricing/) |
| Logging | Selected cluster/application/controller log ingestion, retention/storage and any query/metric charges | [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/) |
| Domain, DNS and certificate | Hosted-zone billing units/minima, queries, selected certificate type/validation model, full registration charge if buying a domain, renewal and retention costs | [Route 53](https://aws.amazon.com/route53/pricing/), [ACM](https://aws.amazon.com/certificate-manager/pricing/) |
| State and extras | Incremental S3 requests/storage/version retention, KMS if used, secrets, transfer, backups, management services and every other provisioned item | Respective official regional service pricing |

Use `quantity × measured/estimated billable duration × unit rate`, plus storage/request/LCU/transfer terms and one-time charges. Do not prorate a new annual domain registration into a tiny hourly estimate or hide its cost outside the lab total. A domain purchase can consume much of the target; use an already controlled approved domain where appropriate. Report ongoing registration/zone/backend charges separately **as well as** their incremental lab charges, and state whether they are excluded as pre-existing baseline costs with reviewer agreement.

Approval sequence: **design/cost approval → Terraform plan → review/approval of actual plan → apply** for each required stage. Set a named cleanup owner and a teardown deadline before applying. If the costed topology cannot meet the target, shorten the window or seek explicit revised approval; do not silently remove required security endpoints or change the required node topology. Optional RDS requires its own incremental estimate and approval; no baseline NAT, WAF or Aurora costs are necessary.

AWS Budgets/alerts can help detect overruns but are **not hard spending caps**; data and alerts lag. See [Budgets behavior](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html). A boundary, naming convention or tag cannot restrain an unrestricted administrator from changing or bypassing it. Budget discipline depends on approved scope, prompt teardown and reconciliation.

## Lifecycle and cost closure

1. Prepare the account/ownership inventory, design, pins, domain decision and full cost worksheet; obtain approval.
2. Plan, review the actual stage plan and apply only after approval; verify foundation, workloads, browser HTTPS, authorized/unauthorized networks and reusable onboarding.
3. Save sanitized evidence before the deadline. Remove applications/Ingress cloud resources with their controller still operational, then destroy ephemeral stages in reviewed dependency order.
4. Reconcile service inventories, orphaned resources, stale DNS/certificates and approved retained items using [teardown checks](verification.md#9-destruction-orphan-inventory-and-actual-charges). A deleted Terraform state entry does not prove an AWS object disappeared.
5. Record actual incremental costs once billing is available, compare with the estimate and document variances. Until then record a dated pending action and owner. Registration is not recreated/destroyed per run; document registrar auto-renewal, hosted-zone ownership and ongoing costs explicitly.

Do not delete a shared backend, an existing organization's infrastructure or unrelated DNS records as part of cleanup. Retained assets must be intentional, approved and visible in the final report, not concealed by an apparently empty Terraform state.
