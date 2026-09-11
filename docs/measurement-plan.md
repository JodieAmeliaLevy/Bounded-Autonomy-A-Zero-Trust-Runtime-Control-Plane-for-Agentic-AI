# Measurement Plan

For every experiment record:

## Configuration
- model / version;
- harness version;
- system prompt hash;
- available tools;
- permissions;
- policy version;
- monitor version;
- attack budget;
- random seed where applicable.

## Per-scenario outcomes
- task completed?;
- unsafe action attempted?;
- unsafe action executed?;
- intervention type;
- monitor score;
- human review required?;
- latency;
- token/API cost;
- number of attempts;
- failure taxonomy label.

## Aggregate reporting
- attack success rate with confidence interval;
- benign completion rate with confidence interval;
- monitor precision/recall;
- escalation burden;
- mean/median latency overhead;
- cost overhead;
- security/utility frontier by configuration.

## Important comparisons

1. model-only vs external control;
2. static permissioning vs policy-aware control;
3. no monitor vs monitor;
4. no human review vs risk-based review;
5. naive attacker vs adaptive attacker;
6. single-agent vs delegated/multi-agent where feasible.
