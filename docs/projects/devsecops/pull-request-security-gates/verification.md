# Verification — DEVOPS-005

Record the assignment version, repository and PR links, test date, exact commits and sanitized evidence. Use a non-bypass identity to test actual mergeability. For every scenario identify the scanner analysis ID, analyzed revision, final result and matching GitHub check. Explain differences between head and test-merge commits and show the result applies to the commit GitHub requires.

| Scenario | Required observation |
| --- | --- |
| Clean baseline in each of four repositories | Reproducible build, three applicable independent checks pass and the protected PR is mergeable. |
| Known vulnerable dependency | Real Black Duck result identifies the dependency; severity and check outcome match the documented policy. |
| Source weakness | Real Coverity result identifies the controlled weakness and produces the mapped check outcome. |
| Quality or security violation | Real SonarQube result and final quality gate match the configured check outcome. |
| Critical case in each repository | Authoritative severity and finding are recorded; a required check fails and the protected PR cannot merge. |
| Remediation | A new commit is analyzed; the relevant finding is resolved, all required checks pass and the protected PR becomes mergeable. |
| Concurrency and independence | Timestamps or run records show all three can overlap and each has its own result; failure of one does not hide the others. |
| Failure and freshness | Exercise scanner unavailability or execution failure, plus authentication, result retrieval, timeout, stale-result and unexpected-skip handling. The required gate cannot falsely pass. |
| Endpoint rotation | Change a centralized endpoint through the appropriate secret and demonstrate the integration uses the new endpoint without a workflow code change; redact both values. |
| Trust and protection | Demonstrate the handling of internal and fork PRs, unavailable secrets and attempted unauthorized changes to workflow or gate configuration. Explain why untrusted builds cannot access credentials. |

For each case provide the component or weakness, affected version where applicable, CVE or CWE where applicable, severity with its authoritative source, expected detecting scanner, actual result, expected and actual check, and remediation. Provide the scanner responsibility matrix, policy thresholds, rules and justified overlaps and exclusions. Differentiate critical security findings from quality violations.

Show the required check names and protection or ruleset configuration, expected source where supported, and merge-box or API evidence before and after remediation. A screenshot of a failed workflow alone does not establish merge blocking. GitHub may treat a skipped job as successful: test the actual required gate and account for skipped, neutral and missing checks. If a plan or scanner cannot support a requirement, record the limitation and the unperformed demonstration separately; propose an alternative for approval. Mocks supplement, but never replace, real scanner evidence.

Provide setup and cleanup records for any optional Sandbox infrastructure, cost estimates and evidence of destruction. Remove secrets and sensitive identifiers from all reports and artifacts; do not submit Terraform state or plans.
