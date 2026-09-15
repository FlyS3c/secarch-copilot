# Privacy and Data Handling

Last reviewed: 2026-09-15

## Scope

SecArch Copilot is designed for controlled, local portfolio demonstrations using public, synthetic, or explicitly approved information.

It is not approved for employer data, customer data, personal information, credentials, production logs, internal architecture diagrams, restricted documents, or licensed material that has not been approved for this use.

## Information processed

The application may process:

* Synthetic system descriptions and architecture details entered by the user
* Approved public reference material listed in `data/sources.yml`
* Embeddings generated from approved reference material
* Retrieved reference chunks used to ground a response
* Model prompts and generated architecture-review or threat-model drafts
* A local API key supplied with an API request
* Operational metadata needed for security auditing

The application does not require real customer, employee, or production information.

## Local API key

The browser interface presents the API key as a password field. The key is sent in the `X-API-Key` request header to the locally configured API endpoint.

The frontend does not intentionally store the key in cookies, `localStorage`, or `sessionStorage`. The key may remain temporarily in browser memory while the page is open.

The default interface uses loopback HTTP communication with `127.0.0.1`. The API must not be exposed to a local network or the internet without TLS, stronger identity controls, and a separate security review.

## Local storage

Runtime data is stored beneath the directory configured by `SECARCH_DATA_ROOT`.

This can include:

* Approved raw source documents under the configured raw-data directory
* Chroma vector collections under the configured Chroma directory
* Audit records under the configured logs directory
* Locally generated embeddings and collection metadata

Raw source documents, Chroma data, model files, environment files, and audit logs are intentionally excluded from Git.

Generated responses are returned to the caller. The application does not provide a persistent conversation-history feature.

## Audit logging

Security audit events are designed to contain operational metadata rather than full user prompts, retrieved document text, model responses, API keys, or model reasoning.

Audit metadata may include items such as:

* Request identifiers and timestamps
* Workflow and authorization decisions
* Referenced source identifiers
* Retrieval and result counts
* Processing latency
* Error categories

Automated security tests verify that designated synthetic canary values and sensitive request content do not appear in audit records.

Application-server, container, operating-system, terminal, or browser logs may independently retain connection or command information. Users are responsible for protecting and clearing those records when appropriate.

## Model and retrieval processing

By default, generation and embedding requests are sent to an Ollama service configured on the local workstation. The container instructions use `host.docker.internal` to reach that local service.

`OLLAMA_HOST` is configurable. Pointing it to a remote service changes the privacy boundary and may send prompts, system descriptions, and retrieved reference evidence outside the workstation. Remote model services are outside the approved default configuration and require a separate privacy and security assessment.

Chroma runs as an embedded local client. SecArch Copilot explicitly constructs its Chroma clients with anonymized product telemetry disabled.

## External network activity

Normal local runtime operation is intended to use loopback or local-container communication.

Separate development and maintenance activities may access external services:

* Downloading approved public source documents
* Installing Python dependencies
* Pulling Ollama or container images
* Running GitHub Actions
* Running Semgrep analysis
* Querying package-vulnerability services through `pip-audit`

GitHub Actions and Semgrep may process repository source code, dependency metadata, workflow metadata, and security findings according to their respective service terms. They should not receive local runtime inputs unless someone improperly commits those inputs to the repository.

## Retention and deletion

The project does not claim automatic retention enforcement or log rotation.

Raw documents, vector collections, audit records, and locally installed models remain until the operator removes them. Before deleting runtime data, stop the application and verify the exact configured `SECARCH_DATA_ROOT` location.

Deleting a Chroma collection or raw source may require rebuilding the approved local index before the application can operate normally.

Git history, GitHub Actions records, Semgrep findings, and other third-party records are governed by their respective retention controls.

## User responsibilities

Users must:

* Use only public, synthetic, or explicitly approved information
* Keep `.env` files, API keys, model files, raw documents, Chroma data, and logs out of Git
* Keep the API bound to loopback interfaces
* Review every generated finding before relying on it
* Avoid using generated output for architecture approval, compliance decisions, risk acceptance, or autonomous remediation
* Review the configured model endpoint before submitting information
* Follow the source approval requirements in `docs/source-retrieval.md`

## Limitations

Local execution reduces external data exposure but does not by itself guarantee confidentiality. Workstation malware, browser extensions, terminal history, container logs, backups, remote model configuration, or operator error may expose information.

Citation validation confirms that a citation identifier came from retrieved evidence. It does not prove that every generated claim is semantically supported by that evidence.

See `docs/limitations.md`, `docs/data-policy.md`, and `SECURITY.md` for additional boundaries and reporting instructions.
