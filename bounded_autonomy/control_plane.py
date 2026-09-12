from __future__ import annotations

from .audit import AuditLogger
from .escalation import HumanReviewQueue
from .models import ActionRequest, Decision, DecisionType
from .monitors import Monitor
from .policy import PolicyEngine
from .risk import classify_risk


class ControlPlane:
    def __init__(
        self,
        policy: PolicyEngine,
        monitor: Monitor,
        audit: AuditLogger | None = None,
        review_queue: HumanReviewQueue | None = None,
    ) -> None:
        self.policy = policy
        self.monitor = monitor
        self.audit = audit or AuditLogger()
        self.review_queue = review_queue or HumanReviewQueue()

    def evaluate(self, request: ActionRequest) -> Decision:
        risk = classify_risk(request)
        monitor_result = self.monitor.inspect(request)
        decision = self.policy.decide(request, risk, monitor_result)

        if decision.decision == DecisionType.ESCALATE:
            decision.review = self.review_queue.submit(request, decision)

        self.audit.write(request, decision)
        return decision
