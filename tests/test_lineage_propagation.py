import unittest

from experiments.lineage_propagation_eval import (
    run_attack,
)


class LineagePropagationTests(
    unittest.TestCase
):
    def test_transformations_leak_without_lineage(self):
        for strategy in (
            "base64",
            "reverse",
            "chunks",
            "paraphrase",
        ):
            with self.subTest(
                strategy=strategy
            ):
                result = run_attack(
                    strategy,
                    use_lineage_guard=False,
                )

                self.assertTrue(
                    result["attack_success"]
                )

    def test_lineage_survives_transformations(self):
        for strategy in (
            "base64",
            "reverse",
            "chunks",
            "paraphrase",
        ):
            with self.subTest(
                strategy=strategy
            ):
                result = run_attack(
                    strategy,
                    use_lineage_guard=True,
                )

                self.assertFalse(
                    result["attack_success"]
                )

                self.assertIn(
                    "browser:submit_artifact",
                    result["blocked_actions"],
                )


if __name__ == "__main__":
    unittest.main()
