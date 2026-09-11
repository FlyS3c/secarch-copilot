# SecArch Copilot Threat Model

## Scope
The local UI, FastAPI application, ingestion pipeline, Chroma database, Ollama service, model/adapters, source documents, logs, and optional cloud fine-tuning path.

## Protected assets
- Approved source content and classification metadata
- Embeddings and index integrity
- System prompts and output schemas
- Local tokens, configuration, and logs
- Evaluation results and model provenance

## Entry points
- User text input
- Uploaded or downloaded source documents
- Manifest changes
- API requests
- Model and dependency downloads
- Optional cloud dataset upload
## Risk scale
Likelihood: Low / Medium / High
Impact: Low / Medium / High
Overall: use professional judgment and explain the result.

## Threat register
| ID | Category | Scenario | Asset | Existing control | Likelihood | Impact | Treatment | Test |
|---|---|---|---|---|---|---|---|---|
| TM-01 | Spoofing | Caller supplies a different role in the request body | Restricted chunks | Role comes from authenticated context | Medium | High | Reject user-supplied identity fields | AUTH-01 |
| TM-02 | Tampering | Source document is changed after approval | Corpus integrity | SHA-256 and manifest approval | Medium | High | Recalculate hash and quarantine mismatch | POISON-01 |
| TM-03 | Information disclosure | Similarity search returns another tenant's chunk | Source content | Pre-query tenant filter | Medium | High | Negative authorization tests | AUTH-02 |
| TM-04 | Prompt injection | Retrieved text tells the model to ignore rules | Output integrity | Untrusted-context delimiters; no tools | High | Medium | Indirect-injection test set | INJ-02 |
| TM-05 | Denial of service | Oversized input or repeated requests exhausts the laptop | Availability | Size, token, timeout, rate, and concurrency limits | Medium | Medium | Resource-abuse tests | DOS-01 |
| TM-06 | Elevation of privilege | Model claims it can approve risk or make changes | Governance | Read-only capability and human review | Medium | High | Refusal and agency tests | AGENCY-01 |
| TM-07 | Supply chain | Malicious or mismatched model/adapter is imported | Laptop and output integrity | Approved source, exact revision, hashes, Safetensors, isolated test | Low | High | Provenance review | SC-01 |
| TM-08 | Misinformation | Unsupported recommendation appears authoritative | Decision quality | Citations, abstention, confidence, human review | High | High | Grounding evaluation | GROUND-01 |

## Residual risks
- Prompt injection cannot be eliminated solely with prompting.
- A local user with file-system access can tamper with runtime data.
- Small models may miss context or produce incorrect severity judgments.

## Review triggers
Revisit this model when adding users, network exposure, new data classes, cloud services, write-capable tools, or a new model/adapter.
