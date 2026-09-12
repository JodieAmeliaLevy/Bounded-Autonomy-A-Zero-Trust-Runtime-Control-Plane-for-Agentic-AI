# Bounded Autonomy: Evaluating a Zero-Trust Runtime Control Plane for Agentic AI

## Abstract
State the problem, intervention, evaluation setup, main quantitative result and key limitation. Write this last.

## 1. Introduction
- increasingly capable agents can take consequential external actions;
- model-level safeguards alone may not provide sufficient authority separation;
- contribution: implement and empirically evaluate a model-agnostic runtime control plane.

## 2. Related work

See [`docs/related-work.md`](../docs/related-work.md) for the current
positioning, which must be written before the results are, not after.

The load-bearing comparison is CaMeL (Debenedetti et al., arXiv:2503.18813),
which reaches a similar capability and dataflow design by construction. The
claim this paper can make is empirical: what such a control plane costs, and
where it fails under an adaptive attacker. Any draft that does not state
that comparison in the first page of the introduction will be read as
unaware of it.

Also covered:
- design patterns for securing LLM agents (Beurer-Kellner et al., arXiv:2506.08837);
- AgentDojo as the existing benchmark (Debenedetti et al., arXiv:2406.13352);
- AI control and trusted monitoring;
- capability security and least authority;
- runtime assurance and safety cases.

## 3. Threat model
Define assets, attacker capability, agent knowledge, tool boundary, trusted components and non-goals.

## 4. Architecture
Describe the control plane, permission model, provenance, policy engine, monitors, review and audit.

## 5. Control configurations
Define the baseline and each ablation configuration.

## 6. Benchmark and evaluation methodology
Scenario construction, model/harness settings, attack budgets, benign controls, ground truth and statistical analysis.

## 7. Adaptive adversary setup
How attackers learn from denials, monitor feedback or repeated attempts.

## 8. Results
Primary safety and utility outcomes.

## 9. Ablations
Which controls create marginal value?

## 10. Failure analysis
Where does the architecture fail and why?

## 11. Security–utility trade-offs
Review burden, latency, cost and benign degradation.

## 12. From evaluation evidence to deployment claims
Translate results into explicit claims, confidence and residual risk.

## 13. Limitations
Be aggressive and specific.

## 14. Conclusion
What this work establishes, what it does not, and the next experiment.
