# ADR-001: Enforce action authority outside model reasoning

**Status:** Accepted for v0.1

## Context
Model-level instruction following is probabilistic and can be influenced by untrusted context. A safety architecture that asks the same model to decide whether it should obey itself creates a weak trust boundary.

## Decision
External tool actions must pass through a control-plane decision before execution.

## Consequences
- stronger separation between reasoning and authority;
- added latency and implementation complexity;
- security depends on complete mediation: unmediated tool paths are critical failures;
- permits independent evaluation of the control layer.
