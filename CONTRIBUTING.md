# Contributing to SecArch Copilot

Thank you for considering a contribution to SecArch Copilot.

This is an experimental, local security architecture and secure AI engineering project. Contributions must preserve its read-only design, data restrictions, authorization boundaries, human-review requirement, and non-production status.

## Before contributing

Read the following documents:

* `README.md`
* `SECURITY.md`
* `docs/data-policy.md`
* `docs/architecture.md`
* `docs/threat-model.md`
* `docs/evaluation-report.md`
* `docs/source-retrieval.md`

Report suspected vulnerabilities through the private process described in `SECURITY.md`. Do not disclose vulnerability details in a public issue or pull request.

## Data policy

Use only:

* Synthetic system descriptions
* Original project content
* Public information that has been reviewed for the intended use
* Approved source records from `data/sources.yml`

Never commit or submit:

* Employer or customer information
* Personal or regulated data
* Credentials, API keys, tokens, or `.env` files
* Production logs, configurations, hostnames, addresses, or diagrams
* Raw source documents
* Chroma databases or embeddings
* Model files or adapters
* Licensed course material
* Restricted documents
* Model outputs containing prohibited data

If prohibited data is discovered, stop work and follow the incident procedure in `docs/data-policy.md`.

## Development setup

The primary documented development environment is Windows with PowerShell and Python 3.14. Continuous integration validates the project on Linux with Python 3.12.

Clone the repository and create a virtual environment:

```powershell
git clone https://github.com/FlyS3c/secarch-copilot.git
Set-Location .\secarch-copilot

py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install `
  --require-hashes `
  --requirement .\requirements-dev.txt
```

Copy the example configuration:

```powershell
Copy-Item .\.env.example .\.env
```

Replace the example API key with a randomly generated local value. Do not commit `.env`.

Follow `docs/source-retrieval.md` if your change requires the local approved corpus. Most deterministic tests do not require a running Ollama service.

## Branch and commit process

Create a focused branch from an up-to-date `main` branch:

```powershell
git switch main
git pull --ff-only
git switch -c type/short-description
```

Use a descriptive branch prefix such as:

* `feature/`
* `fix/`
* `security/`
* `test/`
* `docs/`
* `build/`
* `ci/`

Keep commits focused and use clear messages such as:

```text
fix: reject incomplete retrieval results
test: add cross-tenant retrieval coverage
docs: explain source approval process
```

Do not combine unrelated formatting, dependency, feature, and documentation changes in one commit.

## Coding expectations

Contributions should:

* Preserve authorization outside the language model
* Apply authorization filters before vector ranking
* Treat user input, retrieved text, and model output as untrusted
* Retain structured request and response validation
* Validate citations against retrieved evidence
* Fail closed when security validation cannot complete
* Avoid logging prompts, source text, secrets, or hidden reasoning
* Avoid write-capable tools or automatic remediation
* Use explicit types and clear error handling
* Keep security decisions documented and testable
* Remain compatible with the configured Ruff Python target

Do not suppress security-tool findings without a documented reason, scope, owner, review date, compensating controls, and expiration or remediation trigger.

## Formatting and static analysis

Run:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy app
python -m bandit -r app scripts
```

To apply approved Ruff fixes:

```powershell
python -m ruff check . --fix
python -m ruff format .
```

Review all automated changes before committing them.

## Tests

Run the deterministic test suite with coverage:

```powershell
python -m pytest `
  --cov=app `
  --cov-report=term-missing `
  --cov-fail-under=80
```

New behavior should include appropriate tests. Security-sensitive changes should include negative and fail-closed cases, including tests for relevant authorization, injection, leakage, validation, or resource-limit boundaries.

The deterministic test suite must not require a live Ollama service or external network access.

## Model-dependent evaluation

Changes to prompts, retrieval, response schemas, model configuration, citation validation, or grounding behavior require a new model-dependent evaluation:

```powershell
python .\scripts\run_model_evaluation.py
```

Retain the result needed to support the documented decision and update `docs/evaluation-report.md` when conclusions, model versions, prompt hashes, schema hashes, latency, or limitations change.

Passing automated citation checks is not sufficient evidence of semantic grounding. Human review remains required.

## Source contribution and approval

Do not commit raw reference documents.

To propose a source:

1. Confirm that it is relevant to the project’s intended workflows.
2. Record its authoritative and retrieval URLs.
3. Record its publisher, version, retrieval date, file type, and local relative path.
4. Review its license or applicable publication terms.
5. Assign its classification, tenant, and allowed roles.
6. Calculate its SHA-256 value.
7. Document its intended use and any restrictions.
8. Add it to `data/sources.yml` with `approved: false`.
9. Update `docs/source-retrieval.md`.
10. Request review before changing the record to `approved: true`.

A source must not be parsed, embedded, indexed, or used for retrieval while it is unapproved.

The SABSA records currently in the manifest are restricted and reference-only. Do not enable or use them without written permission from the applicable rights holders.

## Dependency changes

Make direct dependency changes in:

* `requirements.in`
* `requirements-dev.in`

Regenerate the applicable hash-locked requirement files for each supported platform. Do not manually change only a transitive dependency inside a compiled lock file.

Dependency pull requests must include:

* Reason for the change
* Version change
* Compatibility impact
* Vulnerability or license impact
* Updated Windows and Linux lock files when applicable
* Successful tests and container build
* Updated SBOM when the container contents change

Known or accepted dependency risks must be documented in `docs/dependency-risk-register.md`.

## Container changes

For Docker-related changes:

```powershell
docker build `
  --tag secarch-copilot:local `
  .

docker image inspect secarch-copilot:local `
  --format 'User={{.Config.User}} OS={{.Os}} Architecture={{.Architecture}}'

docker run --rm `
  --entrypoint id `
  secarch-copilot:local
```

The final image must continue to use the non-root `secarch` user. Do not copy `.env`, raw documents, logs, indexes, credentials, test artifacts, or development tools into the runtime image.

Regenerate and review the CycloneDX SBOM after changing runtime dependencies or container contents.

## Documentation changes

Keep documentation consistent with implemented behavior. Do not claim that the project is production-ready, fully secure, compliant, grounded, or resistant to all prompt-injection attacks.

Update related architecture decisions, policies, evaluation evidence, limitations, source instructions, and examples when a change affects them.

Use synthetic values in commands, screenshots, fixtures, reports, and examples.

## Pull request checklist

Before submitting a pull request, confirm:

* [ ] The change has a focused purpose.
* [ ] No sensitive, restricted, licensed, or production data is included.
* [ ] `.env`, credentials, raw sources, models, indexes, and logs remain outside Git.
* [ ] Ruff lint and formatting checks pass.
* [ ] Mypy passes.
* [ ] Bandit passes or findings are documented.
* [ ] Deterministic tests pass with at least 80% application coverage.
* [ ] Relevant negative and security tests were added.
* [ ] Model-dependent evaluation was rerun when required.
* [ ] Dependency locks and the SBOM were updated when required.
* [ ] Documentation reflects the implemented behavior and known limitations.
* [ ] `git diff --check` returns no errors.

## Review

Changes may be declined if they weaken security boundaries, introduce unapproved data, create unsupported production expectations, lack required tests, or conflict with the project’s documented scope.
