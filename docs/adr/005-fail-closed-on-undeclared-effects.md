# ADR-005: Undeclared effects fail closed

**Status:** Accepted

## Context

Risk was originally assigned by matching the capability string against two
hardcoded sets, with `RiskTier.LOW` for everything else. A tool the
classifier had never seen was therefore treated as the safest possible
action. Adding a tool to a deployment and forgetting to update the
classifier silently created an unmediated path.

Complete mediation is the assumption the whole architecture rests on
(ADR-001), and a default of LOW quietly breaks it.

## Decision

One registry, `EFFECT_REGISTRY` in `bounded_autonomy/semantics.py`, maps
each tool and action to a declared security effect and a reversibility
flag. It is the only place a tool acquires a security meaning.

A tool and action pair that is not in the registry classifies as
`SemanticCapability.UNKNOWN`, which is:

- `RiskTier.CRITICAL`;
- denied by the policy engine, whatever capability grants exist;
- never covered by a user mandate;
- counted as a damaging effect by the evaluation oracle.

## Consequences

- Adding a tool requires a deliberate, reviewable declaration of what it
  does. That is the point.
- Integration failures surface as denials rather than as silent allows,
  which is the correct direction for the error to point.
- The registry becomes a target: a wrong declaration is now a single point
  of failure, so it should be reviewed like a policy file and not like
  configuration.
- The benchmark scenario `unregistered-tool-egress` and the environment
  `SyntheticWebhook` exist to keep this case in the standing test set.
