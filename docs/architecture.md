# SecArch Copilot Architecture

## Context
A local, read-only security copilot produces cited drafts. The language model is not trusted to enforce access control or approve decisions.

## Components
1. Browser UI - collects sanitized input and displays structured results.
2. FastAPI - validates requests, authenticates the local user, applies limits, and logs control events.
3. Retrieval service - builds mandatory authorization filters before querying Chroma.
4. Chroma - stores embeddings, text chunks, and security metadata.
5. Ollama - creates embeddings and generates structured responses.
6. Ingestion pipeline - validates manifests, quarantines files, parses, chunks, embeds, and versions the index.
7. Evaluation suite - tests authorization, injection, leakage, grounding, output handling, and resource limits.
## Data flow
1. User submits a sanitized system description.
2. API obtains tenant, role, and clearance from authenticated local configuration, not from the request body.
3. Retrieval service applies tenant, allowed_roles, classification_rank, and approved filters.
4. Chroma ranks only eligible chunks.
5. Prompt builder labels retrieved chunks as untrusted reference data.
6. Ollama returns JSON constrained by a schema.
7. Pydantic validates the result before the UI escapes and displays it.

## Trust boundaries
- User to API
- Raw source to ingestion pipeline
- Retrieval result to model prompt
- Model output to application
- Local laptop to optional cloud training

## Deployment
Version 1 runs on one Windows laptop. FastAPI and Ollama bind to 127.0.0.1. Runtime data is stored under C:\SecArchCopilotData.
## Security decisions
- Authorization occurs outside the model and before vector ranking.
- Version 1 has no write-capable tools.
- Source and index versions are traceable by checksum.
- Prompts contain no secrets.
- Logs contain metadata rather than sensitive content.
- Human review is required for every deliverable.

## Open questions
- What relevance threshold performs best on the evaluation set?
- Which small local model provides the best grounded output?
- Does LoRA improve format consistency without increasing security failures?
