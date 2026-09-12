# ADR-004: The harness owns every security claim about an action

**Status:** Accepted

## Context

ADR-001 put authority outside model reasoning. That is undone if the model
is still the source of the facts authority is computed from.

The first implementation let the agent provider supply `provenance`,
`user_authorized` and `reversible` with each proposed tool call, and the
policy engine branched on all three. The scripted attackers happened to
report themselves honestly, so the controls appeared to work. See
docs/findings/agent_supplied_metadata_bypass.md.

## Decision

An agent proposes a tool name, an action and arguments. Nothing else.

The harness derives:

- **provenance** from the sources the session has ingested, with every
  environment untrusted unless it declares otherwise;
- **authority** from the user's mandate, supplied when the run starts;
- **reversibility** from the effect registry.

`ActionRequest.user_authorized` and `.reversible` default to the unsafe
assumption so that an unstamped request cannot be mistaken for a safe one.

## Consequences

- An attacker cannot improve its position by lying about itself; it can
  only change what it asks for.
- Every experiment must now state the mandate it ran under, which is a
  cost in setup and an improvement in interpretability.
- The mandate becomes the thing to attack. A mandate too broad to be
  useful, or too narrow to complete the task, is now the visible failure
  mode rather than a hidden one.
- A real deployment must elicit that mandate from a user. This project
  supplies it in the scenario file and does not claim to have solved
  elicitation.
