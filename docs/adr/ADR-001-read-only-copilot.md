# ADR-001: Build a read-only copilot first

Status: Accepted
Date: 2026-09-03

## Context
An autonomous agent would add tool permissions, external side effects, and more severe failure modes before the core retrieval controls are proven.

## Decision
Version 1 may draft threat models and architecture reviews but cannot execute commands, modify systems, send messages, or approve risk.

## Consequences
- Lower impact if the model is manipulated or wrong
- Clear human accountability
- Less automation in the first release

## Validation
Agency tests must prove that action requests are refused and returned only as drafts.
