# Versions and upstream contracts

## Version policy

Upstream artifacts and configuration keys below were inspected on **2026-10-19**. This is a source-checked compatibility baseline, **not a deployed or integration-tested environment**. Learners must prove runtime compatibility, pin resolved image digests and provider locks, and record actual tool outputs. No Kubernetes deployment was performed when authoring this portal.

| Component | Assignment baseline | Notes |
| --- | --- | --- |
| WSL / Ubuntu | WSL2 / Ubuntu 24.04 LTS | Record exact Windows and WSL builds; networking depends on them |
| Docker | Engine 28.5.1 or Docker Desktop providing that compatible API | Use one documented Docker setup; record server/client versions and WSL integration |
| Minikube | 1.37.0 | Docker driver, named profile |
| Kubernetes / kubectl | 1.34.0 / 1.34.0 | Match client and server minor version |
| Helm CLI | 3.19.0 | Helm 3 baseline; avoid silently adopting Helm 4 |
| Terraform | 1.13.3 | Constrain CLI to the tested minor and pin patch in tooling |
| Kubernetes provider | hashicorp/kubernetes 2.38.0 | Explicit kubeconfig path and context |
| Helm provider | hashicorp/helm 3.0.2 | Uses object-form `kubernetes` configuration; do not copy provider v2 syntax |
| Gitea chart / application | 12.7.0 / 1.27.0 | Official chart repository; preserve rootless image variant and pin digest |
| PostgreSQL chart | CloudPirates `postgres` 0.21.2 | Maintained Helm-based method using official PostgreSQL image |
| PostgreSQL image | Official `postgres:18.6` | Chart pins a digest; record and retain that digest |
| Git | 2.43.0 or a security-patched Ubuntu 24.04 Git package | Record exact package revision |

Tool versions are a reproducibility baseline, not a claim that older patches are secure forever. Before starting, check upstream support and advisories. If a baseline is unavailable, vulnerable, or incompatible on your workstation, propose a pinned replacement, cite its release information, and document compatibility verification. No floating `latest` images or unbounded chart/provider versions.

## Workstation capacity

Plan for a Windows host with **4 logical CPUs, 16 GiB RAM, and 30 GiB free disk**. Start with **4 CPUs and 6 GiB RAM** assigned to Minikube, leaving capacity for Windows, WSL, Docker, images, PVCs, and logs. A smaller machine may work with tuning but must be documented and validated. Minikube's upstream general minimum (2 CPUs, 2 GiB free RAM, 20 GiB disk) is not a workload sizing guarantee. Virtualization and WSL2 must be enabled; confirm `docker info` works inside Ubuntu before provisioning.

See [Minikube prerequisites](https://minikube.sigs.k8s.io/docs/start/), [Docker driver](https://minikube.sigs.k8s.io/docs/drivers/docker/), [WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install), and [WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking).

## Gitea chart contract

The official [chart index](https://dl.gitea.com/charts/index.yaml) lists [gitea-12.7.0.tgz](https://dl.gitea.com/charts/gitea-12.7.0.tgz) with application version 1.27.0. Inspect the packaged `Chart.yaml`, `values.yaml`, and templates, rather than an unversioned blog example. Chart source: [Gitea Helm chart](https://gitea.com/gitea/helm-gitea).

These are configuration locations to investigate, not a complete values file:

| Concern | Verified chart keys |
| --- | --- |
| Bundled database | `postgresql.enabled`, `postgresql-ha.enabled` — disable both |
| Cache dependencies | `valkey.enabled`, `valkey-cluster.enabled` — explicitly choose and configure application cache/session/queue behavior |
| Application database | `gitea.config.database` using Gitea `DB_TYPE`, `HOST`, `NAME`, `USER`; supply `PASSWD` from a Secret |
| Secret configuration | `gitea.additionalConfigFromEnvs` supports environment entries sourced via `valueFrom.secretKeyRef`; `gitea.additionalConfigSources` supports Secret configuration sources |
| Admin provisioning | `gitea.admin.existingSecret` — inspect required keys before bootstrap |
| Advertised access | `gitea.config.server` including `ROOT_URL` and transport-specific settings |
| Repository storage | `persistence.enabled`, `persistence.size`, `persistence.storageClass` |
| Runtime sizing | Top-level `resources` |
| Health | `gitea.readinessProbe`, `gitea.livenessProbe`, `gitea.startupProbe` |
| Local Services | `service.http`, `service.ssh` |

See [Gitea configuration](https://docs.gitea.com/administration/config-cheat-sheet/) and [database preparation](https://docs.gitea.com/installation/database-prep/). Upstream documents PostgreSQL >= 12, which includes the selected major version; application behavior and image execution still require validation. Select UTF-8 database configuration and appropriate ownership/authentication.

## PostgreSQL chart contract

Use `oci://registry-1.docker.io/cloudpirates/postgres` at **0.21.2**. The [tagged source](https://github.com/CloudPirates-io/helm-charts/tree/postgres-0.21.2/charts/postgres) and [release](https://github.com/CloudPirates-io/helm-charts/releases/tag/postgres-0.21.2) identify the pinned chart. This avoids depending on legacy Bitnami image availability. Verify OCI pull and images before deployment.

| Concern | Verified chart keys and semantics |
| --- | --- |
| Identity | `auth.username`, `auth.database`; username initializes a **superuser**, not a least-privilege application account |
| Secret | `auth.existingSecret`, `auth.secretKeys.adminPasswordKey` (default key `postgres-password`) |
| Application role | `initdb.scripts` or `initdb.scriptsConfigMap`; arrange secret-safe role/database initialization without embedding real passwords in source or Helm values |
| Storage | `persistence.enabled`, `persistence.size`, `persistence.storageClass` |
| Networking | `service.type` defaults to ClusterIP; `service.port` |
| Health and sizing | `readinessProbe`, `livenessProbe`, `resources` |
| Image | `image.registry`, `image.repository`, `image.tag`; tagged chart default is official PostgreSQL 18.6 with digest |

PostgreSQL 18 changed image data-directory conventions. Inspect the tagged StatefulSet volume mount and `PGDATA`; do not assume a path from a PostgreSQL 16 tutorial. Initialization scripts only run on first initialization. Refer to the [official image documentation](https://hub.docker.com/_/postgres) for volume and initialization behavior. Explain how the separate application role obtains credentials and how bootstrap handles existing storage.

## Verify sources before implementation

From WSL Bash with Helm installed and internet access:

```bash
helm repo add gitea https://dl.gitea.com/charts/
helm repo update
helm show chart gitea/gitea --version 12.7.0
helm show values gitea/gitea --version 12.7.0
helm show chart oci://registry-1.docker.io/cloudpirates/postgres --version 0.21.2
helm show values oci://registry-1.docker.io/cloudpirates/postgres --version 0.21.2
```

Expected: both charts resolve and values match the contract. Render your own configuration and inspect resources before applying. Do not share rendered Secret objects. Chart download/configuration inspection does not establish runtime compatibility.

Provider configuration is documented in the tagged [Kubernetes 2.38.0 provider](https://github.com/hashicorp/terraform-provider-kubernetes/blob/v2.38.0/docs/index.md) and [Helm 3.0.2 provider](https://github.com/hashicorp/terraform-provider-helm/blob/v3.0.2/docs/index.md). Both support `config_path` and `config_context`; set them explicitly. Record provider checksums in `.terraform.lock.hcl`.
