# Platform architecture

The portal is a Git-maintained content platform compiled into a static Zensical website. Markdown holds assignments; JSON holds project definitions; JSON Schema and Python checks enforce contracts. It requires no backend database, learner account, or runtime API.

## Repository structure

```text
projects/                         # Canonical project definitions, keyed by permanent ID
  DEVOPS-001/project.json
  DEVOPS-002/project.json          # Future example, not yet present

docs/                             # Only this tree is published
  projects/
    index.md                      # Generated catalog; do not edit by hand
    kubernetes/
      self-hosted-gitea/
        index.md                  # Single canonical learner assignment
        milestones.md
        verification.md
        versions.md
  platform/
    architecture.md
    roadmap.md
reviewers/
  DEVOPS-001.md                    # Separate evaluation material, never published

templates/                        # Reusable assignment, metadata and reviewer templates
platform/
  schemas/project.schema.json     # Versioned metadata contract
  README.md                       # Platform tooling entry point
scripts/                          # Build-time validation and catalog tooling
zensical.toml                     # Framework configuration and checked navigation
requirements-docs.txt              # Pinned platform dependencies
.github/workflows/                # Documentation CI and main-only Pages delivery
```

Framework-required files stay at the repository root or `.github/`. Platform infrastructure does not belong inside an assignment directory. Learners submit implementations in separate repositories; this platform never needs to run Kubernetes to render its documentation.

## Content model and identity

Each definition has one permanent ID, one primary domain, one canonical content directory, and an ordered list of public pages. The ID `DEVOPS-001` identifies **Self-Hosted Gitea Platform**, regardless of its title, directory, or technical classification. The initial primary domain is `kubernetes` and its difficulty is `intermediate`.

Allocate the next unused `DEVOPS-NNN` number, padded to at least three digits. Never reuse or renumber an ID, including after retirement. The definition directory and reviewer filename use that ID. The content directory uses a readable lowercase kebab-case slug under its primary domain. Difficulty never determines content placement. Domains describe technical areas such as `kubernetes`, `infrastructure-as-code`, `databases`, or `source-control`; difficulty describes learner experience separately.

A project spanning domains keeps one primary home. Its `domains` list includes the primary domain and all secondary technical areas. Its `tags` enable narrower cross-cutting classification: DEVOPS-001 includes `kubernetes`, `terraform`, `helm`, `minikube`, `postgresql`, and `gitea`. `technologies` carries readable names, while tags use stable lowercase kebab-case tokens.

Learning paths should reference permanent IDs, resolve them through project definitions, and link to canonical content. The same ID can appear in any number of paths without copying Markdown. Role-specific path manifests and path rendering are future work; no learner-facing path engine is implemented now.

## Metadata schema

`platform/schemas/project.schema.json` is a JSON Schema Draft 2020-12 contract. `scripts/project_metadata.py` validates it locally using the pinned `jsonschema` dependency; no schema-server request is needed at build time. Unknown properties are rejected to catch misspellings.

| Field | Contract and purpose |
| --- | --- |
| `schema_version` | Integer `1`; selects the supported metadata contract |
| `id` | Permanent `DEVOPS-NNN` identifier, independent of content path |
| `title` | Human-readable project title |
| `version` | Assignment semantic version, such as `1.0.0` |
| `primary_domain` | Domain determining the canonical content directory and navigation group |
| `domains` | Unique domain slugs including primary and secondary areas |
| `difficulty` | `beginner`, `intermediate`, or `advanced` |
| `estimated_effort` | Positive integer `min`/`max`, with unit `hours`; excludes stretch goals |
| `technologies` | Nonempty unique list of readable mandatory tool/product names |
| `tags` | Nonempty unique lowercase kebab-case discovery tags |
| `prerequisites` | Structured `skills`, `tools`, and permanent project ID lists |
| `learning_objectives` | Observable learning outcomes |
| `status` | `draft`, `active`, `deprecated`, or `archived` |
| `content_path` | Canonical path relative to `docs/`, under `projects/<primary-domain>/<slug>` |
| `pages` | Ordered page labels and Markdown filenames; first is `index.md` |
| `deprecation` | Required only for deprecated/archived projects: reason and optional replacement ID |

Schema validation checks field types, required fields, allowed values and naming. Cross-record checks enforce unique IDs/content paths, primary-domain consistency, valid effort ranges, unique page names/labels, existing pages/reviewer notes, and resolvable prerequisite/replacement IDs without self-reference. Prerequisite cycle analysis and dependency graph rendering are deferred; current references are checked for existence only.

Copy `templates/project.json` when authoring. The sample DEVOPS-002 ID is illustrative; confirm it is unused before allocating it. Keep both template and definitions valid when changing schema versions.

## Project lifecycle

| Status | Meaning | Publication policy |
| --- | --- | --- |
| `draft` | Under development, acceptance requirements may change | If included in this repository's catalog, visible and clearly labeled draft; never assume private |
| `active` | Ready for learner use and review | Included in catalog/navigation |
| `deprecated` | Discouraged for new starts; retain for existing learners | Retain content and ID, explain reason and replacement in catalog |
| `archived` | No longer maintained or recommended | Retain historical content and ID with explicit status/reason |

Normally a project moves draft → active → deprecated → archived. A maintainer reviews the metadata/content diff and compatibility evidence before a transition; there is no hidden workflow service. Git review enforces transition judgment, while validation enforces valid states and deprecation details. Draft content is public whenever the site is published. Keep confidential or incomplete work on an unpublished branch, not in a supposedly hidden navigation entry.

Record deprecation reason and replacement ID when one exists; never silently redirect learners to a different assignment. Keep retired definitions as tombstones and retain canonical content. Before changing an already published content path, update every internal reference and provide a redirect or old-path notice; redirect automation is not implemented. The initial directory migration happened before any publication, so there are no published old URLs to preserve.

## Versioning conventions

Reviewer-released follow-ups are handouts under `reviewers/followups/`, with separate evaluation notes under `reviewers/`. They extend a permanent project using a display suffix, not a new schema-v1 project ID or catalog definition. They do not enter `docs/`, navigation, generated indexes, or search assets. A reviewer checks the base completion evidence and records a manual decision before handing over only the learner brief through the agreed review channel. This implements no authentication, automatic unlock, or confidentiality: all tracked source remains visible to repository readers. Publication validation scans nested reviewer material, including follow-up identifiers and titles. Follow-up effort is separate from the base estimate.

The permanent ID identifies the assignment; `version` identifies its requirements. Use patch increments for clarifications preserving acceptance criteria, minor increments for backward-compatible added guidance or optional work, and major increments for changed mandatory outcomes, stack, or acceptance behavior. Tool pins do not automatically decide the version bump: assess their effect on learners.

Git commits and tags preserve history; learners submit the project ID, assignment version, and their solution commit SHA. Before releasing updates, document material changes in the project overview or a linked changelog page declared in `pages`. Future multi-version rendering can use Git tags without duplicating the current assignment now. Schema changes are separate from assignment versions: introduce a new schema contract plus an explicit metadata migration and update validation before adopting it.

## Navigation generation and validation

The initial implementation uses two small, deterministic mechanisms:

1. `python scripts/project_metadata.py --write` generates the catalog from definitions, grouped by primary domain and ordered by permanent ID. It includes title, ID, effort, difficulty, lifecycle, technologies, tags, domains, objectives and deprecation notices.
2. `python scripts/project_metadata.py --navigation` prints the expected Projects navigation tree as JSON. Authors mirror that tree in readable `zensical.toml`. Validation compares the complete Projects subtree against metadata, including groups, labels, order and page paths.

Run `python scripts/project_metadata.py` to check without writing. The main documentation validator also performs these checks, requires every Markdown page to be in navigation, and verifies generated links and reviewer isolation. CI fails if metadata, catalog or navigation drift apart. Run metadata checks before building and HTML checks after building.

This deliberately avoids a custom Zensical plugin or generated framework configuration. With 20 or more projects, authors still add a definition, content and the corresponding domain navigation entries; no site redesign or database migration is needed. Catalog generation stays build-time Python. Domain membership comes from metadata, never from experience level.

## Extension points

These are future design directions, not implemented features:

| Capability | Incremental extension |
| --- | --- |
| Interactive filtering | Emit a public catalog JSON from validated definitions; enhance the static catalog with small accessible JavaScript for tags, domain, difficulty, effort and status |
| Role-specific learning paths | Add schema-validated manifests listing ordered permanent project IDs; resolve canonical links and allow overlap across roles |
| Prerequisite graphs | Build directed edges from `prerequisites.projects`; add cycle checks and render a graph at build time |
| Project version history | Link Git tags/commits and changelogs, then evaluate static versioned builds if demand warrants them |
| Automated assignment validation | Add project-specific static contract checks without distributing complete solutions |
| Automated learner submission testing | Separate trusted test definitions from submissions; run opt-in tests in isolated disposable runners with no platform or publication credentials |
| Reviewer workflows | Add review templates and evidence summaries keyed by ID/version/submission SHA; retain reviewer source outside published artifacts |
| Learner progress | Start with learner-owned local files or exports keyed by ID/version. Accounts, cross-device sync and sensitive progress data require a separate privacy/access design |

A future backend could consume the same static definitions, but the catalog, assignments, review expectations and learning paths must retain a usable static representation. Do not add accounts, trackers, runtime APIs or a database merely to reserve extension points.

## Technical decisions and trade-offs

- **Git and static files:** simple review, branching, reproducibility and hosting; no centralized progress synchronization today.
- **Definitions outside published content:** clear separation between the canonical data model and prose. Public metadata is projected into the catalog; reviewer data never enters it.
- **One domain home plus tags:** stable, understandable structure without duplicate assignments; cross-domain discovery needs a later filter or path view.
- **JSON Schema plus small Python checks:** portable contract with cross-record integrity; one additional pinned validation dependency rather than a bespoke schema language.
- **Generated catalog, validated navigation:** avoids drift while keeping framework configuration transparent; navigation edits remain an explicit authoring step.
- **Reviewer separation:** build boundaries prevent accidental site inclusion, but repository readers can still see reviewer files. This is not confidentiality or access control.

See the [incremental roadmap](roadmap.md) for implementation gates.
