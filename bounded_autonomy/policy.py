from __future__ import annotations

from dataclasses import dataclass

from .models import ActionRequest, Decision, DecisionType, MonitorResult, RiskTier
from .permissions import PermissionStore
from .provenance import has_untrusted_provenance


@dataclass
class PolicyConfig:
    deny_unpermitted: bool = True
    escalate_high_risk: bool = True
    deny_critical_without_user_authorization: bool = True
    escalate_untrusted_high_impact: bool = True
    monitor_threshold: float = 0.75


class PolicyEngine:
    def __init__(self, permissions: PermissionStore, config: PolicyConfig | None = None):
        self.permissions = permissions
        self.config = config or PolicyConfig()

    def decide(self, request: ActionRequest, risk: RiskTier, monitor: MonitorResult) -> Decision:
        reasons: list[str] = []

        if self.config.deny_unpermitted and not self.permissions.is_allowed(request):
            return Decision(DecisionType.DENY, risk, ["principal lacks required capability"], monitor)

        if (
            self.config.deny_critical_without_user_authorization
            and risk == RiskTier.CRITICAL
            and not request.user_authorized
        ):
            return Decision(DecisionType.DENY, risk, ["critical action lacks explicit user authorization"], monitor)

        if monitor.score >= self.config.monitor_threshold:
            return Decision(DecisionType.ESCALATE, risk, ["monitor score exceeded escalation threshold"], monitor)

        if self.config.escalate_untrusted_high_impact and has_untrusted_provenance(request) and risk in {
            RiskTier.HIGH,
            RiskTier.CRITICAL,
        }:
            return Decision(DecisionType.ESCALATE, risk, ["high-impact action depends on untrusted input"], monitor)

        if self.config.escalate_high_risk and risk in {RiskTier.HIGH, RiskTier.CRITICAL}:
            reasons.append("high-impact action requires review")
            return Decision(DecisionType.ESCALATE, risk, reasons, monitor)

        return Decision(DecisionType.ALLOW, risk, ["policy checks passed"], monitor)
