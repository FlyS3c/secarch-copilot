# SecArch Copilot Project Charter

## Purpose
Help a security professional create a cited first draft of an enterprise threat model or architecture review from sanitized input.

## Target user
A security engineer or security architect working with synthetic or approved information.

## Version 1 workflows
- Threat Model Builder
- Architecture Review Assistant

## Inputs
- Sanitized system purpose and components
- Data classification and data flows
- Identities, integrations, network boundaries, and vendors
- Approved public security references
## Outputs
- Summary, assumptions, and missing information
- Assets and trust boundaries
- Findings, threats, recommendations, and residual-risk questions
- Source IDs and page or section citations
- A visible human-review-required indicator

## Non-goals
- No production connections or write-capable tools
- No command execution or automatic remediation
- No architecture approval, risk acceptance, or compliance certification
- No employer, customer, secret, or licensed-course data

## Success criteria
- 100% schema-valid responses on the evaluation set
- Zero unauthorized chunks returned in access-control tests
- Citations support at least 90% of sampled material claims
- The system abstains when evidence is missing or conflicting
## Human review boundary
The assistant drafts and recommends. A qualified person validates every finding, mapping, severity, and decision before use.

## Assumptions
- Version 1 runs locally on one Windows laptop.
- Ollama and FastAPI listen only on loopback.
- The portfolio tenant is portfolio-demo.
- The initial authenticated role is security-architect.

## Owner and review
Owner: Glenn Merritt
Review cadence: at the end of every phase
Last reviewed: 2026-09-03
