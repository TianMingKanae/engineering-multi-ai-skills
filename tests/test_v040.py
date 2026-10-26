from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/execution-integrity/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location("integrity_" + name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


packet, budget = load("packet"), load("budget")


class PacketTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "settings.json").write_bytes(b'{"items":3}\n')
        (self.root / "empty.bin").write_bytes(b"")
        self.out = self.root / "packet.json"
        self.spec = dict(id="task-17", phase="preparation", files=["settings.json", "empty.bin"],
                         checked=["declared inventory"], unchecked=["runtime", "execution release"])

    def seal(self):
        return packet.seal(self.root, self.spec, self.out)["packet_sha256"]

    def test_round_trip_keeps_empty_bytes_and_scope(self):
        anchor = self.seal()
        result = packet.check(self.root, self.out, anchor, "preparation")
        self.assertEqual("PACKET_INTACT", result["status"])
        self.assertEqual(self.spec["unchecked"], result["unchecked"])
        self.assertEqual(0, json.loads(self.out.read_bytes())["files"]["empty.bin"]["bytes"])

    def test_preparation_cannot_satisfy_execution_phase(self):
        anchor = self.seal()
        with self.assertRaisesRegex(ValueError, "phase"):
            packet.check(self.root, self.out, anchor, "execution")

    def test_line_endings_and_other_byte_changes_are_rejected(self):
        anchor = self.seal()
        (self.root / "settings.json").write_bytes(b'{"items":3}\r\n')
        with self.assertRaisesRegex(ValueError, "bytes changed"):
            packet.check(self.root, self.out, anchor)

    def test_changed_manifest_cannot_replace_trusted_anchor(self):
        anchor = self.seal()
        content = json.loads(self.out.read_bytes())
        content["phase"] = "execution"
        self.out.write_text(json.dumps(content))
        with self.assertRaisesRegex(ValueError, "anchor"):
            packet.check(self.root, self.out, anchor)

    def test_missing_file_or_reseal_fails_without_overwrite(self):
        anchor = self.seal()
        with self.assertRaises(FileExistsError):
            self.seal()
        self.assertEqual(anchor, packet.digest(self.out.read_bytes()))
        (self.root / "settings.json").unlink()
        with self.assertRaises(OSError):
            packet.check(self.root, self.out, anchor)

    def test_invalid_paths_duplicates_and_conflicting_scope_rejected(self):
        for names in (["../settings.json"], ["/settings.json"], ["C:/settings.json"],
                      ["folder\\settings.json"], ["settings.json", "settings.json"]):
            with self.subTest(names=names), self.assertRaises(ValueError):
                packet.seal(self.root, dict(self.spec, files=names), self.out)
        with self.assertRaises(ValueError):
            packet.seal(self.root, dict(self.spec, unchecked=self.spec["checked"]), self.out)
        self.assertFalse(self.out.exists())

    def test_seal_rejects_missing_and_self_inventory(self):
        with self.assertRaises(ValueError):
            packet.seal(self.root, dict(self.spec, files=["missing.bin"]), self.out)
        with self.assertRaises(ValueError):
            packet.seal(self.root, dict(self.spec, files=["packet.json"]), self.out)

    def test_relocated_identical_inventory_can_be_checked(self):
        anchor = self.seal()
        relocated = self.root / "target"
        relocated.mkdir()
        for name in self.spec["files"]:
            (relocated / name).write_bytes((self.root / name).read_bytes())
        self.assertEqual("PACKET_INTACT", packet.check(relocated, self.out, anchor)["status"])

    def test_unlisted_file_is_explicitly_outside_inventory(self):
        anchor = self.seal()
        (self.root / "unlisted.txt").write_text("not covered")
        self.assertEqual("PACKET_INTACT", packet.check(self.root, self.out, anchor)["status"])

    def test_cli_seal_and_wrong_phase_exit(self):
        spec_path = self.root / "spec.json"
        spec_path.write_text(json.dumps(self.spec))
        seal = subprocess.run([sys.executable, str(SCRIPTS / "packet.py"), "seal", "--root", str(self.root),
                               "--spec", str(spec_path), "--out", str(self.out)], capture_output=True, text=True)
        self.assertEqual(0, seal.returncode, seal.stderr)
        anchor = json.loads(seal.stdout)["packet_sha256"]
        check = subprocess.run([sys.executable, str(SCRIPTS / "packet.py"), "check", "--root", str(self.root),
                                "--packet", str(self.out), "--sha256", anchor, "--require-phase", "execution"],
                               capture_output=True, text=True)
        self.assertEqual(1, check.returncode)
        self.assertIn("phase", check.stderr)


class BudgetTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "budget.sqlite"
        budget.initialize(self.path, "task-17", 10, 3, "work-units")

    def status(self):
        with closing(budget.connect(self.path)) as db:
            return budget.balance(db)

    def receipt(self, attempt, charged, **extra):
        result = dict(attempt=attempt, cost_id=attempt + "-lifetime", status="FAILED", charged=charged,
                      basis="measurement", evidence="synthetic meter fixture")
        result.update(extra)
        return json.dumps(result).encode()

    def test_pending_reservation_survives_reopen_and_blocks_overspend(self):
        budget.reserve(self.path, "a", "preparation", 7)
        self.assertEqual(7, self.status()["pending_reserved"])
        with self.assertRaises(ValueError):
            budget.reserve(self.path, "b", "execution", 4)
        self.assertEqual(1, self.status()["attempts"])

    def test_failure_cost_and_attempt_persist_across_phases(self):
        budget.reserve(self.path, "a", "preparation", 7)
        result = budget.settle(self.path, self.receipt("a", 5))
        self.assertEqual(5, result["measured"])
        budget.reserve(self.path, "b", "execution", 3)
        budget.settle(self.path, self.receipt("b", 1, status="CANCELLED"))
        budget.reserve(self.path, "c", "execution", 1)
        with self.assertRaises(ValueError):
            budget.reserve(self.path, "d", "preparation", 1)
        self.assertEqual(3, self.status()["attempts"])

    def test_overrun_is_stored_in_full_and_blocks_further_reservation(self):
        budget.reserve(self.path, "a", "execution", 5)
        result = budget.settle(self.path, self.receipt("a", 12))
        self.assertEqual(12, result["charged"])
        self.assertEqual(2, result["overrun"])
        with self.assertRaises(ValueError):
            budget.reserve(self.path, "b", "execution", 1)

    def test_settlement_cannot_be_replaced_or_cost_id_counted_twice(self):
        budget.reserve(self.path, "a", "preparation", 2)
        budget.reserve(self.path, "b", "preparation", 2)
        raw = self.receipt("a", 1, cost_id="shared-lifetime")
        budget.settle(self.path, raw)
        with self.assertRaises(ValueError):
            budget.settle(self.path, raw)
        with self.assertRaises(sqlite3.IntegrityError):
            budget.settle(self.path, self.receipt("b", 1, cost_id="shared-lifetime"))
        self.assertEqual(2, self.status()["pending_reserved"])
        with closing(budget.connect(self.path)) as db:
            stored = db.execute("SELECT receipt_sha256,receipt FROM attempts WHERE id='a'").fetchone()
            self.assertEqual((budget.hashlib.sha256(raw).hexdigest(), raw.decode()), stored)

    def test_policy_debit_is_not_reported_as_measurement(self):
        budget.reserve(self.path, "a", "preparation", 3)
        result = budget.settle(self.path, self.receipt("a", 3, basis="policy-debit"))
        self.assertEqual(0, result["measured"])
        self.assertEqual(3, result["policy_debits"])

    def test_reset_delete_and_settled_update_rejected(self):
        with self.assertRaises(FileExistsError):
            budget.initialize(self.path, "reset", 100, 30, "work-units")
        budget.reserve(self.path, "a", "preparation", 2)
        budget.settle(self.path, self.receipt("a", 1))
        with closing(budget.connect(self.path)) as db:
            for command in ("DELETE FROM attempts", "UPDATE attempts SET charged=0", "UPDATE policy SET ceiling=100",
                            "DELETE FROM policy", "INSERT INTO policy VALUES ('new',100,30,'other')"):
                with self.subTest(command=command), self.assertRaises(sqlite3.IntegrityError):
                    db.execute(command)
        self.assertEqual(10, self.status()["ceiling"])
        self.assertEqual(1, self.status()["charged"])

    def test_bad_amount_or_estimate_cannot_enter_measured_accounting(self):
        for units in (float("nan"), float("inf"), True, -1, 0):
            with self.subTest(units=units), self.assertRaises(ValueError):
                budget.reserve(self.path, "a", "execution", units)
        budget.reserve(self.path, "a", "execution", 2)
        for fields in (dict(charged=-1), dict(charged=True), dict(charged=float("nan")), dict(basis="estimate")):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                budget.settle(self.path, self.receipt("a", **{"charged": 1, **fields}))
        self.assertEqual(2, self.status()["pending_reserved"])

    def test_two_concurrent_reservations_cannot_oversubscribe_one_ledger(self):
        def claim(name):
            try:
                budget.reserve(self.path, name, "execution", 6)
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=2) as workers:
            self.assertEqual([False, True], sorted(workers.map(claim, ("a", "b"))))
        self.assertEqual(6, self.status()["pending_reserved"])

    def test_duplicate_attempt_rejected_even_after_settlement(self):
        budget.reserve(self.path, "a", "execution", 1)
        budget.settle(self.path, self.receipt("a", 1))
        with self.assertRaises(sqlite3.IntegrityError):
            budget.reserve(self.path, "a", "execution", 1)

    def test_cli_status_and_missing_ledger_does_not_create_one(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "budget.py"), "--ledger", str(self.path), "status"],
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(10, json.loads(result.stdout)["remaining"])
        missing = self.path.with_name("missing.sqlite")
        with self.assertRaises(sqlite3.OperationalError):
            budget.reserve(missing, "a", "execution", 1)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
