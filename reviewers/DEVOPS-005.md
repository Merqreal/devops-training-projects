# Reviewer notes — DEVOPS-005

REVIEWER_ONLY_DO_NOT_PUBLISH

Git visibility is not confidentiality. Do not publish this file.

## Evaluation criteria

Require a mapping from every mandatory outcome to actual evidence. Check four independent repositories, real reproducible build manifests and locks, three reusable independently named gates, parallel runs and per-technology configuration. Inspect the responsibility matrix, justified overlap, version pins, licensing assessment and source dates. Verify each repository has a sourced critical case, and all three scanners have meaningful real findings across the set. Each case needs expected and actual results, commit, severity source and remediation. A documented blocker is honest but is not evidence of a passing integration; do not silently credit a substitute or a mock.

Use a non-bypass account to inspect actual branch protection and mergeability before and after remediation. Verify results correspond to the required current commit, final remote analysis and configured threshold. Check each failure mode, especially unavailable endpoint, auth, retrieval, stale result, timeout and skipped required job. Confirm endpoint rotation without code edits and clean baseline in each repository. Assess setup, operations, cleanup, costs and optional Terraform when used.

## Common failure modes

Accepted scan uploads treated as final results; stale or shared scanner project results; a skipped or neutral job accepted by GitHub; check name collisions; checks bypassed by filters; policy thresholds that misclassify quality findings as critical CVEs; unverified free access; scanner tokens exposed to build scripts, plugins, forks or modified workflows; runner caches or artifacts leaking secrets; screenshots without merge evidence; mock data presented as actual analysis.

## Expected technical explanations

Ask how the system binds analysis and status to the required SHA, enforces failure on missing results, protects trusted configuration and prevents untrusted builds from reading or exfiltrating credentials. Ask how forks and internal PRs differ, why GitHub masking is insufficient, which identity enforces merge rules, and what remains unsupported. Require a credible separation of build execution and privileged scanning, with scanner-specific limitations acknowledged. Explain quality gates versus vulnerability severity and why overlap alone is not grounds for excluding coverage. Verify legal and technical eligibility rather than treating documentation as a license.

## Reference validation strategy

This is a planned review, not a claim of executed integration. Inspect sanitized configuration and evidence first; reproduce selected safe clean, critical, remediation and failure scenarios in the learner's isolated test environment using a non-bypass identity. Confirm parallel timing, scanner result revision, actual merge blocking and eventual mergeability. Test secret boundary and fork handling without disclosing credentials. Review optional Terraform for isolation, least privilege, networking, cost and teardown; verify cleanup and absence of state or secrets in the submission. Record untested or unavailable capabilities explicitly.
