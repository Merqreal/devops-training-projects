# Platform roadmap

Each phase should preserve the static site and existing permanent project IDs. Later phases are proposals, not features delivered with this portal.

## Phase 1 · Maintainable static foundation — implemented

- Domain-based canonical content with permanent IDs and structured definitions.
- Reusable assignment/reviewer templates, a versioned JSON Schema and cross-record checks.
- Generated catalog, metadata-validated navigation, lifecycle and version conventions.
- Zensical site, reviewer isolation checks, pinned dependencies and publication restricted to `main`.
- DEVOPS-001 under Kubernetes, with intermediate difficulty and cross-domain tags.

**Gate:** metadata/schema tests, catalog/navigation checks, strict site build and generated-link/reviewer-isolation validation pass. This gate does not deploy or validate the learner infrastructure.

## Phase 2 · Discovery and curated paths — proposed

Add projects across domains and experience levels first. Measure where catalog navigation becomes difficult. If needed, export public metadata and add accessible client-side filtering with a usable no-JavaScript fallback. Define role-specific path manifests referencing permanent IDs and prerequisite cycle checks. Generate path pages and optional dependency diagrams from those references.

**Gate:** no duplicated project content, all referenced IDs resolve, filters work with keyboard controls, and catalog/path pages remain readable as static HTML. Do not add learner accounts.

## Phase 3 · Assignment evolution and reviewer support — proposed

Add explicit release notes and link Git version history. Introduce reviewer checklists and standardized evidence summaries keyed by project ID and assignment version. Add assignment-specific static checks and fixtures where they verify meaningful requirements. Evaluate versioned documentation only when concurrent assignment versions need support.

**Gate:** existing learner submissions remain interpretable against their assigned version; deprecations retain IDs and explain replacements; reviewer material stays outside public build artifacts.

## Phase 4 · Isolated submission validation — proposed

Pilot automated learner tests on one assignment. Separate platform documentation CI from untrusted submission execution. Define permissions, resource/time budgets, test ownership, evidence retention and disposable cleanup before running third-party code. Review infrastructure tests for portability and avoid exposing a complete implementation through public fixtures.

**Gate:** no submission code can access repository publication credentials or other learners' data. Manual reviewer assessment remains available when runtime checks are unavailable. Clearly distinguish static checks, actual deployment checks and unexecuted tests.

## Phase 5 · Optional progress tooling — proposed

Start with learner-controlled local progress records or exports keyed by project ID/version, optionally referencing evidence and solution SHA. Evaluate a separate service only if authenticated cross-device synchronization is justified. Decide identity, consent, retention, data access, deletion and maintenance ownership before collecting centralized learner data.

**Gate:** the static portal works independently; progress tooling can be removed without losing assignment content or breaking discovery. No backend database is required by the initial architecture.
