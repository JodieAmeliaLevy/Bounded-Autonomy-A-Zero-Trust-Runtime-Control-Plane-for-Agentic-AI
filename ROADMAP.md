# Berkeley 12-Week Work Plan

## Success criteria by 15 December 2026

- A runnable control-plane prototype with a clear security boundary.
- A public benchmark with at least 30 well-specified scenarios.
- At least 3 meaningful control configurations plus a baseline.
- Repeated experiments across at least 3 model families where access permits.
- Quantitative results on safety, utility, monitoring and review burden.
- A paper-quality write-up and reproducible release.
- At least 3 serious external technical reviewers.
- At least 10 substantive technical conversations that materially change the work.

## Week 1 — reproduce and specify

**Build**
- Run this starter project end-to-end.
- Reproduce one public control/monitorability experiment in a separate notebook or branch.
- Learn the tool protocol you will target first (preferably MCP or a similarly explicit tool boundary).

**Research**
- Freeze the first threat model.
- Freeze the first 3 research questions.
- Write explicit non-goals.

**People**
- 3–5 design conversations with control, evals or security researchers.
- Ask: “What assumption here is most likely to invalidate the project?”

**Output**
- `v0.0.1` release + architecture note.

## Week 2 — interception boundary

**Build**
- Intercept tool calls.
- Normalize actions into a typed schema.
- Add actor identity, task identity and provenance metadata.
- Persist audit events.

**Learn**
- async Python, typed interfaces, API boundaries, retries, idempotency.

**Output**
- ADR: why enforcement lives outside model reasoning.

## Week 3 — authority and escalation

**Build**
- Capability-scoped permissions.
- Risk tiers.
- Risk-dependent human approval.
- Explicit fail-open/fail-closed modes.
- Safe synthetic environments for filesystem/email/browser/shell.

**Learn**
- authentication vs authorization, least privilege, capability security, privilege escalation.

**People**
- security-engineer review.

## Week 4 — trusted monitoring

**Build**
- Pluggable monitor interface.
- At least one rule-based and one model-based monitor adapter.
- Structured monitor evidence in every decision.
- Synchronous vs asynchronous intervention modes.

**Output**
- `v0.1.0` demo.
- 10-minute Constellation technical talk.

## Week 5 — benchmark design

**Build**
- Create controlled environments with deterministic ground truth.
- Define scenario schema and attack budgets.

**Research**
- Expand taxonomy: injection, unauthorized action, escalation, exfiltration, chaining, side tasks, delegation, repeated attempts, monitor evasion.

**Output**
- Evaluation protocol v1.

## Week 6 — 30–50 scenarios

**Build**
- Implement scenarios and benign controls.
- Add reproducibility seeds and per-run metadata.

**People**
- evaluation-methodology review.

**Output**
- `ControlPlaneBench v0.1`.

## Week 7 — first model experiments

**Build**
- Connect multiple model providers where permitted.
- Add harness configuration: model, system prompt, tool set, budget, retries.

**Experiment**
- baseline: no external controls;
- static permissions;
- permissions + policy;
- policy + monitor;
- policy + monitor + human review.

**Output**
- first results table.

## Week 8 — adaptive adversary

**Experiment**
- Tell the attacker that monitoring exists.
- Permit repeated attempts within a fixed budget.
- Add hidden side-task conditions.
- Test subagent/delegation if implementation supports it.

**Output**
- failure catalogue: “how the control plane actually breaks.”

## Week 9 — operational measurements

Measure:
- attack success rate;
- benign-task completion;
- monitor recall / precision;
- false-positive rate;
- escalation rate;
- human-review burden;
- latency;
- token/API cost;
- time-to-detection/intervention.

**Learn**
- confidence intervals, calibration, sensitivity analysis, uncertainty reporting.

## Week 10 — paper draft

Write the full paper, not a blog post.

Sections:
1. problem;
2. threat model;
3. related work;
4. architecture;
5. control primitives;
6. evaluation methodology;
7. adaptive adversary;
8. results;
9. ablations;
10. utility/security trade-offs;
11. failure analysis;
12. deployment/safety-case implications;
13. limitations.

## Week 11 — adversarial review

- Send the draft and repo to 3 technical reviewers.
- Ask each reviewer for the strongest reason the conclusions might be wrong.
- Rerun experiments needed to answer those objections.

## Week 12 — release

Ship:
- tagged GitHub release;
- reproducibility instructions;
- benchmark;
- paper/preprint;
- 2-page technical summary;
- safety-case note;
- 15-minute talk deck;
- one public write-up focused on findings rather than career narrative.
