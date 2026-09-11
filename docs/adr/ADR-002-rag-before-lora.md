# ADR-002: Establish secured RAG before LoRA

Status: Accepted
Date: 2026-09-03

## Context
RAG supplies current cited evidence. LoRA is better suited to repeatable behavior and format than to storing changing security facts.

## Decision
Build and measure base-model, RAG, and secured-RAG baselines before training an adapter. Keep the adapter only if the same evaluation set proves improvement without added security failures.

## Consequences
- More defensible comparison
- Fine-tuning can be deferred without blocking the useful product
- A valid project result may be that LoRA is not selected
