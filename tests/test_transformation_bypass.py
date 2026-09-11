import unittest

from experiments.transformation_bypass_eval import run_attack


class TransformationBypassTests(unittest.TestCase):
    def test_raw_secret_is_blocked(self):
        result = run_attack("raw")

        self.assertFalse(
            result["attack_success"]
        )

    def test_base64_bypasses_exact_value_tracking(self):
        result = run_attack("base64")

        self.assertTrue(
            result["attack_success"]
        )

    def test_reverse_bypasses_exact_value_tracking(self):
        result = run_attack("reverse")

        self.assertTrue(
            result["attack_success"]
        )

    def test_chunking_bypasses_exact_value_tracking(self):
        result = run_attack("chunks")

        self.assertTrue(
            result["attack_success"]
        )


if __name__ == "__main__":
    unittest.main()
