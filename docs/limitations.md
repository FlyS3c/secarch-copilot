# Limitations and Intended Use

Last reviewed: 2026-09-15

## Current decision

SecArch Copilot is suitable only for controlled local portfolio demonstrations using public, synthetic, or explicitly approved information, with mandatory qualified human review.

It is not approved for production use, autonomous security decisions, compliance determinations, architecture approval, risk acceptance, or automated remediation.

## Model output limitations

The language model is an untrusted drafting component. Generated findings may:

* Misinterpret the supplied architecture
* Introduce assumptions that were not provided
* Recommend controls not supported by the retrieved evidence
* Misstate or reverse the meaning of a source
* Assign an inappropriate severity
* Omit relevant threats or security considerations
* Produce inconsistent results across repeated executions
* Return plausible but incorrect information

Every finding is marked as requiring human review. This marker does not make the finding accurate.

## Grounding and citation limitations

The application validates that generated citation identifiers match evidence retrieved for the request. This blocks fabricated or out-of-scope citation identifiers.

Citation identifier validation does not prove that:

* The cited text supports the generated claim
* The recommendation follows from the cited evidence
* Conditional guidance applies to the described system
* The model interpreted the source correctly
* The cited evidence is complete or current
* The generated risk severity is justified

Human review of the recorded grounded evaluation found that none of the three generated findings were fully supported by their cited evidence. The model introduced unsupported assumptions and recommendations and misinterpreted cited guidance.

This semantic-grounding failure is a primary reason production and autonomous use remain prohibited. See `docs/evaluation-report.md` for the recorded results.

## Retrieval limitations

Retrieval quality depends on:

* The completeness and quality of the approved source corpus
* Document parsing and chunking
* Embedding-model behavior
* The configured distance threshold
* The number of results requested
* The terminology used in the system description
* Collection version and metadata quality

Relevant evidence may not be retrieved, and retrieved evidence may not be sufficient to support a finding.

The approved local corpus is intentionally limited. It does not represent every security framework, technology, regulatory requirement, threat, architecture pattern, or organizational policy.

## Source limitations

Only sources marked as approved in `data/sources.yml` may be ingested and used for retrieval.

Restricted SABSA materials remain reference-only and are excluded from ingestion and retrieval unless written permission is obtained from the applicable rights holders.

Source hashes identify the expected local file versions but do not prove that the content is safe, correct, complete, or suitable for a particular decision. Ingestion warnings still require review.

The project does not automatically guarantee that downloaded sources remain current. Source updates require version, checksum, approval, ingestion, and evaluation review.

## Threat-model limitations

Generated threat models are preliminary drafts rather than exhaustive threat analyses.

They may omit:

* Assets or data flows not supplied by the user
* Technology-specific threats
* Abuse cases and business-logic failures
* Insider threats
* Supply-chain risks
* Operational and recovery risks
* Physical security concerns
* Organization-specific risk and control requirements

The project does not perform live asset discovery, configuration review, vulnerability scanning, penetration testing, source-code analysis, or control-effectiveness validation.

## Architecture-review limitations

Architecture reviews depend entirely on the supplied system description and approved retrieved evidence.

The application does not independently verify:

* Whether the described architecture matches the deployed environment
* Whether stated controls are implemented
* Whether controls operate effectively
* Whether security boundaries are complete
* Whether identities, integrations, or data classifications are accurate
* Whether a system meets legal, regulatory, contractual, or internal-policy requirements

Generated reviews must not be treated as architecture approval or certification.

## Authorization limitations

The project applies tenant, role, classification, approval, and source metadata filters before returning retrieval results.

These controls demonstrate authorization-aware retrieval but are not a replacement for a production identity and access management system.

The local deployment uses configured identity context and a shared local API key. It does not provide full user lifecycle management, federation, individual accountability, privileged-access management, enterprise key rotation, or production-grade multi-tenant isolation.

## Prompt-injection limitations

The project treats system descriptions and retrieved reference text as untrusted data and includes tests for prompt boundaries and indirect prompt injection.

These controls reduce risk but do not prove immunity from:

* New prompt-injection techniques
* Encoded or obfuscated instructions
* Multi-step manipulation
* Model-specific behavior
* Malicious source combinations
* Future dependency or model changes

Unsupported citations are designed to fail closed, but other forms of misleading model output may still pass structural validation.

## Privacy limitations

The approved configuration is local by default, but local execution does not guarantee confidentiality.

Information could still be exposed through:

* Workstation compromise
* Browser extensions
* Terminal or PowerShell history
* Container or application logs
* Backups
* Misconfigured file permissions
* Remote model endpoints
* Operator error
* Improper Git commits

Changing `OLLAMA_HOST` to a remote endpoint changes the privacy boundary and may transmit prompts and retrieved evidence outside the workstation.

See `docs/privacy.md` and `docs/data-policy.md` before using the application.

## Deployment limitations

The reference deployment is a single-user local demonstration.

It does not include all controls expected for a production service, including:

* TLS termination
* Enterprise authentication or federation
* Centralized secrets management
* High availability
* Backup and recovery procedures
* Centralized monitoring and alerting
* Production log management
* Automated key rotation
* Network segmentation validation
* Web application firewall protection
* Formal capacity planning
* Disaster recovery testing
* Production support commitments

Binding the API beyond `127.0.0.1` or exposing it through a tunnel, proxy, local network, or the internet is outside the approved configuration.

## Performance limitations

Model-dependent requests can be slow and vary based on hardware, model state, prompt size, evidence size, and model availability.

The recorded evaluation reported a P95 latency of approximately 123 seconds. This does not establish a production service-level objective.

The local configuration limits concurrent model requests to reduce resource exhaustion. It is not designed for high-volume or multi-user workloads.

## Evaluation limitations

The deterministic test suite, automated model evaluation, Semgrep results, dependency auditing, container checks, and SBOM improve assurance but do not prove that the application is secure or correct.

The model-dependent evaluation currently contains a small number of scenarios and uses a specific local generation model, embedding model, source corpus, prompt version, schema version, and retrieval configuration.

Results may change when any of those components change.

The SBOM is a point-in-time inventory. Dependency findings and temporary risk acceptances are documented in `docs/dependency-risk-register.md`.

## Required human review

A qualified reviewer must verify, at minimum:

* The architecture description and assumptions
* The applicability and meaning of every citation
* Whether each risk follows from the described condition
* Whether each recommendation is supported by evidence
* Severity and prioritization
* Missing threats, assets, identities, boundaries, and integrations
* Alignment with organizational requirements
* Whether additional evidence or specialist review is required

A reviewer must reject unsupported findings rather than attempting to justify them from the presence of a citation.

## Prohibited uses

Do not use SecArch Copilot to:

* Approve an architecture
* Accept or transfer risk
* Determine compliance
* Produce an authoritative audit conclusion
* Make autonomous access-control decisions
* Trigger remediation without review
* Process real sensitive or restricted information
* Replace qualified security, privacy, legal, compliance, or risk professionals
* Operate an internet-facing or production service without a separate design and approval process
