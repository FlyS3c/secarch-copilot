# SecArch Copilot Data Policy

## Scope
This policy applies to source documents, user input, prompts, embeddings, model output, logs, tests, screenshots, training data, and published repository content.

## Classification labels
- public: approved for the public repository and demonstrations
- internal-demo: synthetic project material kept locally unless explicitly reviewed for publication
- restricted: never used by this portfolio project

## Allowed data
- Public NIST, OWASP, MITRE, and official vendor documentation
- Open-license documents after license review
- Fictional architectures and synthetic test cases
- Original templates and notes written for this project
## Conditional data
Personal notes may be used only when I own them, rewrite them in my own words, remove identifiers, and confirm they contain no employer, customer, or licensed-course material.

## Prohibited data
- Employer or customer diagrams, tickets, configurations, IP addresses, logs, findings, or credentials
- Personal data, account numbers, secrets, tokens, or private keys
- SANS courseware, copied TryHackMe content, or other material I cannot republish
- The ai notebook.mht file itself

## Approval before ingestion
Every source requires an owner, source URL, license, version or retrieval date, SHA-256, classification, allowed roles, and approved=true in data/sources.yml.
## Storage and retention
Raw documents live under C:\SecArchCopilotData\raw. Rejected files live under quarantine. The Chroma database, processed text, and local logs remain outside Git. Delete superseded index versions after a tested rollback window.

## Logging
Log request ID, time, workflow, policy decision, source IDs, latency, and error category. Do not log full prompts, document text, secrets, or hidden model reasoning.

## Cloud transfer
Only public or synthetic data may be uploaded for optional LoRA training. Use a new least-privilege token, remove it after training, and delete the temporary compute instance.

## Incident response
If prohibited data is found: stop ingestion, quarantine it, remove it from indexes and Git history if necessary, rotate exposed secrets, record the event, and retest before continuing.

Owner: Glenn Merritt
Last reviewed: 2026-09-03
