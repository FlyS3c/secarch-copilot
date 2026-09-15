# Security Policy

## Supported versions

SecArch Copilot is an experimental portfolio project under active development. Security fixes are applied only to the latest commit on the `main` branch.

| Version                  | Supported |
| ------------------------ | --------- |
| Latest `main` branch     | Yes       |
| Earlier commits or forks | No        |

The project is approved only for controlled local demonstrations using public, synthetic, or explicitly approved data. It is not supported for production, multi-user, internet-facing, autonomous, compliance, architecture-approval, or risk-acceptance use.

## Reporting a vulnerability

Use GitHub private vulnerability reporting:

[Report a vulnerability privately](https://github.com/FlyS3c/secarch-copilot/security/advisories/new)

Do not disclose vulnerability details in a public issue, discussion, pull request, commit message, or social-media post.

If private vulnerability reporting is not available, open a public issue titled `Security contact requested` without including technical details, exploit steps, logs, secrets, or affected data. The maintainer will establish a private reporting channel.

## Information to include

Provide enough information to reproduce and assess the issue safely:

* Affected commit, component, endpoint, or workflow
* Vulnerability type and expected security boundary
* Minimal reproduction steps using synthetic data
* Potential impact
* Required attacker access or prerequisites
* Relevant configuration with secrets removed
* Suggested mitigation, if available

Do not include real API keys, tokens, credentials, personal information, employer information, customer data, production logs, restricted documents, or licensed training content.

## Response expectations

The maintainer will aim to:

* Acknowledge the report within five business days
* Complete an initial severity and applicability assessment within ten business days
* Keep the reporter informed when additional investigation is required
* Develop a remediation or compensating-control plan based on severity and project scope
* Coordinate public disclosure after a fix or documented risk decision is available

These are good-faith targets for a personal portfolio project, not contractual service-level commitments.

## In-scope security issues

Examples include:

* API authentication or authorization bypass
* Retrieval across tenant, role, clearance, classification, or approval boundaries
* Exposure of prompts, source text, credentials, or audit-sensitive information
* Citation validation bypass
* Unsafe handling of model-generated HTML or script content
* Source-validation, path-containment, checksum, or quarantine bypass
* Prompt injection that changes application scope or exposes protected instructions
* Request-size, rate-limit, concurrency-limit, or timeout-control bypass
* Container privilege, secret-handling, or GitHub Actions security weaknesses
* Project-specific exploitation of a vulnerable dependency

## Generally out of scope

The following are generally not treated as security vulnerabilities unless they enable a documented security-boundary failure:

* Generic language-model hallucinations or low-quality recommendations
* Unsupported security conclusions already documented in the evaluation report
* High local model latency
* Attacks that require intentionally exposing the local-only service to untrusted networks
* Missing production controls for a project explicitly classified as non-production
* Vulnerabilities that exist only in unsupported forks or modified configurations
* Denial-of-service testing that could affect third-party services or systems

Model-quality, grounding, and evaluation defects may still be reported as ordinary GitHub issues using synthetic evidence.

## Dependency vulnerabilities

Known dependency findings are documented in `docs/dependency-risk-register.md`. A listed accepted risk may still be reported if new evidence shows that it is exploitable in the supported local architecture or invalidates a documented compensating control.

When the root cause is an upstream dependency, report it to the upstream maintainer as appropriate and notify this project privately if SecArch Copilot is affected.

## Safe-harbor intent

Good-faith research that follows this policy, uses synthetic data, avoids privacy violations, and does not degrade third-party systems is welcomed. Stop testing and report the issue if you encounter data or access that you did not expect.

This policy does not authorize testing against systems, accounts, data, or infrastructure that you do not own or have explicit permission to assess.

## Disclosure

Allow reasonable time for investigation and remediation before public disclosure. The maintainer may credit reporters who want public acknowledgment after the issue is resolved.
