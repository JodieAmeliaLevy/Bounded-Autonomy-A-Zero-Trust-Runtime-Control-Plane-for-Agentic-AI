from __future__ import annotations

from .models import ActionRequest, RiskTier


_HIGH_RISK_ACTIONS = {
    "email:send_external",
    "filesystem:delete",
    "filesystem:write_sensitive",
    "shell:execute",
    "browser:submit_form",
}

_CRITICAL_ACTIONS = {
    "payments:transfer",
    "identity:change_permissions",
    "shell:execute_privileged",
}


def classify_risk(action: ActionRequest) -> RiskTier:
    """Simple transparent risk classifier used as a research baseline."""
    cap = action.capability
    if cap in _CRITICAL_ACTIONS:
        return RiskTier.CRITICAL
    if cap in _HIGH_RISK_ACTIONS:
        return RiskTier.HIGH
    if not action.reversible:
        return RiskTier.HIGH
    if not action.user_authorized:
        return RiskTier.HIGH
    if any(not p.trusted for p in action.provenance):
        return RiskTier.MEDIUM
    return RiskTier.LOW
