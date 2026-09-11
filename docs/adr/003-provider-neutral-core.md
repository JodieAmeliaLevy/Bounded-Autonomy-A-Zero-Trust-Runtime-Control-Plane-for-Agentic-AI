# ADR-003: Keep the core control plane provider-neutral

**Status:** Accepted for v0.1

## Context
The research question concerns agentic control, not one model vendor's API semantics.

## Decision
Provider-specific calls are normalized into a common action schema before policy evaluation.

## Consequences
- enables cross-model experiments;
- requires careful adapters to avoid losing provider-specific semantics;
- improves reproducibility and comparability.
