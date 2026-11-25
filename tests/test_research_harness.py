"""Regression tests for research-harness ledger, dual verification, briefings and CLI."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/research-harness/scripts/harness_ledger.py"

spec = importlib.util.spec_from_file_location("harness_ledger", SCRIPT)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class ResearchHarnessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / "context/harness_state.json"
        ledger.init_ledger(self.state)
        ledger.add_direction(self.state, "dir-a", "Bound residual norm under non-uniform weights")
        ledger.add_direction(self.state, "dir-b", "Test normalized step scaling on sparse grid")

    def test_init_refuses_overwrite_without_force_and_requires_objection_on_fail(self):
        with self.assertRaises(FileExistsError):
            ledger.init_ledger(self.state)
        with self.assertRaisesRegex(ValueError, "objection"):
            ledger.record_attempt(self.state, "a-1", 1, "dir-a", "F", "constant step", outcome="fail")
        with self.assertRaisesRegex(ValueError, "single_verdict and cross_verdict"):
            ledger.record_attempt(
                self.state, "a-ok", 1, "dir-a", "F", "scaled step", outcome="pass", single_verdict="pass"
            )

    def test_dual_verification_blocks_self_review_and_requires_both_passes(self):
        ledger.record_attempt(self.state, "a-1", 1, "dir-a", "F", "constant step", artifact="out/a1.txt")
        with self.assertRaisesRegex(ValueError, "author"):
            ledger.verify_attempt(self.state, "a-1", "single", "pass", "F")
        res = ledger.verify_attempt(self.state, "a-1", "single", "pass", "C1")
        self.assertEqual("pending", res["outcome"])
        res = ledger.verify_attempt(self.state, "a-1", "cross", "pass", "C2")
        self.assertEqual("pass", res["outcome"])

        ledger.record_attempt(self.state, "a-2", 1, "dir-b", "F", "grid heuristic")
        ledger.verify_attempt(self.state, "a-2", "single", "pass", "C1")
        res2 = ledger.verify_attempt(
            self.state, "a-2", "cross", "fail", "C2", objection="Shared seed bias across grid rows"
        )
        self.assertEqual("fail", res2["outcome"])
        self.assertIn("[cross] Shared seed bias", res2["objection"])

    def test_isolated_fragment_salvage_and_scoped_briefing_with_stall_detection(self):
        ledger.record_attempt(
            self.state, "a-1", 1, "dir-a", "F", "constant step 0.1",
            outcome="fail", single_verdict="pass", cross_verdict="fail",
            objection="Diverges at ratio 4:1", artifact="out/a1.txt",
        )
        ledger.record_attempt(
            self.state, "a-2", 2, "dir-a", "F", "step 0.05",
            outcome="fail", single_verdict="fail", cross_verdict="pending",
            objection="Still diverges at ratio 6:1", artifact="out/a2.txt",
        )
        ledger.record_attempt(
            self.state, "b-1", 1, "dir-b", "F", "sparse warmup",
            outcome="fail", objection="Unrelated dir-b noise",
        )

        # Author cannot self-certify their salvaged fragment
        with self.assertRaisesRegex(ValueError, "Isolated verifier"):
            ledger.promote_fragment(
                self.state, "frag-1", "Bound holds for ratio <= 2:1", "a-1", "F", "ratio <= 2:1"
            )
        # Distinct verifier can salvage a valid sub-lemma from a rejected attempt
        frag = ledger.promote_fragment(
            self.state, "frag-1", "Bound holds for ratio <= 2:1", "a-1", "C-auditor", "ratio <= 2:1"
        )
        self.assertEqual("a-1", frag["source_attempt"])

        ledger.exclude_dead_end(
            self.state, "dead-1", "dir-a", "Unnormalized step fails above ratio 3:1",
            "out/a1.txt", revisit_if="weights are pre-normalized",
        )
        ledger.exclude_dead_end(
            self.state, "dead-b", "dir-b", "Sparse-only grid fails", "out/b1.txt"
        )
        ledger.add_rule(
            self.state, "rule-1", "Corner ratios missed in round 1",
            "Always test 6:1 ratio before passing any draft.", "Advisor", source_rounds="1-2"
        )

        briefing = ledger.build_briefing(self.state, "dir-a")
        self.assertIn("Stall notice", briefing)
        self.assertIn("rule-1", briefing)
        self.assertIn("frag-1", briefing)
        self.assertIn("dead-1", briefing)
        self.assertIn("Diverges at ratio 4:1", briefing)
        self.assertNotIn("dead-b", briefing)
        self.assertNotIn("Unrelated dir-b noise", briefing)

        summary = ledger.status_summary(self.state)
        self.assertEqual(["dir-a"], summary["stalled_directions"])
        self.assertEqual(1, summary["verified_fragments"])
        self.assertEqual(2, summary["dead_ends"])

    def test_cli_round_trip_and_invalid_command_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state = Path(tmpdir) / "state.json"
            for cmd in (
                ["init", "--state", str(state)],
                ["add-direction", "--state", str(state), "--id", "d1", "--goal", "Test synthetic bound"],
                ["record-attempt", "--state", str(state), "--id", "x1", "--round", "1",
                 "--direction", "d1", "--author", "F", "--method", "analytic bound"],
                ["verify-attempt", "--state", str(state), "--id", "x1",
                 "--scope", "single", "--verdict", "pass", "--reviewer", "C1"],
                ["verify-attempt", "--state", str(state), "--id", "x1",
                 "--scope", "cross", "--verdict", "pass", "--reviewer", "C2"],
                ["status", "--state", str(state)],
            ):
                proc = subprocess.run([sys.executable, str(SCRIPT), *cmd], capture_output=True, text=True)
                self.assertEqual(0, proc.returncode, proc.stderr)
            parsed = json.loads(proc.stdout)
            self.assertEqual(1, parsed["passed_attempts"])
            self.assertEqual([], parsed["pending_dual_verification"])

            bad = subprocess.run(
                [sys.executable, str(SCRIPT), "briefing", "--state", str(state), "--direction", "missing"],
                capture_output=True, text=True,
            )
            self.assertEqual(1, bad.returncode)
            self.assertIn("ERROR:", bad.stderr)


if __name__ == "__main__":
    unittest.main()
