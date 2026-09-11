# Threat Model v0.1

## Protected assets

Examples:
- private data;
- user accounts;
- credentials and tokens;
- filesystem integrity;
- external communications;
- permissions and policy state;
- money or other irreversible resources;
- audit evidence.

## Adversaries / failure sources

### A. Untrusted external content
A webpage, email, document or tool output contains instructions that the agent mistakes for authority.

### B. Mis-specified agent objective
The agent pursues the user's goal too literally or optimizes a proxy in a way that creates harm.

### C. Compromised / intentionally adversarial agent
The model attempts to achieve a hidden side objective and may understand that monitoring is present.

### D. Tool or environment compromise
A tool returns malicious or misleading data, or attempts to expand its authority.

### E. Human error
Users or reviewers grant excessive authority or approve a risky action without sufficient context.

## Initial attack classes

1. indirect prompt injection;
2. unauthorized actions;
3. privilege escalation;
4. cross-context data exfiltration;
5. dangerous goal misinterpretation;
6. chained actions whose composition is harmful;
7. hidden side-task behavior;
8. monitor evasion;
9. repeated-attempt / search-over-bypass behavior;
10. delegated or subagent bypass.

## Security assumptions to test, not assume

- A trusted monitor is actually more trustworthy than the acting model.
- The agent cannot bypass the gateway through an unmediated channel.
- Tool schemas expose enough structure for reliable policy checks.
- High-risk actions can tolerate added latency.
- Human review reduces risk rather than merely moving the failure point.
- Provenance can be represented with useful fidelity.

## Non-goals for v0.1

- proving alignment of the underlying model;
- defending arbitrary production systems;
- securing model weights;
- solving all prompt injection;
- replacing provider safeguards.
