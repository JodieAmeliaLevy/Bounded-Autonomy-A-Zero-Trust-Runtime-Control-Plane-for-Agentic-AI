# Related work

This project is not the first to argue that authority over an agent's
actions should sit outside the model. The nearest work reaches a very
similar architecture by a different route, and the honest position is that
Bounded Autonomy's contribution is empirical rather than architectural.

## CaMeL

Edoardo Debenedetti, Ilia Shumailov, Tianqi Fan, Jamie Hayes, Nicholas
Carlini, Daniel Fabian, Christoph Kern, Chongyang Shi, Andreas Terzis and
Florian Tramèr, *Defeating Prompt Injections by Design*, arXiv:2503.18813.
<https://arxiv.org/abs/2503.18813>

> "Large Language Models (LLMs) are increasingly deployed in agentic
> systems that interact with an untrusted environment. However, LLM agents
> are vulnerable to prompt injection attacks when handling untrusted data."

CaMeL separates control flow and data flow from the model and enforces a
capability and dataflow policy outside it. The v0.3.5 lineage design in
this repository arrives at the same family of mechanism, independently and
later. Anyone reviewing this project should read CaMeL first.

**Where this project differs.** CaMeL argues largely by construction: the
design makes a class of attack impossible under stated assumptions. This
project starts from the opposite end, by building a control plane that is
deliberately ordinary and then measuring where it breaks under adaptive
pressure, including bypasses in its own earlier versions. The interesting
output is the failure catalogue and the security-utility frontier, not the
architecture.

## Design patterns for securing LLM agents

Luca Beurer-Kellner, Beat Buesser, Ana-Maria Creţu, Edoardo Debenedetti,
Daniel Dobos, Daniel Fabian, Marc Fischer, David Froelicher, Kathrin
Grosse, Daniel Naeff, Ezinwanne Ozoani, Andrew Paverd, Florian Tramèr and
Václav Volhejn, *Design Patterns for Securing LLM Agents against Prompt
Injections*, arXiv:2506.08837. <https://arxiv.org/abs/2506.08837>

> "Among the most pressing threats are prompt injection attacks, which
> exploit the agent's reliance on natural language inputs -- an especially
> dangerous threat when agents are granted tool access or handle sensitive
> information."

This catalogues the pattern space that this repository has been
rediscovering one commit at a time. Each control configuration in
`evals/harness.py` should be named against a pattern in that paper rather
than invented afresh.

## AgentDojo

Edoardo Debenedetti, Jie Zhang, Mislav Balunović, Luca Beurer-Kellner,
Marc Fischer and Florian Tramèr, *AgentDojo: A Dynamic Environment to
Evaluate Prompt Injection Attacks and Defenses for LLM Agents*,
arXiv:2406.13352. <https://arxiv.org/abs/2406.13352>

> "We populate the environment with 97 realistic tasks (e.g., managing an
> email client, navigating an e-banking website, or making travel
> bookings), 629 security test cases"

A benchmark of this shape already exists with far more coverage than this
repository will build from scratch. The 16 synthetic scenarios in
`evals/scenarios.json` exist to exercise this control plane's own boundary
conditions and to keep its regressions visible; they are not a rival
benchmark and should not be presented as one.

**Planned use.** Run the control plane against AgentDojo rather than
extending the local scenario set, and contribute the cases AgentDojo does
not cover, which are the ones this project keeps finding by accident:
semantically equivalent egress through a second tool, retry after denial
within one task, effects the deployment never declared, and the gap
between a destination being contactable and being cleared to receive
sensitive data.

## Still to write up

- AI control and trusted monitoring, and what a monitor is worth when it
  is weaker than the agent it watches. The heuristic monitor in this
  repository adds nothing over policy alone in the current benchmark,
  which is a reason to characterise the claim properly rather than to ship
  a better monitor.
- Capability security and the object-capability literature, which is where
  the permission model comes from.
- Runtime assurance and safety cases, for the deployment-claims chapter.
