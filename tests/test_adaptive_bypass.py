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

    def test_browser_direct_reveals_egress_gap(self):
        result = run_attack(
            "browser_direct",
            "egress",
        )

        self.assertTrue(
            result["attack_success"]
        )

        self.assertEqual(
            result["exfiltration_channel"],
            "browser",
        )

    def test_browser_fallback_reveals_egress_gap(self):
        result = run_attack(
            "browser_fallback",
            "egress",
        )

        self.assertTrue(
            result["attack_success"]
        )

        self.assertIn(
            "email:send_external",
            result["blocked_actions"],
        )

        self.assertEqual(
            result["exfiltration_channel"],
            "browser",
        )


if __name__ == "__main__":
    unittest.main()
