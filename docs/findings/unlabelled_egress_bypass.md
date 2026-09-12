# Finding: unlabelled egress bypassed lineage enforcement

Date: 2026-09-12

Status: **closed** on branch `fix/trust-boundary-and-evidence`.

## Setup

`LineageFlowGuard` was introduced in v0.3.5 to replace literal content
matching, which transformation defeats (see
[transformation_and_lineage.md](transformation_and_lineage.md)). It checks the label
on an artifact referenced by an outbound action.

Two properties of that implementation mattered more than the label logic:

- `observe()` returned `None`. Nothing in the system attached a label at
  run time. Labels existed only because the lineage environments created
  them and the scripted attacker chose to pass an `artifact_id`.
- `authorize()` returned `True, "no labeled artifact attached"` when the
  action carried no `artifact_id`.

## Result

Against the pre-change guard, with a protected artifact in the store:

    submit_artifact with artifact_id : (False, 'external action carries an artifact derived from protected data')
    submit_form with the raw value   : (True,  'no labeled artifact attached')

The plaintext is already in the transcript as the `content` field of the
read result, so an agent bypasses the guard by not mentioning the artifact.

## Interpretation

This is the cross tool egress bypass again, one layer down. The earlier
finding was that policy protected a tool name rather than an effect. This
one is that policy protected a data reference rather than the data, and
made carrying that reference optional for the party being constrained.

A control that only applies when the constrained component opts into it is
not a control.

## Fix

- `observe()` now runs on every executed action. When it sees a read of a
  protected resource it mints a labelled artifact, annotates the tool
  result and marks the session as having touched protected data.
- `authorize()` fails closed: once a session has touched protected data, an
  outbound action whose lineage cannot be established is denied unless the
  destination was explicitly delegated to receive sensitive material.
- `UserIntent` now separates `allowed_external_destinations` (may be
  contacted) from `sensitive_release_destinations` (may receive protected
  data). Conflating the two is how a legitimate status endpoint becomes an
  exfiltration channel, which is the one attack that still succeeds under
  `policy_review` in the benchmark.

## Reproduce

    python -m unittest tests.test_trust_boundary.UnlabelledEgressTests -v
    python -m evals.runner

## Limitation

Lineage is tracked over tool boundaries, not through the model's context.
An agent that reads protected content, remembers it and retypes a
paraphrase in a later argument is not caught by the label, and the
benchmark's oracle cannot see that case either. The scenario
`transformation-paraphrase-unlabelled` is kept in the set so this blind
spot is reported by the runner rather than quietly improving the numbers.
