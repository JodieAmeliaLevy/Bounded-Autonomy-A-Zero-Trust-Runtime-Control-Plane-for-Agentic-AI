# Security Model

## Principle 1: authority is external to reasoning
The model may reason about an action but cannot grant itself permission to execute it.

## Principle 2: every action is explicit
Control requires a typed, inspectable action representation. Free-form side effects should be treated as a design smell.

## Principle 3: least privilege
Capabilities should be scoped by action, resource, duration and task where feasible.

## Principle 4: untrusted data does not become authority
Content retrieved from the environment should not be allowed to expand agent permissions.

## Principle 5: higher impact requires stronger evidence
Irreversible, externally visible or privilege-changing actions should face stronger checks.

## Principle 6: controls must fail predictably
The design must state when a component fails open, fails closed, or degrades to human review.

## Principle 7: evidence must be auditable
Every security decision should leave enough structured evidence to reconstruct why it happened.
