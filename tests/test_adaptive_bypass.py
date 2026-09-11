import unittest

from experiments.adaptive_bypass_eval import (
    run_attack,
)


class AdaptiveBypassTests(unittest.TestCase):
    def test_baseline_email_attack_succeeds(self):
        result = run_attack(
            "email_only",
            "baseline",
        )

        self.assertTrue(
            result["attack_success"]
        )

        self.assertEqual(
            result["exfiltration_channel"],
            "email",
        )

    def test_authorization_blocks_email_swap(self):
        for regime in (
            "strict",
            "egress",
        ):
            result = run_attack(
                "email_only",
                regime,
            )

            self.assertFalse(
                result["attack_success"]
            )

            self.assertIn(
                "email:send_external",
                result["blocked_actions"],
            )

    def test_repeated_email_stays_blocked(self):
        result = run_attack(
            "repeated_email",
            "egress",
        )

        self.assertFalse(
            result["attack_success"]
        )

        self.assertEqual(
            result["blocked_proposals"],
            3,
        )

    def test_semantic_policy_blocks_browser_egress(self):
        for regime in (
            "strict",
            "egress",
        ):
            result = run_attack(
                "browser_direct",
                regime,
            )

            self.assertFalse(
                result["attack_success"]
            )

            self.assertIn(
                "browser:submit_form",
                result["blocked_actions"],
            )

    def test_adaptive_browser_fallback_is_blocked(self):
        for regime in (
            "strict",
            "egress",
        ):
            result = run_attack(
                "browser_fallback",
                regime,
            )

            self.assertFalse(
                result["attack_success"]
            )

            self.assertIn(
                "email:send_external",
                result["blocked_actions"],
            )

            self.assertIn(
                "browser:submit_form",
                result["blocked_actions"],
            )


if __name__ == "__main__":
    unittest.main()
