# DevOps Fieldwork

A Zensical training portal for outcome-based DevOps onboarding. The first assignment is **DEVOPS-001 — Self-Hosted Gitea Platform**. This repository contains the assignment and review materials, not a learner solution.

## Local setup and preview

Use Python **3.12** and run from the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-docs.txt
.venv/bin/zensical serve --dev-addr 127.0.0.1:8000
```

Open <http://127.0.0.1:8000>. Stop the preview with Ctrl-C. Dependencies, including transitive Python packages, are pinned. Internet is required for installation and upstream research. The theme may fetch web fonts and Mermaid runtime assets; use internet access for diagram rendering during preview.

Build and validate:

```bash
.venv/bin/python scripts/project_metadata.py
.venv/bin/zensical build --strict
.venv/bin/python scripts/validate_docs.py
```

The validator checks every Markdown page is in navigation, project metadata, catalog entries, separate reviewer notes, generated local links/assets/anchors, and reviewer marker/prose leakage across HTML and search assets. It does not fetch external links or prove Kubernetes behavior. Build output in `site/` is ignored.

## Repository map

- `projects/`: permanent-ID project definitions.
- `docs/`: published learner content grouped by primary domain, catalog, standards and platform architecture.
- `platform/`: validated metadata schema and platform tooling entry point.
- `zensical.toml`, `docs/stylesheets/extra.css`: navigation, theme, typography and responsive styling.
- `templates/`: reusable assignment, metadata and reviewer templates.
- `reviewers/`: evaluation criteria, expected explanations, failure modes and reference validation strategy. Excluded from the site, **visible in Git**.
- `AGENTS.md`: instructions for future Codex authors.
- `scripts/validate_docs.py`: offline documentation contract checks.
- `.github/workflows/docs.yml`: build and validation on push/PR.
- `.github/workflows/pages.yml`: automatic deployment from `main` using official GitHub Pages actions.

## Add a project

1. Allocate a permanent unused `DEVOPS-NNN` ID; copy `templates/project.json` to `projects/DEVOPS-NNN/project.json`.
2. Choose a primary technical domain and canonical `docs/projects/<primary-domain>/<slug>/` directory. Copy the assignment template there; complete all 17 sections and the metadata. Add every public page to the ordered `pages` list.
3. Create `reviewers/DEVOPS-NNN.md` from the reviewer template, outside the published tree.
4. Run `.venv/bin/python scripts/project_metadata.py --write` to regenerate the catalog. Run it with `--navigation` to inspect the expected Projects subtree, then update `zensical.toml` accordingly. A mismatch exits nonzero until fixed.
5. Run `.venv/bin/python -m unittest discover -s tests`, metadata validation, the strict build, and documentation validation. Review upstream contracts and the diff; do not invent runtime results.

Read [architecture](docs/platform/architecture.md) for schema, identity, domain, lifecycle and version conventions, and [roadmap](docs/platform/roadmap.md) for proposed future features. Learning paths will reference IDs without copying assignment content. The static site needs no database or backend.

## Public GitHub Pages publication

The repository and portal are intended to be public. Production URL:
<https://merqreal.github.io/devops-training-projects/>.

Every push to `main` runs `.github/workflows/pages.yml`: generate/check catalog, run contract tests and metadata checks, build Zensical, check generated links/reviewer isolation, upload only `site/`, then deploy using the official Pages actions. Manual dispatch is also available, and both build and deploy jobs refuse branches other than `main`. Pull requests continue to run read-only documentation validation. Deployment is serialized with the `pages` concurrency group.

Repository setup (requires authorized GitHub access): configure **Settings → Pages → Source → GitHub Actions**. The equivalent API sets the Pages build type to `workflow`. Use the `github-pages` environment with deployment branches restricted to `main`; preserve existing protections. Do not require per-deployment manual approval if unattended redeployment on merged changes is desired. Branch protection remains authoritative for merges.

No publication authorization variable or confirmation phrase is required now that public publication has been explicitly approved. Only public learner content under `docs/` is built; reviewer files remain visible in the public Git repository but are excluded from the website and search artifacts. See the validation record for actual deployment status; workflow configuration alone does not prove a live deployment.

## Verification scope

See [VALIDATION.md](VALIDATION.md) for checks actually performed and limitations. Chart/source inspection does not establish that the learner infrastructure has been deployed or tested.
