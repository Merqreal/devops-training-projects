# Verification and teardown

These are **learner-run diagnostics**, not an end-to-end implementation or commands executed by the portal author. No AWS or Kubernetes execution was performed while authoring. Use Bash, AWS CLI v2, jq, Terraform, kubectl, Helm, Docker, curl, dig and OpenSSL from your approved workstation/management path. Supply resource identities from your reviewed configuration and observed inventory; never guess IDs in a shared account. Most commands below are read-only; plan/apply, deployment, image push and destruction are explicitly separated by approval gates.

## 1 · Target, ownership and approval

Replace all `REPLACE_...` placeholders. Keep actual account identifiers, corporate CIDRs and full inventory private; publish sanitized evidence only. Examples assume one region and a distinct Terraform environment directory; adapt the directory to your design.

```bash
export AWS_PROFILE=REPLACE_APPROVED_SSO_PROFILE
export AWS_REGION=eu-west-1
export AWS_DEFAULT_REGION=eu-west-1
export AWS_PAGER=''
export PROJECT=REPLACE_UNIQUE_OWNERSHIP_TAG
export CLUSTER=REPLACE_CLUSTER_NAME
export NODEGROUP=REPLACE_NODEGROUP_NAME
export CONTEXT=REPLACE_REVIEWED_KUBECONFIG_CONTEXT
export VPC_ID=REPLACE_VPC_ID
export TF_ROOT=REPLACE_TERRAFORM_ENVIRONMENT_DIRECTORY
export EXPECTED_ACCOUNT_ID=REPLACE_APPROVED_ACCOUNT_ID
aws configure list
aws sts get-caller-identity
test "$(aws sts get-caller-identity --query Account --output text)" = "$EXPECTED_ACCOUNT_ID"
```

Stop on identity/region/target mismatch. A successful STS call merely identifies the session; it does not prove least privilege. Record pre-lab inventory and ownership tags, existing domain/zone/backend permissions, intended new resources and retention exceptions. Discover resources read-only through service inventories; do not import unrelated infrastructure. Verify quotas and current eu-west-1 standard support before selecting versions:

```bash
aws eks describe-cluster-versions --query 'clusterVersions[].{Version:clusterVersion,Status:versionStatus,StandardEnd:endOfStandardSupportDate}'
aws ec2 describe-availability-zones --query 'AvailabilityZones[].{Zone:ZoneName,State:State}'
aws ec2 describe-instance-type-offerings --location-type availability-zone --filters Name=instance-type,Values=t3.small
```

Expected: chosen minor is still in standard support and t3.small is offered in both chosen AZs. Record API date and support evidence rather than assuming the authoring baseline remains current. Keep the unique prefix/tag and actual resource IDs in a private inventory; tags alone cannot prove that all resources are owned or visible.

The version query uses `clusterVersions[].versionStatus` from the [current AWS CLI response structure](https://docs.aws.amazon.com/cli/latest/reference/eks/describe-cluster-versions.html), checked on 2026-10-27. Require `Status` to be `STANDARD_SUPPORT` for the selected minor and check `StandardEnd` against your deployment window; the older `status` field is deprecated.

Obtain design, domain and cost approval before creating resources. Then review the **actual** Terraform plan with the reviewer before applying each stage. Record approval against the source SHA, plan identity and intended account. A changed plan needs new review.

## 2 · Terraform, state and deployment stages

From the separate learner checkout, with approved backend access and secret inputs prepared:

```bash
terraform -chdir="$TF_ROOT" version
terraform -chdir="$TF_ROOT" fmt -check -recursive
terraform -chdir="$TF_ROOT" init -lockfile=readonly
terraform -chdir="$TF_ROOT" validate
umask 077
PRIVATE_PLAN=$(mktemp /tmp/devops-003-plan.XXXXXX)
terraform -chdir="$TF_ROOT" plan -out="$PRIVATE_PLAN"
terraform -chdir="$TF_ROOT" show "$PRIVATE_PLAN"
```

For first authoring, create/review the provider lock with `init` before requiring readonly mode. Full plans and `show` output can contain secrets; inspect locally, never commit them, and share only redacted summaries. Demonstrate the approved S3 bucket/key, encryption/versioning/access controls and working lock acquisition/contention on your own lab state. Do not test locking against another user's state or forcibly unlock an active operation.

**Apply gate:** only after the matching plan is approved may the learner execute `terraform -chdir="$TF_ROOT" apply "$PRIVATE_PLAN"`. No `-auto-approve`. Keep infrastructure/platform/application stages and provider connectivity reproducible; document which stages need an existing EKS API. After expected reconciliation, run `terraform -chdir="$TF_ROOT" plan -detailed-exitcode`: 0 means no changes, 2 means proposed changes and 1 means error. Capture the exit immediately; do not hide 2 in a generic success wrapper. Explain operator-managed status versus actual configuration drift. Securely dispose of saved plans according to the approved workstation policy.

## 3 · VPC, routes, service paths and private workers

```bash
aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --query 'Vpcs[].{Id:VpcId,Cidr:CidrBlock,Tags:Tags}'
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[].{Id:SubnetId,AZ:AvailabilityZone,Cidr:CidrBlock,PublicMap:MapPublicIpOnLaunch,IPv6:Ipv6CidrBlockAssociationSet,Tags:Tags}'
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID"
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$VPC_ID" --query 'NatGateways[].{Id:NatGatewayId,State:State}'
aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=$VPC_ID" --query 'VpcEndpoints[].{Id:VpcEndpointId,Service:ServiceName,Type:VpcEndpointType,State:State,PrivateDNS:PrivateDnsEnabled,Subnets:SubnetIds,Routes:RouteTableIds,Groups:Groups}'
aws ec2 describe-instances --filters "Name=vpc-id,Values=$VPC_ID" --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Type:InstanceType,Subnet:SubnetId,Private:PrivateIpAddress,Public:PublicIpAddress,IPv6:NetworkInterfaces[].Ipv6Addresses,Role:IamInstanceProfile,Metadata:MetadataOptions}'
```

Interpret the outputs: exactly four intended subnets across two AZs; public ALB route associations; private worker routes without internet/NAT shortcuts; no active NAT Gateway or NAT instance; two running t3.small workers with no public IPs or public IPv6 reachability. Include any approved private management resources separately. Check subnet auto-address settings **and actual instance/ENI addresses**, IGW/IPv6 routes and security groups.

For each required AWS service path, inspect endpoint DNS resolution from the actual private caller and service connectivity, endpoint state, endpoint SG rules, route associations and endpoint/IAM policies. Compare with your dependency matrix. An `available` endpoint is not proof that a Pod can use it. Separate ECR authorization from registry transport and S3 layers; include controller APIs, identity token exchange and image sources. Document how bootstrap works with no NAT, including any explicitly mirrored platform image. Successful image pulls are required runtime evidence, not inferred from endpoint names.

## 4 · EKS, nodes and core add-ons

```bash
aws eks describe-cluster --name "$CLUSTER" --query 'cluster.{Status:status,Version:version,Network:resourcesVpcConfig,Access:accessConfig,Role:roleArn,Logging:logging,Tags:tags}'
aws eks list-nodegroups --cluster-name "$CLUSTER"
aws eks describe-nodegroup --cluster-name "$CLUSTER" --nodegroup-name "$NODEGROUP" --query 'nodegroup.{Status:status,Types:instanceTypes,Scale:scalingConfig,Subnets:subnets,Role:nodeRole,Health:health,Resources:resources}'
aws eks list-addons --cluster-name "$CLUSTER"
aws eks describe-addon --cluster-name "$CLUSTER" --addon-name vpc-cni
kubectl --context "$CONTEXT" cluster-info
kubectl --context "$CONTEXT" get nodes -o wide
kubectl --context "$CONTEXT" get nodes -o json | jq -e '.items | length == 2 and all(.[]; any(.status.conditions[]; .type == "Ready" and .status == "True"))'
kubectl --context "$CONTEXT" -n kube-system get deployments,daemonsets,pods
kubectl --context "$CONTEXT" describe nodes
```

Expected: one owned cluster, one managed group, two Ready nodes of the required type in private subnets; inspect node provider IDs against EC2 inventory. Review fixed scaling bounds, compatible versions and health of VPC CNI, CoreDNS, kube-proxy, identity/CSI add-ons if selected, and controller deployment. For self-managed add-ons inspect their manifests/images instead of assuming they appear in `list-addons`.

Use `describe-addon` for each selected managed add-on and compare its pinned version to `describe-addon-versions` for the chosen Kubernetes minor. Inspect Pod/IP capacity, events, requests versus allocatable memory/CPU and rollout headroom. Record retention on cluster/controller/application log groups. Explain how your management process reaches the Kubernetes API independently of the EKS management API endpoint; do not expose nodes to make kubectl work.

## 5 · Registry, applications and functional health

Build and push images from your approved build environment using the documented ECR authentication method. Do not log ECR authorization tokens. The learner implements that workflow; the diagnostics below do not perform an image push or deployment.

Set application variables to your actual names. Repeat application-scoped checks for B using its independent namespace/image/configuration.

```bash
export ECR_REPOSITORY=REPLACE_OWNED_REPOSITORY
export IMAGE_TAG=REPLACE_IMMUTABLE_BUILD_TAG
export APP_NS=REPLACE_APPLICATION_A_NAMESPACE
export APP_DEPLOYMENT=REPLACE_DEPLOYMENT
export APP_SERVICEACCOUNT=REPLACE_SERVICE_ACCOUNT
aws ecr describe-repositories --repository-names "$ECR_REPOSITORY"
aws ecr describe-images --repository-name "$ECR_REPOSITORY" --image-ids "imageTag=$IMAGE_TAG" --query 'imageDetails[].{Digest:imageDigest,Tags:imageTags,Size:imageSizeInBytes}'
helm --kube-context "$CONTEXT" list -A
kubectl --context "$CONTEXT" get namespaces
kubectl --context "$CONTEXT" -n "$APP_NS" get deployments,services,pods,ingresses,serviceaccounts,configmaps
kubectl --context "$CONTEXT" -n "$APP_NS" rollout status "deployment/$APP_DEPLOYMENT" --timeout=180s
kubectl --context "$CONTEXT" -n "$APP_NS" get pods -o json | jq '.items[] | {Name:.metadata.name,Images:[.status.containerStatuses[]? | {Image:.image,Resolved:.imageID,Ready:.ready}],IP:.status.podIP}'
kubectl --context "$CONTEXT" -n "$APP_NS" get events --sort-by=.metadata.creationTimestamp
kubectl --context "$CONTEXT" -n "$APP_NS" get serviceaccount "$APP_SERVICEACCOUNT" -o yaml
kubectl --context "$CONTEXT" -n "$APP_NS" get networkpolicies
```

Compare the deployed image IDs/digests with ECR and the build artifacts. Observe a rollout with newly scheduled Pods pulling privately; record events and readiness without deleting node caches or inventing evidence. Inspect both Deployment specifications for distinct environment/config references, secret **names**, requests/limits, probes, runtime security and rolling updates; do not dump Secret objects or environment values. Verify effective RBAC and network-policy enforcement with permitted/denied connections in your own namespaces. The existence of a policy object alone does not prove isolation.

Open both applications from the corporate browser. Confirm distinguishable UI/build identifiers, configuration behavior and successful health endpoints. Use the documented health paths, not a guessed `/health` if your app exposes another path.

## 6 · Exactly one ALB, routing, targets and security groups

Discover the owned ALB by VPC, controller ownership and inventory, not simply by picking the account's first load balancer. Retain its ARN/DNS identity privately for the reuse test.

```bash
aws elbv2 describe-load-balancers --query 'LoadBalancers[].{Name:LoadBalancerName,Arn:LoadBalancerArn,Vpc:VpcId,Scheme:Scheme,Type:Type,DNS:DNSName,Groups:SecurityGroups,AZs:AvailabilityZones}'
export ALB_ARN=REPLACE_OWNED_ALB_ARN
export LISTENER_ARN=REPLACE_HTTPS_LISTENER_ARN
export TARGET_GROUP_ARN=REPLACE_APPLICATION_TARGET_GROUP_ARN
export ALB_SG_ID=REPLACE_ATTACHED_ALB_SECURITY_GROUP_ID
aws elbv2 describe-tags --resource-arns "$ALB_ARN"
aws elbv2 describe-listeners --load-balancer-arn "$ALB_ARN"
aws elbv2 describe-rules --listener-arn "$LISTENER_ARN"
aws elbv2 describe-target-groups --load-balancer-arn "$ALB_ARN"
aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP_ARN"
aws ec2 describe-security-group-rules --filters "Name=group-id,Values=$ALB_SG_ID"
```

Count ALBs in the **owned VPC**, including unexpected ones from application Ingress or LoadBalancer Services. Exactly one must be an active internet-facing application ALB spanning the public subnets. Inspect every attached SG (their rules combine), 443 listener/certificate, per-application rules, target groups/health and backend SG path. Use `describe-target-health` for every application target group; prove targets are the intended Pod IPs when IP mode is selected. Check controller logs and ingress events on mismatch.

No 80 listener or public management ports are needed. Effective application ingress must be 443 from the **approved CIDRs only**, with no IPv4/IPv6 anywhere rule or alternative public endpoint. Inspect backend ingress for intended ALB traffic rather than broad access. Repeat these checks after application B onboarding to catch merged or conflicting shared-ingress settings. Keep corporate addresses out of published evidence; reviewer inspection of the real allowlist happens privately.

## 7 · Domain ownership, ACM and corporate/unauthorized tests

```bash
export DOMAIN=REPLACE_APPROVED_CONTROLLED_DOMAIN
export APP_HOST=REPLACE_APPLICATION_A_HOSTNAME
export DEMO_HOST=REPLACE_APPLICATION_B_HOSTNAME
export ZONE_ID=REPLACE_APPROVED_HOSTED_ZONE_ID
export CERT_ARN=REPLACE_EU_WEST_1_CERTIFICATE_ARN
aws route53 get-hosted-zone --id "$ZONE_ID"
aws route53 list-resource-record-sets --hosted-zone-id "$ZONE_ID"
aws acm describe-certificate --certificate-arn "$CERT_ARN" --query 'Certificate.{Status:Status,Names:SubjectAlternativeNames,Validation:DomainValidationOptions,Expiry:NotAfter,InUse:InUseBy}'
dig NS "$DOMAIN"
dig +trace "$APP_HOST"
dig A "$APP_HOST"
dig AAAA "$APP_HOST"
curl --fail --show-error --connect-timeout 10 --max-time 30 "https://$APP_HOST/"
curl --fail --show-error --connect-timeout 10 --max-time 30 "https://$DEMO_HOST/"
openssl s_client -connect "$APP_HOST:443" -servername "$APP_HOST" -verify_hostname "$APP_HOST" -verify_return_error </dev/null
```

At the registrar, verify delegation matches the approved authoritative Route 53 zone, not merely that a duplicate zone exists. Keep proof of domain control/approval private. Check Alias records reference the correct ALB and hosted-zone target, DNS validation records are authoritative, certificate status is `ISSUED`, region matches the ALB and names cover both apps. From the corporate path, verify the certificate chain, hostname and validity without `curl -k`, plus both app UIs and health endpoints. A curl 0 or an OpenSSL handshake alone does not establish the right application content: inspect response, certificate verification result and browser trust.

Repeat the HTTPS commands from a genuinely unrelated external network without corporate VPN/proxy. Confirm DNS still resolves to the same intended ALB, then record timestamps, network context and the transport-denied result. Check A/AAAA address families as applicable. A bad certificate, unresolved DNS, broken application or HTTP 403 from a reachable app does not prove the ALB SG blocked that network. Correlate the negative result with inspected effective SG restrictions and simultaneous successful corporate tests. Record unexpected success as a failed security gate, fix through the declared workflow and retest both paths.

## 8 · IAM identities and reusability

```bash
export ROLE_NAME=REPLACE_OWNED_ROLE_NAME
aws iam get-role --role-name "$ROLE_NAME" --query 'Role.{Name:RoleName,Trust:AssumeRolePolicyDocument,Boundary:PermissionsBoundary,Tags:Tags}'
aws iam list-attached-role-policies --role-name "$ROLE_NAME"
aws iam list-role-policies --role-name "$ROLE_NAME"
aws eks list-access-entries --cluster-name "$CLUSTER"
aws eks list-pod-identity-associations --cluster-name "$CLUSTER"
kubectl --context "$CONTEXT" -n "$APP_NS" auth can-i --list --as="system:serviceaccount:$APP_NS:$APP_SERVICEACCOUNT"
```

Repeat IAM inspection for every platform role in your matrix. Retrieve each managed policy's default version and inline policy document locally; attached names alone are insufficient. Compare trust principals/conditions, permissions, resources and pass-role boundaries with the design. Inspect IRSA bindings if that mechanism is used instead of Pod Identity; verify supported SDK identity resolution and the required private token path. Access entries and RBAC privileges are distinct from AWS API privileges.

Use a small learner-authored, reviewed test under the **actual application service account**, with no copied human credentials: capture its AWS caller identity when access is intended, a narrowly scoped allowed action and a harmless denied read outside its scope. For apps needing no AWS role, demonstrate no usable AWS credentials/privileged node fallback and denied unauthorized Kubernetes access. Do not run an administrator CLI call and label it a Pod-identity test; do not dump metadata credentials. These are tests to implement, not evidence inferred from a role annotation.

Record VPC, cluster, node-group/node and ALB identities/counts after A is healthy. Introduce B through your reusable interface; compare before/after plans and identities and validate B's own image, namespace, service, route, hostname, environment, resources, account and configuration. Maintain repeated B HTTPS/health checks while rolling A to another build, then remove A through the declared application workflow. B must still show its original build/configuration without errors or replacement of shared infrastructure. Keep timestamped results and restore/redeploy A if needed for final evidence. Cloud objects for A must reconcile away without deleting B's routes/ALB. One hardcoded app with two aliases fails this gate.

## 9 · Destruction, orphan inventory and actual charges

Destruction is mandatory **for the learner**, after evidence collection and reviewer confirmation of ownership/retention. Do not execute this section as portal authoring. Confirm account/context/VPC again; show the exact plan/targets to the reviewer. No broad account cleanup or tag-based bulk delete script.

1. Remove ephemeral application DNS references and application resources in your dependency order. Remove shared Ingress/controller-managed AWS objects **while the controller, credentials, endpoints and cluster still work**. Wait for finalizer reconciliation and observe ALB/listener/target-group/SG deletion. Do not blindly remove finalizers to mask orphaned billable objects.
2. **ECR deletion checkpoint — before Terraform destruction:** inspect every lab-owned repository scheduled for deletion, including tagged and untagged images, for example with `aws ecr list-images --repository-name "$ECR_REPOSITORY" --filter tagStatus=ANY`. Compare its identity and contents against the approved ownership inventory. [ECR will not delete a non-empty repository](https://docs.aws.amazon.com/cli/latest/reference/ecr/delete-repository.html) unless content deletion is explicitly requested. Ensure Terraform can remove it: either explicitly delete only the approved training images first and verify the repository is empty, or obtain reviewer approval for a Terraform repository deletion configuration that explicitly permits removing its contents. Review that behavior in the selected provider version and destruction plan. Do not enable unrestricted deletion across repositories or apply content deletion to shared, pre-existing or unrelated repositories; stop and resolve any ownership ambiguity. Repeat for each repository rather than assuming the earlier application-A variable covers all images.
3. Remove Helm/Kubernetes platform resources and perform the reviewed Terraform destruction stages. From the appropriate environment roots, run `terraform plan -destroy` and review it; only then run `terraform destroy` with its confirmation prompt. Preserve retained domain/backend state in its separately documented ownership boundary. Do not destroy shared state infrastructure, unrelated hosted-zone records or registrations.
4. Verify intended state removals with `terraform state list` in each ephemeral state and perform independent AWS inventories. A successful destroy or empty state alone does not prove controller objects, retained volumes or DNS were removed.

Examples below are read-only follow-up inventories; substitute the saved IDs and compare to your pre-lab inventory:

```bash
aws eks list-clusters
aws elbv2 describe-load-balancers
aws elbv2 describe-target-groups
aws ec2 describe-network-interfaces --filters "Name=vpc-id,Values=$VPC_ID"
aws ec2 describe-vpc-endpoints --filters "Name=vpc-id,Values=$VPC_ID"
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$VPC_ID"
aws ec2 describe-volumes --filters "Name=tag:Project,Values=$PROJECT"
aws ec2 describe-addresses
aws ec2 describe-vpcs --vpc-ids "$VPC_ID"
aws ecr describe-repositories
aws logs describe-log-groups --log-group-name-prefix "/aws/eks/$CLUSTER"
aws route53 list-hosted-zones-by-name
aws acm list-certificates
aws resourcegroupstaggingapi get-resources --tag-filters "Key=Project,Values=$PROJECT"
```

After deletion, a VPC-specific request may return `NotFound`: record that expected absence rather than treating it as a reason to recreate infrastructure. Conversely, an AccessDenied or wrong-region query is **not** proof of absence. Tagging API coverage is incomplete and untagged/controller resources can be missed: reconcile service inventories, saved IDs and ownership instead. Check EC2/ASGs, EBS volumes/snapshots, ALBs/target groups/ENIs/SGs, endpoints, ECR images/repositories, log groups, optional RDS instances/snapshots/secrets, lab IAM/OIDC/identity resources, DNS aliases and certificates. Investigate orphans by their real owner before any deletion; do not touch unrelated objects.

Document every retained resource, owner, reason and ongoing charge, including domain registration/auto-renewal, hosted zone, certificate-validation records and approved S3 state. Remove stale application DNS pointing to the destroyed ALB. Retain ACM validation only for an expressly retained certificate/domain lifecycle. Establish responsibility for retained state encryption/versions and avoid deleting forensic evidence prematurely.

When billing data becomes available, review the selected time window in approved Cost Explorer/Billing views, service charges, tag-attribution gaps and baseline shared costs. Record actual incremental charges, estimate variance and any delayed/unallocated items. If billing lags, mark reconciliation **pending**, assign an owner/date and update later; do not claim a zero bill or a verified $30 ceiling. Capture final cleaned inventory and actual-cost follow-up separately.
