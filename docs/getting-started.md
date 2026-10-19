# Getting started

## Prepare your workstation

You need Git, a text editor, a terminal, basic Linux shell skills, and enough local resources for your chosen assignment. DEVOPS-001 requires Windows with virtualization enabled, WSL2 running Ubuntu, Docker available inside Ubuntu, and a local Kubernetes toolchain. Follow its [version and resource baseline](projects/kubernetes/self-hosted-gitea/versions.md).

You should be comfortable with commits, branches, YAML, TCP ports, environment variables, and basic containers. Learn unfamiliar tools from upstream documentation and record what you learn. Internet access is needed to download tools, charts, and images; no hosted runtime or paid cloud account is required.

## Work from outcomes

1. Read the entire assignment and its acceptance criteria before writing infrastructure.
2. Create a **separate solution repository**; do not put a completed solution in this portal.
3. Pin dependencies and record your design decisions. Commit small, understandable changes.
4. Implement each milestone and collect redacted verification evidence.
5. Rehearse deployment from documented prerequisites, repeat the plan, and test failure recovery.
6. Submit your project ID, assignment version, repository URL and immutable commit SHA to your reviewer through the team's agreed channel.

Assignments describe expected behavior and constraints. You choose the implementation. Upstream examples may inform your work; acknowledge sources and explain every submitted component. A prebuilt solution repository does not demonstrate completion.

## Repository conventions

The portal stores public assignments in `docs/projects/<primary-domain>/<slug>/`, with definitions in `projects/DEVOPS-NNN/project.json`. Learner repositories contain Terraform, Helm configuration, scripts, documentation, and sanitized evidence. See [standards](standards.md) for the expected tree and review rules.

## Ask useful questions

Include the milestone, expected behavior, observed behavior, tool versions, and minimal redacted diagnostics. Never share kubeconfig contents, passwords, tokens, state files, saved plans, or secret manifests. Document any manual step needed to reproduce the environment.

## Submit and iterate

Give the reviewer access to your separate repository. Include a requirement-to-evidence checklist, known limitations, and exact setup, validation, and cleanup commands. Respond to review findings in new commits; update the submitted SHA. A reviewer should be able to work from your README without asking you for missing deployment steps.
