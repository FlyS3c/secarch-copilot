# Retrieval Evidence Threshold Baseline

## Evaluation details

- Evaluation date: 2026-09-11
- Embedding model: embeddinggemma
- Chroma collection: secarch_knowledge_2026_09_09_v1
- Distance metric: Chroma collection default (L2)
- Relevant test queries: 10
- Irrelevant test queries: 10
- Results file: retrieval-threshold-20260911T110723Z.csv

## Results

- Largest relevant-query distance: 0.982052
- Smallest irrelevant-query distance: 1.433656
- Separation margin: 0.451604
- Selected maximum distance: 1.207854

## Decision

The selected threshold is the midpoint between the largest relevant-query
distance and the smallest irrelevant-query distance.

Retrieved chunks with a distance less than or equal to 1.207854 are accepted.
Chunks with a distance greater than 1.207854 are excluded before generation.

If no chunks remain after filtering, the application must abstain rather than
generate an unsupported architecture recommendation.

## Security rationale

This threshold helps prevent unrelated or weakly supported documents from
being supplied to the language model. It supplements, but does not replace,
the mandatory tenant, role, classification, approval, and deletion filters.

The threshold must be recalibrated whenever the embedding model, source
documents, chunking strategy, collection distance metric, or index version
changes.

## Limitations

This initial evaluation uses a small synthetic query set. The threshold will
be reevaluated as more representative architecture-review and threat-modeling
questions are added.