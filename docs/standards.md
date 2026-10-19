# Engineering standards

## Portal structure

Project definitions live in `projects/DEVOPS-NNN/project.json`. Learner content lives in `docs/projects/<primary-domain>/<slug>/`; difficulty never determines a directory. Reviewer notes live in `reviewers/DEVOPS-NNN.md`. Templates, schemas, scripts, and CI remain separate from assignment content.

The permanent ID survives renames and domain moves. Structured metadata records difficulty, technologies, prerequisite skills/tools/project IDs, effort, lifecycle, domains, tags, version, and ordered pages. Read the [platform architecture](platform/architecture.md) for the full tree, schema, naming, lifecycle and deprecation rules.

Generate the catalog with `python scripts/project_metadata.py --write` and update the Projects navigation to match the emitted metadata-derived tree. CI validates both against definitions. Reference IDs from future learning paths; link to the single canonical assignment instead of copying it.

## Learner repository

```text
README.md
terraform/               # Providers, namespace, releases, version constraints
  .terraform.lock.hcl    # Commit provider dependency lock
helm/                    # Values and any custom chart source + chart lock
scripts/                 # Bootstrap, deployment, health, access, test, cleanup
validation/              # Procedures and sanitized evidence
  persistence.md
diagrams/                # Mermaid source or diagram in README
.gitignore
```

Equivalent layouts are acceptable if the README maps their contents. Commit source and dependency locks. Ignore runtime caches, credentials, private keys, state and backups, saved plans, real variable files, and local environment files. Supply placeholder-only input documentation.

## Documentation expectations

Use readable Markdown with relative internal links, descriptive headings, language-tagged code fences, and a Mermaid architecture diagram. Separate requirements from optional extensions. Commands must identify their shell, prerequisites, working directory, inputs, expected result, and destructive effects. Do not describe an unexecuted check as passing.

The solution README must cover architecture, prerequisites, deployment, configuration, access, validation, troubleshooting, persistence behavior, and cleanup. Explain resource ownership and recovery limits. Record exact tool, chart, image, and Kubernetes versions and upstream sources.

## Submission and completion

Submit the permanent project ID, assignment version, separate repository and commit SHA with all mandatory deliverables. Reviewers assess reproducibility, functionality, data durability, security, operational usability, and explanation quality. Every acceptance criterion needs evidence or a reproducible verification procedure, and runtime persistence checks need actual before/after evidence. Optional work cannot compensate for missing mandatory work.

No real secrets, cloud credentials, undocumented required mutations, or unrelated application development. Failed or incomplete checks must be disclosed. Reviewers may request a clean deployment and a live failure demonstration. Reviewer-only notes remain outside `docs/`; Git visibility is **not** an access-control boundary.
