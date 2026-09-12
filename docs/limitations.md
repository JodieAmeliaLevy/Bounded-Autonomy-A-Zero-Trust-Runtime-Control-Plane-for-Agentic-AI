# Limitations and non-claims

Bounded Autonomy is an early research prototype. The current evidence is useful for comparing security abstractions inside a controlled harness; it is not sufficient to establish production security.

## What the current evidence does support

The synthetic experiments support narrow architectural claims:

- tool-specific authorization can fail under semantically equivalent cross-tool actions;
- semantic authorization can still fail when individually authorized actions compose into an impermissible information flow;
- exact-value sensitive-data tracking is brittle under simple transformations;
- persistent labels can survive the explicit transformations implemented inside a lineage-aware mediated environment.

## What the current evidence does not support

The repository does **not** establish that:

- the control plane prevents arbitrary prompt injection or exfiltration;
- provenance cannot be stripped, copied, laundered or bypassed;
- arbitrary model-internal reasoning or transformation preserves lineage;
- the current policy language is complete;
- a determined adaptive model cannot discover unmodelled channels;
- the controls preserve acceptable utility at realistic scale;
- the monitor, policy engine or human-review layer is secure against compromise;
- the architecture is ready for production deployment.

## Synthetic environments

Most current experiments use deterministic scripted providers and synthetic filesystem, email, browser and transformation environments. This is intentional: the first objective is to isolate architectural failure modes without confounding them with model variance.

The cost is external validity. Real models may:

- choose different action sequences;
- exploit representations not anticipated by the harness;
- use tool outputs in unanticipated ways;
- encode or summarize protected information internally;
- exploit missing tools, side channels or state;
- fail benign tasks because of control friction.

## Transformation experiment

The base64, reverse and chunk results are direct tests of exact-string tracking and are reproducible in the harness.

The current `paraphrase` strategy is synthetic and its v0.3.4 success predicate is qualitative. It should therefore be treated as a design illustration, not as a rigorous measurement of semantic exfiltration.

## Lineage assumptions

The lineage result depends on computation remaining inside a mediated substrate that carries artifact identity and labels forward. The implementation currently trusts the transform environment to create derived artifacts with inherited labels.

An important open failure mode is **provenance stripping**: if protected content crosses into an unlabelled raw value or an unmediated channel, the current lineage guard may not know that the outbound value descends from protected data.

This is a research target, not a hidden assumption.

## Evaluation scale

The current scenario count is small and deterministic. Reported booleans and attack-success rates should not be interpreted as population estimates. There are not yet repeated stochastic trials, confidence intervals or broad model-family comparisons.

## Real-model integration

The repository contains an experimental OpenAI Responses provider and a corresponding prompt-injection experiment. Real-model evaluation is not yet part of the published result set. It requires separate provider credentials and should be treated as optional experimental infrastructure.

## Utility and operational cost

The current work emphasizes enforcement correctness and failure discovery. It does not yet provide a complete measurement of:

- benign-task completion;
- false positives;
- escalation frequency;
- human-review burden;
- added latency;
- token/API cost;
- failure recovery.

Those measurements are necessary before drawing deployment conclusions.

## Threat-model scope

The control plane assumes it can mediate the action boundary it is asked to govern. If a model or tool has an execution path outside that boundary, the architecture cannot enforce policy on that path.

The central research question is therefore not whether a wrapper can make an agent perfectly safe, but which **runtime security primitives remain meaningful as agent capabilities, tools and attack strategies become more adaptive**.
