# Berkeley 12 week work plan

## What changed and why

The previous version of this plan scheduled 30 to 50 new scenarios, three
model families, five control configurations, an adaptive adversary, a full
paper and three external reviewers, in twelve weeks, starting from a
scaffold with an unmediated trust boundary. That is roughly twice what the
time holds, and the breadth was the part least likely to produce anything
a reviewer would remember.

This version cuts scope in three places:

- **the benchmark**: run against AgentDojo, which already has 97 tasks and
  629 security test cases, rather than growing a private scenario set. The
  16 local scenarios stay as regression tests for this control plane's own
  boundary, not as a rival benchmark;
- **model coverage**: two model families run properly, with repeats and
  reported uncertainty, rather than three run once;
- **the deliverable**: one paper with one surprising, reproducible result,
  rather than a survey of five configurations.

One finding that survives adversarial review is worth more than a wide
sweep nobody can reproduce.

## Success criteria by 15 December 2026

- A control plane with a boundary that has been attacked, not just
  described, and a written failure catalogue.
- Results on an external benchmark, not only on scenarios written here.
- At least three control configurations plus a baseline, each reported with
  safety, utility and review burden in the same table.
- Repeated runs on at least two model families, with uncertainty reported.
- A paper quality write up and a reproducible release.
- At least three serious external technical reviewers, one of whom should
  know CaMeL well.

## Weeks 1 and 2 — position and connect

**Research**
- Write the related work section first. CaMeL (arXiv:2503.18813) reaches a
  similar design by construction; the empirical claim is what is left. If
  that comparison is not convincing, change the project now rather than in
  week 10.
- Freeze the threat model, the three research questions and explicit non
  goals.

**Build**
- Connect to AgentDojo and get the existing control plane running inside
  it. Expect this to take longer than it sounds.

**People**
- Five design conversations. Ask each person the same question: what
  assumption here is most likely to invalidate the project?

**Output**: related work note, a running AgentDojo integration, revised
threat model.

## Weeks 3 and 4 — real models

**Build**
- Harness configuration: model, system prompt, tool set, budget, retries,
  recorded per run.
- Replace the scripted planned agent with real models for every arm.

**Experiment**
- Baseline, static permissions, policy plus review, full control plane.
- Repeats per condition from the start, not added later.

**Output**: first results table with uncertainty, on an external benchmark.

## Weeks 5 and 6 — adaptive adversary

**Experiment**
- Tell the attacker that monitoring exists.
- Allow repeated attempts within a fixed budget.
- Hidden side task conditions.
- Delegation and subagent paths if the implementation supports them.

**Output**: failure catalogue, in the style of the existing findings
documents: what broke, the reproduce command, and the limitation.

## Weeks 7 and 8 — operational cost

Measure what the research questions promise and the current code does not:

- latency overhead per action and per task;
- token and API cost per task by configuration;
- human review burden, both escalations raised and reviewer decisions
  needed;
- monitor precision and recall, and whether a weak monitor is worth its
  cost at all. The current answer on local scenarios is no, which is a
  result worth establishing properly.

**Learn**: confidence intervals, sensitivity analysis, uncertainty
reporting.

## Weeks 9 and 10 — paper draft

Write the full paper. Sections as listed in `paper/outline.md`, with
related work already drafted from week 1 and limitations written
aggressively.

## Week 11 — adversarial review

- Send draft and repository to three reviewers.
- Ask each for the strongest reason the conclusions might be wrong.
- Rerun what is needed to answer them. Reserve the whole week for this;
  reviewers find things.

## Week 12 — release

- Tagged release with reproducibility instructions.
- Preprint.
- Two page technical summary.
- Safety case note.
- Fifteen minute talk.
- One public write up about the findings, including the ones that went
  against the hypothesis.

## Explicitly out of scope

- A production gateway or MCP proxy.
- Proving anything about the underlying model's alignment.
- Securing model weights.
- Solving prompt injection.
- A rival benchmark to AgentDojo.
