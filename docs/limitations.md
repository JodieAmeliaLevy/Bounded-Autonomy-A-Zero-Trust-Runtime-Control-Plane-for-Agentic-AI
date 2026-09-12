# Limitations and non-claims

Bounded Autonomy is an early research prototype. The current evidence is useful for comparing security abstractions inside a controlled harness; it is not sufficient to establish production security.

## What the current evidence does support

The synthetic experiments support narrow architectural claims:

- tool-specific authorization can fail under semantically equivalent cross-tool actions;
- semantic authorization can still fail when individually authorized actions compose into an impermissible information flow;
- exact-value sensitive-data tracking is brittle under simple transformations;
- persistent labels can survive the explicit transformations implemented inside a lineage-aware mediated environment;
- a control whose inputs are supplied by the component it constrains measures that component's honesty rather than the boundary's strength;
- classifying an unrecognised effect as low risk converts every integration gap into an unmediated path;
- stronger authorization can reduce human-review burden rather than increasing it, at least on this scenario set.

## What the current evidence does not support

The repository does **not** establish that:

- the control plane prevents arbitrary prompt injection or exfiltration;
- provenance cannot be stripped, copied, laundered or bypassed. Stripping through an unlabelled outbound channel is closed as of v0.4.0; stripping through the model's own context, where protected content is read, remembered and retyped, is not, and the evaluation oracle cannot see it either;
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

**Provenance stripping** was named here as the open failure mode, and v0.4.0 attacked it directly. Dropping the `artifact_id` and sending the raw value did bypass the guard. The guard now labels protected reads itself, and an outbound payload whose lineage cannot be established is denied once the session has touched protected data.

What remains open is the harder half of the same question: content that leaves the mediated substrate through the model's own context, rather than through an unlabelled tool argument. A label cannot follow information a model remembers, and the benchmark's oracle cannot detect a paraphrase either, so that case is currently invisible rather than handled. The scenario `transformation-paraphrase-unlabelled` is kept in the standing set so it is reported as a validity warning on every run.

## Evaluation scale

The current scenario count is small and deterministic. Reported booleans and attack-success rates should not be interpreted as population estimates. There are not yet repeated stochastic trials, confidence intervals or broad model-family comparisons.

Sixteen synthetic scenarios, written by the same author as the controls, run once each against environments written by the same author again. This measures whether the boundary holds against attacks that were thought of. It says nothing about attacks that were not, and it is not a substitute for an external benchmark such as AgentDojo.

The v0.3.x evaluation compared the policy engine against fields the scenario file itself declared, with a baseline of `return ALLOW`, five scenarios and one benign case. Those numbers should not be cited: they were arithmetic rather than measurement. [`docs/evaluation-protocol.md`](evaluation-protocol.md) records what replaced them and why.

## Real-model integration

The repository contains an experimental OpenAI Responses provider and a corresponding prompt-injection experiment. Real-model evaluation is not yet part of the published result set. It requires separate provider credentials and should be treated as optional experimental infrastructure.

## Utility and operational cost

v0.4.0 measures benign-task completion, over-blocking, escalation frequency and review burden alongside attack success, on synthetic scenarios. It does not yet measure:

- added latency;
- token/API cost;
- failure recovery;
- any of the above with a real model in the loop.

Those measurements are necessary before drawing deployment conclusions.

## Threat-model scope

The control plane assumes it can mediate the action boundary it is asked to govern. If a model or tool has an execution path outside that boundary, the architecture cannot enforce policy on that path.

The central research question is therefore not whether a wrapper can make an agent perfectly safe, but which **runtime security primitives remain meaningful as agent capabilities, tools and attack strategies become more adaptive**.
