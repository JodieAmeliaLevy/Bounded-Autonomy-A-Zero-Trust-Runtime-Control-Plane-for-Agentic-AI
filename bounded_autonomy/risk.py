from __future__ import annotations

from .models import ActionRequest, RiskTier
from .semantics import SemanticCapability, classify_action


#: Risk floor implied by an action's security effect.
_CAPABILITY_FLOOR: dict[SemanticCapability, RiskTier] = {
    SemanticCapability.UNKNOWN: RiskTier.CRITICAL,
    SemanticCapability.PRIVILEGE_CHANGE: RiskTier.CRITICAL,
    SemanticCapability.RESOURCE_TRANSFER: RiskTier.CRITICAL,
    SemanticCapability.CODE_EXECUTION: RiskTier.HIGH,
    SemanticCapability.EXTERNAL_COMMUNICATION: RiskTier.HIGH,
    SemanticCapability.DESTRUCTIVE: RiskTier.HIGH,
    SemanticCapability.WRITE_RESOURCE: RiskTier.MEDIUM,
    SemanticCapability.READ_RESOURCE: RiskTier.LOW,
    SemanticCapability.DERIVE_DATA: RiskTier.LOW,
    SemanticCapability.INSPECT: RiskTier.LOW,
}

_ORDER = (RiskTier.LOW, RiskTier.MEDIUM, RiskTier.HIGH, RiskTier.CRITICAL)


def _max_tier(left: RiskTier, right: RiskTier) -> RiskTier:
    return left if _ORDER.index(left) >= _ORDER.index(right) else right


def classify_risk(action: ActionRequest) -> RiskTier:
    """
    Transparent risk classifier driven by declared security effect.

    An earlier version matched a hardcoded set of tool/action strings and
    returned LOW for everything it had not seen, so any tool absent from
    that set was waved through. Classification now starts from the effect
    registry, and an unregistered effect is CRITICAL.
    """

    semantics = classify_action(action)
    tier = _CAPABILITY_FLOOR.get(semantics.capability, RiskTier.CRITICAL)

    if not semantics.reversible:
        tier = _max_tier(tier, RiskTier.HIGH)

    if not action.user_authorized:
        tier = _max_tier(tier, RiskTier.HIGH)

    if any(not p.trusted for p in action.provenance):
        tier = _max_tier(tier, RiskTier.MEDIUM)

    return tier
