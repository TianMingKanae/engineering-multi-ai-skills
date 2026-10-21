import unittest
from decision import decide


class DecisionContractTest(unittest.TestCase):
    def test_boundary_passes(self):
        self.assertTrue(decide({"score": 0.0}, {"minimums": {"score": 0.0}}))

    def test_below_threshold_fails(self):
        self.assertFalse(decide({"score": -0.01}, {"minimums": {"score": 0.0}}))

    def test_missing_or_nonfinite_metrics_rejected(self):
        for data in ({}, {"score": float("nan")}, {"score": True}):
            with self.assertRaises(ValueError):
                decide(data, {"minimums": {"score": 0.0}})


if __name__ == "__main__":
    unittest.main()
