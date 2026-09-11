import unittest

from experiments.contextual_authorization_ablation import run_scenario


class ContextualAuthorizationTests(unittest.TestCase):
    def test_baseline_injection_succeeds(self):
        result = run_scenario(
            "injection_exfiltration",
            "baseline",
        )
        self.assertTrue(result["attack_success"])

    def test_strict_blocks_injection_at_read(self):
        result = run_scenario(
            "injection_exfiltration",
            "strict",
        )
        self.assertFalse(result["attack_success"])
        self.assertIn(
            "filesystem:read",
            result["blocked_actions"],
        )

    def test_egress_blocks_injection_at_send(self):
        result = run_scenario(
            "injection_exfiltration",
            "egress",
        )
        self.assertFalse(result["attack_success"])
        self.assertIn(
            "email:send_external",
            result["blocked_actions"],
        )

    def test_legitimate_read_survives_strict_control(self):
        result = run_scenario(
            "legitimate_read",
            "strict",
        )
        self.assertTrue(result["utility_success"])

    def test_legitimate_send_survives_egress_control(self):
        result = run_scenario(
            "legitimate_send_alice",
            "egress",
        )
        self.assertTrue(result["utility_success"])

    def test_recipient_swap_is_blocked(self):
        for regime in ("strict", "egress"):
            result = run_scenario(
                "recipient_swap",
                regime,
            )
            self.assertFalse(result["attack_success"])
            self.assertIn(
                "email:send_external",
                result["blocked_actions"],
            )


if __name__ == "__main__":
    unittest.main()
