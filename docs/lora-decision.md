# LoRA Experiment Decision

## Decision Information

- Date: 2026-09-15
- Status: Deferred
- Decision: LoRA is not selected for the current SecArch Copilot baseline.
- Next phase: Phase 7 containerization, continuous integration, and publication preparation.

## Context

The secured retrieval-augmented generation baseline is operational and has authorization-filtered retrieval, prompt boundaries, structured output validation, citation validation, audit logging, request limits, and fail-closed error handling.

The final evaluation produced these results:

- 100 deterministic tests passed.
- Application coverage was 82%.
- Three of three automated model-dependent cases passed.
- Schema validity was 100%.
- No unauthorized retrieval records were returned.
- No prompt-injection canary leaked.
- The injection case was securely blocked.
- Citation support was 0%.
- Grounded response or correct abstention was 50%.
- P95 model-dependent latency was 123,035 milliseconds.

## Rationale

The current weakness is semantic grounding rather than response structure. The model consistently produced valid JSON but created claims and recommendations that were not fully supported by their citations.

LoRA can improve repeatable response behavior and formatting, but it does not replace retrieval quality, stronger reasoning, or semantic claim-to-evidence validation. The structured-output goal is already being met, so paying for compute and creating a large training dataset is not currently justified.

The evaluation set also contains only three model-dependent cases. That is insufficient to identify a stable behavior that should be taught through fine-tuning or to measure whether an adapter improves performance without introducing regressions.

Training now could reinforce unsupported claims, overfit the small scenario set, or obscure weaknesses that should instead be addressed through retrieval, validation, evaluation, or base-model selection.

## Conditions for Reconsideration

LoRA may be reconsidered when all of the following conditions are met:

1. The model-dependent evaluation set contains at least 20 diverse architecture-review cases.
2. Model-dependent threat-model cases have been added.
3. A stronger compatible base model has been evaluated on the same cases.
4. Reranking or semantic claim-to-evidence validation has been tested.
5. A specific behavioral deficiency remains that LoRA is suited to improve.
6. A manually reviewed pilot dataset of 25 to 50 synthetic examples is available.
7. Dataset rights, exclusions, deduplication, split integrity, and quality-review criteria are documented.
8. Isolated compute, least-privilege credentials, model licensing, and artifact-integrity controls are prepared.

## Consequences

Sections 18.2 through 18.5 are deferred. No training dataset, cloud training environment, adapter, dataset card, or LoRA model card will be created during the current phase.

The secured RAG baseline will remain available for comparison. The project will proceed to Phase 7 as a controlled local demonstration that requires human review and is not approved for autonomous or production use.