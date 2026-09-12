# Architecture

## Security boundary

Bounded Autonomy places authority over external action in a runtime layer outside the model's internal reasoning. The model may propose actions; it does not unilaterally authorize them.

The agent proposes a tool name, an action and arguments. Every other field
of the request is stamped by the harness (see
[ADR-004](adr/004-harness-owns-security-metadata.md)).

The control plane receives a normalized `ActionRequest` containing:
- principal identity;
- task identity;
- requested tool and operation;
- arguments;
- provenance of information that influenced the action;
- whether the user explicitly authorized the action;
- whether the action is reversible.

It produces one of three outcomes:
- **allow**;
- **deny**;
- **escalate** to trusted review, which executes only if a reviewer
  approves and fails closed when no reviewer is configured.

Action modification was previously listed here and in the decision enum. It
was never implemented, so it has been removed rather than left as a
placeholder that reads like a capability.

## Components

### 1. Action normalizer
Provider-specific tool calls are converted into a provider-neutral schema.

### 2. Permission store
Defines capabilities granted to each agent principal. This is intentionally more granular than granting an entire tool.

Example:
- `email:read`
- `email:draft`
- `email:send_external`

### 3. Provenance
Tracks whether data influencing the action came from trusted or untrusted sources. The initial implementation is intentionally simple; provenance is a major research surface.

### 4. Effect registry
`EFFECT_REGISTRY` in `semantics.py` is the only place a tool and action pair
acquires a security meaning. An undeclared pair is `UNKNOWN`, which is
treated as the most dangerous case, not the least
([ADR-005](adr/005-fail-closed-on-undeclared-effects.md)).

### 5. Risk classifier
Assigns a transparent risk tier from the declared effect, reversibility,
delegated authority and provenance.

### 6. Policy engine
Applies explicit rules to determine whether the action can proceed.

### 7. Trusted monitor
Provides an independent signal about suspicious intent or context. The starter monitor is heuristic and should be replaced or supplemented with stronger monitors.

### 8. Human review
High-risk or ambiguous actions can be escalated rather than allowed or denied automatically.

### 9. Execution environment
Synthetic Python objects. There is no sandbox, no container and no network
boundary in this repository. A real deployment would need all three, and
nothing here tests that assumption.

### 10. Audit layer
Every request and decision should be reconstructable after the fact.

## Research direction

The architecture is not the result. The result is whether this structure measurably reduces successful unsafe actions under increasingly realistic adversaries without making benign agents unusable.
