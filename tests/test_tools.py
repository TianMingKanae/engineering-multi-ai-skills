import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dispatch", ROOT / "scripts/dispatch.py")
dispatch = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = dispatch
spec.loader.exec_module(dispatch)


class ToolsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "context/discuss").mkdir(parents=True)
        self.thread = self.root / "context/discuss/task.md"
        self.write_thread()

    def write_thread(self, owner="I", status="open", last="O", note="implement"):
        self.thread.write_text(f"---\nstatus: {status}\nowner: {owner}\nparticipants: O, I, C\n---\n"
                               f"# Task\n### {last} 2026-01-01T00:00:00+00:00\n{note}\n", encoding="utf-8")

    def config(self, code="raise SystemExit(3)", **kwargs):
        cfg = dict(command=[sys.executable, "-c", code, "{prompt}"], timeout_seconds=5, max_attempts=2)
        cfg.update(kwargs)
        return cfg

    def run_pass(self, cfg):
        with dispatch.role_lock(self.root, "I") as folder:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return dispatch.dispatch_pass(self.root, "I", cfg, folder)

    def state(self):
        return json.loads((self.root / ".multi-ai/dispatch-I.json").read_text())

    def test_routing_uses_frontmatter_not_body(self):
        self.write_thread(owner="C", note="owner: I")
        self.assertEqual([], dispatch.pending(self.root, "I"))

    def test_closed_resolved_blocked_not_dispatched(self):
        for status in ("closed", "resolved", "blocked"):
            self.write_thread(status=status)
            self.assertEqual([], dispatch.pending(self.root, "I"))

    def test_last_own_entry_is_not_pending(self):
        self.write_thread(last="I")
        self.assertEqual([], dispatch.pending(self.root, "I"))

    def test_duplicate_and_missing_routing_are_errors(self):
        for text in ("# no frontmatter", "---\nowner: I\n---\n", "---\nowner: I\nowner: C\nstatus: open\n---\n"):
            self.thread.write_text(text)
            with self.assertRaises(ValueError):
                dispatch.pending(self.root, "I")

    def test_quoted_routing(self):
        self.thread.write_text('---\nstatus: "open"\nowner: \'I\'\n---\n# work\n')
        self.assertEqual(1, len(dispatch.pending(self.root, "I")))

    def test_preview_starts_no_process_and_writes_no_state(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/dispatch.py"),
                                 "--root", str(self.root), "--role", "I"], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("PENDING context/discuss/task.md", result.stdout)
        self.assertFalse((self.root / ".multi-ai").exists())

    def test_retries_are_bounded_and_new_input_can_run(self):
        self.assertTrue(self.run_pass(self.config()))
        self.assertTrue(self.run_pass(self.config()))
        self.assertTrue(self.run_pass(self.config()))
        self.assertEqual(2, next(iter(self.state().values()))["attempts"])
        self.write_thread(note="changed requirements")
        self.assertTrue(self.run_pass(self.config()))
        self.assertEqual([1, 2], sorted(r["attempts"] for r in self.state().values()))

    def test_zero_exit_without_handoff_fails(self):
        self.assertTrue(self.run_pass(self.config("pass")))
        rec = next(iter(self.state().values()))
        self.assertEqual("failed", rec["status"])
        self.assertIn("without a role entry", rec["reason"])

    def test_real_runner_handoff_and_no_second_dispatch(self):
        code = ("from pathlib import Path; p=Path('context/discuss/task.md'); "
                "p.write_text(p.read_text().replace('owner: I','owner: C') + "
                "'\\n### I 2026-01-01T01:00:00+00:00\\nEvidence: test passed.\\n')")
        self.assertFalse(self.run_pass(self.config(code)))
        self.assertFalse(self.run_pass(self.config(code)))
        self.assertEqual(1, len(self.state()))
        self.assertEqual("done", next(iter(self.state().values()))["status"])
        self.assertEqual("C", dispatch.read_thread(self.thread, self.root).owner)

    def test_role_lock_rejects_second_owner_and_releases(self):
        with dispatch.role_lock(self.root, "I"):
            with self.assertRaises(ValueError):
                with dispatch.role_lock(self.root, "I"):
                    pass
        self.assertFalse((self.root / ".multi-ai/dispatch-I.lock").exists())

    def test_config_requires_prompt_and_positive_budget(self):
        path = self.root / "runner.json"
        for cfg in ({"command": ["anything"]}, self.config(max_attempts=0), self.config(timeout_seconds=True)):
            path.write_text(json.dumps(cfg))
            with self.assertRaises(ValueError):
                dispatch.load_config(path)

    def test_malformed_second_thread_prevents_partial_dispatch(self):
        (self.root / "context/discuss/z.md").write_text("bad routing")
        with self.assertRaises(ValueError):
            self.run_pass(self.config())
        self.assertFalse((self.root / ".multi-ai/dispatch-I.json").exists())

    def run_command(self, code, *options):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/run_task.py"),
                                 "--root", str(self.root), "--id", "check", *options,
                                 "--", sys.executable, "-c", code], capture_output=True, text=True)
        return result, json.loads(result.stdout)

    def test_command_success_records_log_and_timestamps(self):
        result, record = self.run_command("print('checked')")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("succeeded", record["status"])
        self.assertEqual(0, record["exit_code"])
        self.assertTrue(record["started"] and record["ended"])
        self.assertIn("checked", (self.root / ".multi-ai/runs" / record["log"]).read_text())

    def test_command_failure_preserves_child_code(self):
        result, record = self.run_command("raise SystemExit(7)")
        self.assertEqual(1, result.returncode)
        self.assertEqual("failed", record["status"])
        self.assertEqual(7, record["exit_code"])

    def test_command_timeout_and_unique_runs(self):
        result, record = self.run_command("import time; time.sleep(10)", "--timeout", "1")
        self.assertEqual(1, result.returncode)
        self.assertEqual("timed_out", record["status"])
        _, other = self.run_command("pass")
        self.assertNotEqual(record["run_id"], other["run_id"])

    def test_dispatch_timeout_counts_failed_attempt(self):
        self.assertTrue(self.run_pass(self.config("import time; time.sleep(10)", timeout_seconds=1)))
        self.assertEqual("runner timed out", next(iter(self.state().values()))["reason"])


if __name__ == "__main__":
    unittest.main()
