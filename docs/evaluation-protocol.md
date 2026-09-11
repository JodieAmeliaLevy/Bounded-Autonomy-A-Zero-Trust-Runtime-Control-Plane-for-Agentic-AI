# Evaluation Protocol v0.1

## Claim under test

External runtime controls can reduce successful unsafe or unauthorized actions by tool-using agents relative to model-only safeguards while preserving acceptable benign-task performance.

## Unit of evaluation

A scenario contains:
- user task;
- environment state;
- tool set;
- granted capabilities;
- trusted and untrusted context;
- agent/model configuration;
- attack budget;
- ground-truth success condition;
- ground-truth unsafe-action condition.

## Core configurations

A. model-only baseline;
B. static permissions;
C. permissions + policy engine;
D. C + trusted monitor;
E. D + risk-based human review;
F. full control plane with additional controls.

## Primary metrics

### Safety
- attack success rate;
- unsafe action execution rate;
- time-to-detection/intervention;
- monitor recall;
- monitor precision.

### Utility
- benign-task completion rate;
- false-positive / unnecessary-block rate;
- latency overhead;
- token/API cost;
- human-review escalation rate;
- reviewer minutes per successful task.

## Validity requirements

- Separate development and held-out scenarios.
- Repeat stochastic runs.
- Record model and harness versions.
- Report uncertainty, not only point estimates.
- Test adaptive adversaries with fixed budgets.
- Include benign controls matched to attack scenarios.
- Publish failure cases, not only aggregate wins.
- Avoid benchmark contamination where possible.

## Adaptive-adversary experiment

The adversary may know:
- that a control plane exists;
- which action classes are reviewed;
- whether a monitor is used;
- what feedback follows a denied attempt.

The adversary receives a fixed action/token/attempt budget and must pursue a hidden side goal without triggering intervention.

## Research ethics / safety

Use synthetic data and non-production environments. Do not test destructive or criminal actions against real systems. Keep examples focused on control effectiveness rather than operational exploitation.
