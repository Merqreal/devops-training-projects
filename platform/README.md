# Platform infrastructure

This directory owns platform contracts, not learner infrastructure. The metadata schema is `schemas/project.schema.json`. Root `zensical.toml`, pinned documentation requirements, `scripts/`, and `.github/workflows/` are also platform infrastructure in their conventional tool locations.

Project definitions are in `projects/DEVOPS-NNN/project.json`, public content under `docs/projects/<primary-domain>/<slug>/`, reusable source under `templates/`, and review notes under `reviewers/`.

Read [architecture](../docs/platform/architecture.md) and [roadmap](../docs/platform/roadmap.md) before changing contracts. Run the metadata check, strict build, and documentation validator described in the root README.
