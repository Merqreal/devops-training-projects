# Validation record

Performed locally on 2026-10-19 on branch `feat/devops-training-portal`.

## Repository preparation

The initial working tree was clean and had no tracked project files. No existing content was overwritten or unrelated projects modified. A dedicated feature branch was created. No commit, push, Pages enablement, or deployment was performed.

## Successful checks

- Python 3.12 virtual environment; Zensical 0.0.71 and all resolved Python dependencies installed and pinned in `requirements-docs.txt`.
- `zensical build --strict`: successful with no reported issues.
- `python scripts/validate_docs.py`: one project, nine generated HTML pages, 384 local links/assets/anchors validated. All source Markdown is in navigation; metadata, catalog and reviewer-file association pass.
- Generated HTML and text assets, including search data, scanned for reviewer paths, sentinel and reviewer prose fingerprints. No leakage detected.
- Validator negative checks in an isolated temporary copy rejected missing metadata, broken local links, reviewer sentinel leakage and copied reviewer prose without a sentinel.
- Both GitHub Actions workflow YAML files parsed successfully. Hosted Actions execution has not been run.
- Headless Chrome desktop screenshot inspected at 1440 × 1100. HTTP preview checked with mobile emulation at 390 × 844: page width and scroll width both 390px. Mobile screenshot inspected.
- Browser search for `PostgreSQL` returned ten result links; dark-theme toggle changed the scheme to `slate`; Project 001 Mermaid diagram rendered, with no unrendered Mermaid fence remaining and no horizontal page overflow at 390px.
- Gitea official chart index/package inspected; Helm resolved Gitea 12.7.0 / application 1.27.0.
- Helm resolved CloudPirates PostgreSQL chart 0.21.2 from its OCI registry and inspected published values. OCI manifest digest: `sha256:3e60096923c9afc083d1515960bb22f9cb52b4e781ab81bb7b077ec352ad324b`. Tagged upstream values and provider 2.38.0/3.0.2 context configuration inspected.
- Seven milestones and all requested assignment sections reviewed against the task, including separate data stores, Windows access, explicit targeting, credential/state risks, lifecycle limits, safe cleanup, and real evidence requirements.
- New files scanned for private-key headers, AWS access key patterns and GitHub token patterns; no matches. State and saved plans are excluded; no real credentials were authored. This is a focused scan, not a guarantee against every possible secret format.
- New-file diff reviewed and `git diff --check` passed. Files remain uncommitted for review.

## Unsuccessful attempts and limits

Sandbox DNS/socket restrictions initially blocked package/chart access and local preview/browser connections. Approved network-enabled retries succeeded. Port 8000 was already occupied; actual preview used `http://127.0.0.1:8008`. No existing process on port 8000 was stopped. An initial mobile file-URL screenshot did not reflect the initialized responsive layout; the HTTP preview/mobile-emulation check above supersedes it.

No learner Kubernetes environment was deployed. No Terraform init/plan/apply, database initialization, Git transport, Windows host access, or persistence failure tests were executed for the assignment. Version compatibility is source-checked and must be demonstrated by the learner. Local Helm inspection used installed CLI 3.18.5; the learner baseline is 3.19.0. External links are cited but not exhaustively availability-tested. Browser checks are focused smoke checks, not a complete accessibility audit.

## Publication still requires manual configuration

After explicit approval, follow README instructions: verify audience/privacy, merge onto default branch, configure Pages for Actions, protect the `github-pages` environment, set the authorization variable, and manually dispatch with exact confirmation. No such settings were changed. A private repository must not be assumed to yield a private Pages site.

## Architecture extension verification — 2026-10-19

This section supersedes the initial project name, directory and generated-page counts above. The assignment is now **DEVOPS-001 — Self-Hosted Gitea Platform** with its definition at `projects/DEVOPS-001/project.json` and canonical content at `docs/projects/kubernetes/self-hosted-gitea/`. The permanent ID remains independent of that path. Reviewer notes moved to `reviewers/DEVOPS-001.md`.

- Added JSON Schema v1 with pinned `jsonschema==4.25.1` and transitive dependencies; template and real definition both validate.
- All 14 metadata contract tests passed, including invalid prerequisites/difficulty/effort, duplicate IDs/content paths, missing deprecation details, unresolved references, catalog/navigation drift, stable identity after a domain/path move, and 21 fixture projects across multiple domains and levels.
- Metadata-derived catalog and exact domain-grouped Projects navigation checks passed. Both CI workflows now run tests and metadata checks before the build; hosted Actions remains unexecuted.
- Strict Zensical build passed with no reported issues. Documentation validation passed for one real project, 11 HTML pages and 511 local links/assets/anchors; reviewer isolation remained intact.
- Platform architecture, incremental roadmap, templates, author instructions, standards and setup instructions were reviewed for consistency with the new conventions. Future discovery, paths, graph rendering, assignment testing, reviewer automation and learner tracking are documented proposals, not delivered runtime features.
- No backend/database, publication, learner deployment or new cloud dependency was introduced. Earlier browser smoke results apply to the existing site components; browser smoke checks were not repeated for the new architecture prose pages.

## Public publication preparation — 2026-10-19

Public repository and GitHub Pages publication, including automatic deployment on merged `main` changes, were explicitly authorized. This supersedes earlier disabled-publication instructions. The repository was public and initially had no commits or remote branches; the plan is a minimal `.gitignore` bootstrap on `main`, followed by the portal feature PR and normal CI-verified merge.

- All 14 tests, catalog generation, metadata validation, strict build, 511 local links/assets/anchors and reviewer-content isolation passed again.
- Production `site_url` is exactly `https://merqreal.github.io/devops-training-projects/`.
- Reviewed all 29 source files with focused credential/private-key/token checks, whitespace checks, and generated-artifact exclusions. No matching real credentials or unintended runtime/build artifacts found. Reviewer material is deliberately public in Git, excluded from website artifacts.
- Deployment uses official configure-pages, upload-pages-artifact and deploy-pages actions, explicit main-only triggers/job guards, scoped Pages/OIDC permissions, and serialized deployment concurrency. Pull-request validation remains enabled and rejects stale generated catalog changes.
- GitHub API access as Merqreal has repository administration/push permission. Pages initially returned HTTP 404 (not configured). Final deployment and live verification results will be reported separately after GitHub execution; configuration alone is not a success claim.
- Production-prefix browser checks passed using a local HTTP server that serves only `/devops-training-projects/`: homepage, domain-grouped catalog, DEVOPS-001, verification page, navigation, code copy controls, ten PostgreSQL search-result links, static assets, dark theme, mobile width and Mermaid rendering. All 30 observed internal HTTP responses succeeded. An initial test used the previous theme's copy-button selector; the corrected selector passed.
- Public Pages is configured with build type `workflow`; the `github-pages` environment restricts deployment to the `main` branch. The repository initially had no main branch protection to bypass. Live deployment is still pending the feature PR/CI/merge at this commit's preparation time.
