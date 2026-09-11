# Bounded Autonomy

**A zero-trust runtime control plane for agentic AI.**

Bounded Autonomy is a research and engineering project for testing whether model-agnostic runtime controls can reduce unsafe or unauthorized agent actions while preserving useful task performance.

The project treats an AI agent as a potentially fallible or compromised principal. Proposed tool actions are intercepted before execution and evaluated against explicit authority, provenance, risk, monitoring, and escalation rules.

## Research objective

> How effectively can a model-agnostic runtime control plane prevent unauthorized or harmful actions by increasingly autonomous AI agents while preserving useful task performance?

The repository is designed to support three empirical questions:

1. **Control effectiveness** — which runtime controls most reduce unsafe or unauthorized actions?
2. **Robustness** — do controls remain effective under prompt injection, privilege escalation, tool chaining, monitor evasion, and delegated/subagent behavior?
3. **Cost of control** — what utility, latency, compute, and human-review costs accompany stronger controls?

## Architecture

```text
User intent
    ↓
Agent / model
    ↓
Proposed tool action
    ↓
┌──────────────────────────────────────────────┐
│          BOUNDED AUTONOMY CONTROL PLANE      │
│                                              │
│ action normalisation                         │
│   ↓                                          │
│ identity / permission check                  │
│   ↓                                          │
│ provenance / trust check                     │
│   ↓                                          │
│ risk classification                          │
│   ↓                                          │
│ policy engine                                │
│   ↓                                          │
│ trusted monitor                              │
│   ↓                                          │
│ allow / deny / modify / escalate             │
└──────────────────────────────────────────────┘
    ↓
Human approval when required
    ↓
Sandboxed / controlled execution
    ↓
Audit log + monitoring
```

## What is implemented in this starter repository

This is a deliberately small but runnable research scaffold. It includes:

- typed action and decision objects;
- least-privilege tool permissions;
- risk tiers;
- trusted vs. untrusted provenance handling;
- policy enforcement;
- a pluggable monitoring interface;
- human-review escalation hooks;
- an append-only JSONL audit log;
- synthetic email, filesystem, browser and shell environments;
- a baseline-vs-control-plane evaluation runner;
- starter adversarial scenarios;
- a research protocol, threat model, measurement plan, ADRs and paper outline;
- CI tests suitable for GitHub.

The current repository **does not claim production security**. It is the starting point for a Berkeley research build whose purpose is to make the assumptions explicit, implement the control boundary, and measure where it fails.

## Quick start

Requires Python 3.11+.

```bash
python -m bounded_autonomy.cli demo
python -m bounded_autonomy.cli eval
python -m unittest discover -s tests -v
```

The eval command writes results to `results/`.

## Suggested October–December build sequence

### Phase 1 — control plane (weeks 1–4)
- replace the synthetic action adapter with a real agent/tool protocol integration;
- implement an MCP gateway or equivalent tool-call proxy;
- add capability-scoped permissions, authenticated principals and action schemas;
- add policy state, denial reasons, structured escalation and durable logging;
- add container/network sandboxing and explicit fail-open/fail-closed behavior;
- demo v0.1 to technical reviewers.

### Phase 2 — benchmark (weeks 5–8)
- expand to 30–50 realistic scenarios;
- add prompt injection, privilege escalation, exfiltration, chained actions, side tasks, repeated-attempt attacks and monitor evasion;
- integrate real frontier/open-weight models;
- compare baseline, static permissions, policy enforcement, monitoring, and human review;
- add benign-task controls and repeat runs.

### Phase 3 — evidence (weeks 9–12)
- measure attack success, benign utility, monitor precision/recall, escalation burden, latency and cost;
- run ablations and adaptive-adversary experiments;
- publish the implementation, benchmark and paper;
- obtain external technical review before making strong claims.

## Core outputs

1. **Bounded Autonomy** — runtime control-plane implementation.
2. **ControlPlaneBench** — adversarial benchmark for tool-using agents.
3. **Flagship paper** — *Bounded Autonomy: Evaluating a Zero-Trust Runtime Control Plane for Agentic AI*.
4. **Safety-case note** — *From Evals to Deployment: A Safety Case Pattern for Agentic Systems*.

See [`ROADMAP.md`](ROADMAP.md) for the detailed work plan.

## Repository principles

- Controls should live outside model reasoning when possible.
- Every security claim must state its threat assumptions.
- Safety results must be paired with benign-task utility.
- Adaptive attackers matter more than one-shot prompts.
- A control that cannot be audited is difficult to govern.
- A benchmark that cannot be reproduced is weak evidence.

## Author

Jodie Levy — Constellation Visiting Fellow, Berkeley (October–December 2026)

## License

MIT. Research outputs may later use a different publication license if required by collaborators or venues.
