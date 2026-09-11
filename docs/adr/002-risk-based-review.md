# ADR-002: Use risk-based human review rather than universal approval

**Status:** Accepted for v0.1

## Context
Universal human approval may reduce autonomy to the point of unusability. No review leaves high-impact actions vulnerable.

## Decision
Escalation should depend on action risk, authorization, provenance and monitor evidence.

## Consequences
- makes the safety/utility trade-off measurable;
- requires calibrated risk classification;
- reviewer burden becomes an explicit system metric.
