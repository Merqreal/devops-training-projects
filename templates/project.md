# DEVOPS-NNN — Title

Replace every placeholder before publication. Copy to `docs/projects/<primary-domain>/<slug>/index.md`; create `projects/DEVOPS-NNN/project.json` from the metadata template and `reviewers/DEVOPS-NNN.md`. Follow `docs/platform/architecture.md`. Link any split pages from this overview and navigation.

## Project ID and title
DEVOPS-NNN · Unique title; keep the ID permanent even if the domain or slug changes.

## Difficulty and expected duration
State skill level and realistic hour range, excluding optional work. Mirror the schema-validated metadata. Record primary domain, cross-domain tags, prerequisites, version and lifecycle in the definition.

## Problem statement and business context
Who needs the infrastructure, what problem it solves, and why success matters.

## Learning objectives
Use observable outcomes: build, explain, verify, diagnose.

## Prerequisites
Skills, workstation resources, tools, access, costs, and upstream sources.

## Target architecture
Include a Mermaid diagram of boundaries, traffic and data ownership; leave implementation choices to learners.

## Mandatory technology stack
Pin compatible tools, providers, charts and images; cite upstream versioned configuration contracts. State source-check date and runtime verification status.

## Functional requirements
Describe observable user behavior without a complete implementation.

## Infrastructure requirements
Define lifecycle ownership, networking, storage, sizing, health and repeatability.

## Security requirements
Specify secret injection, least privilege, state/log exposure, and required boundaries.

## Milestones and deliverables
For each milestone list requirements, artifacts and observable acceptance gate.

## Acceptance criteria
Map every mandatory requirement to objective pass/fail evidence.

## Verification procedures
Specify prerequisites, diagnostic commands, expected observations, failure handling and evidence. Distinguish source checks from executed runtime tests.

## Expected submission structure
Separate learner repository containing source, locks, scripts, README, diagram and sanitized validation evidence.

## Constraints and non-goals
Make scope, prohibited dependencies, cost and durability limits explicit.

## Optional stretch goals
Clearly separate all enhancements; mandatory criteria come first.

## Reviewer guidance
Public review expectations only. Keep evaluation notes and reference strategy outside `docs/` using `templates/reviewer.md`.
