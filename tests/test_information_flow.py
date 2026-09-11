import unittest

from experiments.data_flow_composition_eval import (
    run_once,
)


class InformationFlowTests(unittest.TestCase):
    def test_semantic_authorization_alone_leaks(self):
        result = run_once(
            use_flow_guard=False
        )

        self.assertTrue(
            result["attack_success"]
        )

    def test_flow_guard_blocks_composed_leak(self):
        result = run_once(
            use_flow_guard=True
        )

        self.assertFalse(
            result["attack_success"]
        )

        self.assertIn(
            "browser:submit_form",
            result["blocked_actions"],
        )


if __name__ == "__main__":
    unittest.main()
