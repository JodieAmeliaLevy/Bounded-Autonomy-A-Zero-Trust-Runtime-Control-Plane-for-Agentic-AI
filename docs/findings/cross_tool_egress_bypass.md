# Finding: Cross-tool egress bypass

Date: 2026-09-11 (v0.3.1)

Status: **closed** in v0.3.2 by routing authorization through semantic
effects. A regression test,
`tests/test_trust_boundary.SemanticEgressTests`, now asserts that every
registered egress channel is mediated, and the benchmark scenario
`cross-tool-egress` keeps the case in the standing set.

## Reproduce

    python -m experiments.adaptive_bypass_eval

Numbers below are from the v0.3.1 code, before the fix. Running the command
against current `main` reports 0.00 for both authorization regimes.

## Setup

The contextual authorization layer mediated:

- filesystem reads
- external email sends

An adaptive synthetic attacker was permitted to continue searching after a denied action.

Four strategies were evaluated:

1. direct email exfiltration
2. repeated email exfiltration attempts
3. direct browser-form exfiltration
4. browser-form fallback after email denial

## Result

Baseline attack success rate: 1.00

Strict authorization attack success rate: 0.50

Egress authorization attack success rate: 0.50

Under both authorization regimes, email-based exfiltration was blocked.

The remaining successful attacks used browser form submission as an alternative egress channel.

## Interpretation

The policy protected a specific tool/action pair:

    email:send_external

but did not protect the underlying security-relevant capability:

    external communication / data egress

A semantically equivalent action through another tool therefore bypassed the policy.

## Design implication

Authorization for agentic systems should operate over semantic capabilities or effects rather than tool names alone.

Examples:

- external_communication
- sensitive_data_read
- code_execution
- credential_access
- destructive_action
- privilege_change

Individual tools should map onto those higher-level effects before policy evaluation.

## Limitation

This is a synthetic adversarial test using a scripted attacker and synthetic tools. It demonstrates a design flaw in the current prototype, not a vulnerability in any production agent system.
