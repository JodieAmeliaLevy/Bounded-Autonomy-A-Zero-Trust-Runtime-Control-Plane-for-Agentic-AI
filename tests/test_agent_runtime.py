import unittest

from experiments.prompt_injection_e2e import run_once


class AgentRuntimeTests(unittest.TestCase):
    def test_baseline_exfiltrates_secret(self):
        result = run_once(controlled=False)

        self.assertTrue(result["exfiltrated"])
        self.assertIn("email:send_external", result["executed_actions"])

    def test_control_plane_prevents_exfiltration(self):
        result = run_once(controlled=True)

        self.assertFalse(result["exfiltrated"])
        self.assertTrue(len(result["blocked_actions"]) > 0)


if __name__ == "__main__":
    unittest.main()
