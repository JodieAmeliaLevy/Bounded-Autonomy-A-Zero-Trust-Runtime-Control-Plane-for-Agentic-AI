# From Evals to Deployment: A Safety Case Pattern for Agentic Systems

For each important hazard, document:

1. **Hazard** — what bad outcome is being prevented?
2. **Risk pathway** — how can the system reach that outcome?
3. **Control objective** — what property must hold?
4. **Control mechanism** — what prevents or detects the pathway?
5. **Evaluation evidence** — what experiment supports the claim?
6. **Known failure modes** — where does the mechanism fail?
7. **Residual risk** — what remains after mitigation?
8. **Deployment decision** — allow, condition, restrict, or block?
9. **Monitoring / rollback** — what evidence after launch changes the decision?

The paper should include at least one worked example using measured results from ControlPlaneBench.
