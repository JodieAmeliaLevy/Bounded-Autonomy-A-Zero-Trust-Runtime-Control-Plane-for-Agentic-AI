# Architecture

## Security boundary

Bounded Autonomy places authority over external action in a runtime layer outside the model's internal reasoning. The model may propose actions; it does not unilaterally authorize them.

The control plane receives a normalized `ActionRequest` containing:
- principal identity;
- task identity;
- requested tool and operation;
- arguments;
- provenance of information that influenced the action;
- whether the user explicitly authorized the action;
- whether the action is reversible.

It produces one of four outcomes:
- **allow**;
- **deny**;
- **escalate** to trusted review;
- **modify** the proposed action (planned extension).

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

### 4. Risk classifier
Assigns a transparent risk tier using action type, reversibility, authorization and provenance.

### 5. Policy engine
Applies explicit rules to determine whether the action can proceed.

### 6. Trusted monitor
Provides an independent signal about suspicious intent or context. The starter monitor is heuristic and should be replaced or supplemented with stronger monitors.

### 7. Human review
High-risk or ambiguous actions can be escalated rather than allowed or denied automatically.

### 8. Execution environment
Real deployment should execute tools in isolated environments with explicit network/filesystem boundaries.

### 9. Audit layer
Every request and decision should be reconstructable after the fact.

## Research direction

The architecture is not the result. The result is whether this structure measurably reduces successful unsafe actions under increasingly realistic adversaries without making benign agents unusable.
