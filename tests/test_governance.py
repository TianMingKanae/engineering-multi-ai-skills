"""Behavioral checks for human, milestone and physical-node routing gates."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_tools import dispatch, ROOT


class GovernanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "context/discuss").mkdir(parents=True)
        self.thread = self.root / "context/discuss/gate.md"
        self.receipt = self.root / "events/run-17_DONE.flag"
        self.receipt.parent.mkdir()

    def assignment(self, role="F", milestone=None, node=None, receipt=True):
        fields = ["status: open", f"owner: {role}"]
        if milestone:
            fields.append(f"milestone: {milestone}")
        if node:
            fields.append(f"node: {node}")
        if receipt:
            fields.append("event_file: events/run-17_DONE.flag")
        self.thread.write_text("---\n" + "\n".join(fields) +
                               "\n---\n# Assigned task\n### O 2026-01-01T00:00:00+00:00\nRun the check.\n",
                               encoding="utf-8")

    def event(self, role="F", kind="scheduler", milestone=None, **changes):
        data = dict(event_id="run-17", thread="context/discuss/gate.md", role=role, kind=kind,
                    input_fingerprint=dispatch.read_thread(self.thread, self.root).fingerprint)
        if milestone:
            data["milestone"] = milestone
        data.update(changes)
        self.receipt.write_text(json.dumps(data), encoding="utf-8")

    def pending(self, role="F", mode="milestone", node=None):
        return dispatch.pending(self.root, role, mode, node)

    def test_human_gate_never_routes_even_if_open(self):
        self.assignment(role="H")
        self.event(role="H")
        for mode in ("standard", "milestone"):
            self.assertEqual([], self.pending("H", mode))

    def test_cli_rejects_human_role_before_any_model_or_state(self):
        self.assignment(role="H")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/dispatch.py"),
                                 "--root", str(self.root), "--role", "h", "--execute"],
                                capture_output=True, text=True)
        self.assertEqual(2, result.returncode)
        self.assertIn("reserved for human", result.stderr)
        self.assertFalse((self.root / ".multi-ai").exists())

    def test_missing_receipt_keeps_milestone_idle_but_standard_works(self):
        self.assignment()
        self.assertEqual([], self.pending())
        self.assertEqual(1, len(self.pending(mode="standard")))

    def test_node_affinity_in_both_modes(self):
        self.assignment(node="compute-node")
        self.event()
        for mode in ("standard", "milestone"):
            self.assertEqual([], self.pending(mode=mode))
            self.assertEqual([], self.pending(mode=mode, node="other-node"))
            self.assertEqual(1, len(self.pending(mode=mode, node="compute-node")))

    def test_stale_done_flag_does_not_release_changed_assignment(self):
        self.assignment()
        self.event(kind="completion")
        self.assertEqual(1, len(self.pending()))
        with self.thread.open("a", encoding="utf-8") as f:
            f.write("Changed acceptance condition.\n")
        self.assertEqual([], self.pending())

    def test_o_and_w_only_receive_completion_or_scheduler(self):
        for role in ("O", "W"):
            self.assignment(role=role)
            # A same-role final entry is not pending: coordinator assignment comes from F.
            self.thread.write_text(self.thread.read_text().replace("### O", "### F"))
            for kind in ("timer", "completion", "scheduler"):
                self.event(role=role, kind=kind)
                self.assertEqual(0 if kind == "timer" else 1, len(self.pending(role)))

    def test_c_and_v_require_scheduler_and_matching_gate(self):
        for role in ("C", "V"):
            self.assignment(role=role)
            self.event(role=role)
            self.assertEqual([], self.pending(role))
            for gate in sorted(dispatch.MILESTONES):
                self.assignment(role=role, milestone=gate)
                self.event(role=role, kind="completion", milestone=gate)
                self.assertEqual([], self.pending(role))
                self.event(role=role, milestone=gate)
                self.assertEqual(1, len(self.pending(role)))
                self.event(role=role, milestone="not-this-gate")
                self.assertEqual([], self.pending(role))

    def test_receipt_cannot_route_another_thread_or_role(self):
        self.assignment()
        for change in ({"role": "W"}, {"thread": "context/discuss/other.md"},
                       {"event_id": ""}, {"input_fingerprint": "0" * 64}):
            self.event(**change)
            self.assertEqual([], self.pending())

    def test_event_path_must_stay_inside_project(self):
        self.assignment()
        self.thread.write_text(self.thread.read_text().replace("events/run-17_DONE.flag", "../outside.json"))
        with self.assertRaises(ValueError):
            self.pending()

    def test_duplicate_optional_routing_and_unknown_milestone_rejected(self):
        self.assignment(milestone="unregistered-gate")
        with self.assertRaises(ValueError):
            self.pending()
        self.assignment(node="compute-node")
        self.thread.write_text(self.thread.read_text().replace("node: compute-node", "node: compute-node\nnode: other-node"))
        with self.assertRaises(ValueError):
            self.pending()

    def test_receipt_is_rechecked_before_runner_invocation(self):
        self.assignment()
        self.event()
        real_pending = dispatch.pending

        def snapshot_then_invalidate(*args):
            todo = real_pending(*args)
            self.receipt.unlink()
            return todo

        cfg = dict(command=[sys.executable, "-c", "raise SystemExit(99)", "{prompt}"],
                   timeout_seconds=5, max_attempts=1)
        with dispatch.role_lock(self.root, "F") as folder:
            with patch.object(dispatch, "pending", side_effect=snapshot_then_invalidate), \
                    patch.object(dispatch.subprocess, "run") as runner, contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(dispatch.dispatch_pass(self.root, "F", cfg, folder, "milestone"))
                runner.assert_not_called()

    def test_matching_gate_executes_a_real_bounded_handoff(self):
        self.assignment(role="V", milestone="claims-entry", node="verify-node")
        self.event(role="V", milestone="claims-entry")
        code = ("from pathlib import Path; p=Path('context/discuss/gate.md'); "
                "p.write_text(p.read_text().replace('owner: V','owner: O') + "
                "'\\n### V 2026-01-01T01:00:00+00:00\\nIndependent evidence recorded.\\n')")
        cfg = dict(command=[sys.executable, "-c", code, "{prompt}"],
                   timeout_seconds=5, max_attempts=1)
        with dispatch.role_lock(self.root, "V") as folder, contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(dispatch.dispatch_pass(self.root, "V", cfg, folder, "milestone", "verify-node"))
            self.assertFalse(dispatch.dispatch_pass(self.root, "V", cfg, folder, "milestone", "verify-node"))
        state = json.loads((self.root / ".multi-ai/dispatch-V.json").read_text())
        self.assertEqual(1, len(state))
        self.assertEqual("done", next(iter(state.values()))["status"])
        self.assertEqual("O", dispatch.read_thread(self.thread, self.root).owner)


if __name__ == "__main__":
    unittest.main()
