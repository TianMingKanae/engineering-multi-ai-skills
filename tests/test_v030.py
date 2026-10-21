import importlib.util
from contextlib import closing
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


schedule = load("tail_planner", "skills/distributed-orchestration/scripts/rebalance.py")
registry = load("preregistration", "scripts/preregister.py")
doi = load("doi_tool", "skills/literature-provenance/scripts/doi.py")
quotes = load("quote_tool", "skills/literature-provenance/scripts/locate_quote.py")
archive = load("archive_tool", "skills/literature-provenance/scripts/archive_corpus.py")
decision = load("binary_decision", "examples/preregistration/decision.py")


class PlannerTest(unittest.TestCase):
    def state(self, n=18):
        return {"tasks": [dict(id=f"job-{i:02}", status="queued", seed=i, memory_mb=10,
                               required_capabilities=["compute"]) for i in range(n)]}

    def nodes(self):
        return {"nodes": [dict(id="node-a", tier="high-core", ready=True, free_slots=8,
                               free_memory_mb=100, capabilities=["compute"], throughput=2)]}

    def test_exact_full_waves_and_partial_tail_preserve_all_units(self):
        state = self.state()
        plan = schedule.plan(state, self.nodes())
        self.assertEqual([8, 8, 2], [sum(a["wave"] == wave for a in plan["assignments"]) for wave in range(3)])
        self.assertEqual(18, len({a["task_id"] for a in plan["assignments"]}))
        self.assertEqual(list(range(18)), [t["seed"] for t in state["tasks"]])

    def test_live_writer_never_stolen_and_missing_capabilities_reported(self):
        state = self.state(2)
        state["tasks"][0]["status"] = "running"
        state["tasks"][1]["required_capabilities"] = ["entitled-access"]
        plan = schedule.plan(state, self.nodes())
        self.assertEqual([], plan["assignments"])
        self.assertEqual(["job-00"], plan["untouched"])
        self.assertEqual(["job-01"], plan["unassigned"])

    def test_memory_and_zero_capacity_are_respected(self):
        nodes = self.nodes()
        nodes["nodes"][0]["free_memory_mb"] = 20
        plan = schedule.plan(self.state(3), nodes)
        self.assertEqual([2, 1], [sum(a["wave"] == w for a in plan["assignments"]) for w in range(2)])
        nodes["nodes"][0]["free_slots"] = 0
        self.assertEqual(3, len(schedule.plan(self.state(3), nodes)["unassigned"]))

    def test_apply_rejects_stale_or_forged_plan_and_keeps_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            state = self.state(2)
            path.write_text(json.dumps(state))
            plan = schedule.plan(state, self.nodes())
            forged = json.loads(json.dumps(plan))
            forged["assignments"].append(forged["assignments"][0])
            with self.assertRaises(ValueError):
                schedule.apply(path, forged, self.nodes())
            result = schedule.apply(path, plan, self.nodes())
            self.assertEqual([0, 1], [t["seed"] for t in result["tasks"]])
            self.assertTrue(all(t["status"] == "assigned" for t in result["tasks"]))
            with self.assertRaises(ValueError):
                schedule.apply(path, plan, self.nodes())

    def test_apply_uses_supplied_nodes_not_plan_topology(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            state = self.state(2)
            path.write_text(json.dumps(state))
            nodes = self.nodes()
            nodes["nodes"][0]["free_slots"] = 1
            inflated = json.loads(json.dumps(nodes))
            inflated["nodes"][0]["free_slots"] = 99
            forged = schedule.plan(state, inflated)
            self.assertEqual([0, 0], [a["wave"] for a in forged["assignments"]])
            with self.assertRaises(ValueError):
                schedule.apply(path, forged, nodes)
            self.assertEqual(state, json.loads(path.read_text()))
            result = schedule.apply(path, schedule.plan(state, nodes), nodes)
            self.assertEqual([0, 1], [t["wave"] for t in result["tasks"]])

    def test_duplicate_units_and_invalid_capacity_rejected(self):
        state = self.state(1)
        state["tasks"].append(state["tasks"][0])
        with self.assertRaises(ValueError):
            schedule.plan(state, self.nodes())
        nodes = self.nodes()
        nodes["nodes"][0]["free_slots"] = -1
        with self.assertRaises(ValueError):
            schedule.plan(self.state(1), nodes)


class RegistrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "examples/preregistration", self.root / "examples/preregistration",
                        ignore=shutil.ignore_patterns("__pycache__"))
        for command in (["init", "-q"], ["config", "core.autocrlf", "false"],
                        ["config", "user.name", "Synthetic Test"], ["config", "user.email", "test@example.invalid"],
                        ["add", "."], ["commit", "-qm", "freeze decision contract and tests"]):
            subprocess.run(["git", "-C", str(self.root), *command], check=True, capture_output=True)
        self.spec = json.loads((self.root / "examples/preregistration/spec.json").read_text())
        self.spec["test_command"][0] = sys.executable

    def artifact(self, value):
        path = self.root / self.spec["result"]
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE metrics(name TEXT PRIMARY KEY,value REAL)")
            db.execute("INSERT INTO metrics VALUES ('score',?)", (value,))
        return path

    def test_negative_result_recorded_and_cannot_be_washed_by_rerun(self):
        receipt, anchor = registry.seal(self.root, "run-1", self.spec)
        path = self.artifact(-1)
        result = registry.evaluate(self.root, receipt, anchor)
        self.assertEqual("NOT SHOWN", result["status"])
        self.assertFalse(result["passed"])
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("UPDATE metrics SET value=10")
        with self.assertRaises(ValueError):
            registry.evaluate(self.root, receipt, anchor)
        self.assertIn("NOT SHOWN", (self.root / "context/CLAIMS.generated.md").read_text())
        with closing(sqlite3.connect(self.root / "context/CLAIMS.sqlite")) as db, db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM claims")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE claims SET record='{}'")

    def test_pass_requires_later_independent_gate(self):
        receipt, anchor = registry.seal(self.root, "run-2", self.spec)
        self.artifact(0)
        self.assertEqual("PROVISIONAL", registry.evaluate(self.root, receipt, anchor)["status"])

    def test_interrupted_evaluation_is_unfinished_not_provisional(self):
        receipt, anchor = registry.seal(self.root, "run-8", self.spec)
        self.artifact(0)
        original = registry.git

        def crash(*args):
            raise SystemExit("simulated crash after reservation")
        registry.git = crash
        try:
            with self.assertRaises(SystemExit):
                registry.evaluate(self.root, receipt, anchor)
        finally:
            registry.git = original
        with self.assertRaises(ValueError):
            registry.evaluate(self.root, receipt, anchor)
        with closing(sqlite3.connect(self.root / "context/CLAIMS.sqlite")) as db:
            registry.export_ledger(self.root, db)
        ledger = (self.root / "context/CLAIMS.generated.md").read_text()
        self.assertIn("| run-8 | UNFINISHED | None |", ledger)
        self.assertNotIn("PROVISIONAL", ledger)

    def test_premature_evaluation_does_not_consume_registration(self):
        receipt, anchor = registry.seal(self.root, "run-9", self.spec)
        with self.assertRaises(ValueError):
            registry.evaluate(self.root, receipt, anchor)
        self.assertFalse((self.root / "context/CLAIMS.sqlite").exists())
        self.artifact(0)
        self.assertEqual("PROVISIONAL", registry.evaluate(self.root, receipt, anchor)["status"])

    def test_matlab_source_line_endings_are_accepted_at_seal(self):
        helper = self.root / "examples/preregistration/helper.m"
        helper.write_bytes(b"function y = helper(x)\ny = x;\nend\n")
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "add helper"], check=True, capture_output=True)
        helper.write_bytes(b"function y = helper(x)\r\ny = x;\r\nend\r\n")
        self.spec["extra_files"] = ["examples/preregistration/helper.m"]
        receipt, anchor = registry.seal(self.root, "run-10", self.spec)
        record = json.loads(receipt.read_text())
        self.assertNotEqual(record["files"]["examples/preregistration/helper.m"],
                            record["git_files"]["examples/preregistration/helper.m"])
        helper.write_bytes(b"function y = helper(x)\ny = x + 1;\nend\n")
        self.artifact(0)
        result = registry.evaluate(self.root, receipt, anchor)
        self.assertEqual("NOT SHOWN", result["status"])
        self.assertIn("Frozen file changed", result["reason"])

    def test_existing_result_or_uncommitted_contract_cannot_be_sealed(self):
        self.artifact(1)
        with self.assertRaises(ValueError):
            registry.seal(self.root, "run-3", self.spec)
        (self.root / self.spec["result"]).unlink()
        (self.root / self.spec["contract"]).write_text('{"minimums":{"score":-100}}')
        with self.assertRaises(ValueError):
            registry.seal(self.root, "run-4", self.spec)

    def test_tampered_receipt_or_evaluator_does_not_pass(self):
        receipt, anchor = registry.seal(self.root, "run-5", self.spec)
        original = receipt.read_bytes()
        receipt.write_bytes(original + b" ")
        with self.assertRaises(ValueError):
            registry.evaluate(self.root, receipt, anchor)
        receipt.write_bytes(original)
        self.artifact(1)
        (self.root / self.spec["evaluator"]).write_text("raise SystemExit('tampered')")
        result = registry.evaluate(self.root, receipt, anchor)
        self.assertEqual("NOT SHOWN", result["status"])
        self.assertIn("Frozen file changed", result["reason"])

    def test_failing_decision_tests_block_registration(self):
        self.spec["test_command"] = [sys.executable, "-c", "raise SystemExit(1)"]
        with self.assertRaises(ValueError):
            registry.seal(self.root, "run-6", self.spec)

    def test_git_checkout_line_endings_are_recorded_then_frozen(self):
        for path in (self.root / "examples/preregistration").iterdir():
            if path.suffix in {".py", ".json"}:
                relative = path.relative_to(self.root).as_posix()
                committed = subprocess.check_output(["git", "-C", str(self.root), "show", f"HEAD:{relative}"])
                # Choose the opposite of the blob, not the checkout's Git-dependent format.
                opposite = committed.replace(b"\r\n", b"\n") if b"\r\n" in committed else committed.replace(b"\n", b"\r\n")
                path.write_bytes(opposite)
        receipt, anchor = registry.seal(self.root, "run-7", self.spec)
        record = json.loads(receipt.read_text())
        name = self.spec["evaluator"]
        self.assertNotEqual(record["files"][name], record["git_files"][name])
        self.artifact(0)
        self.assertTrue(registry.evaluate(self.root, receipt, anchor)["passed"])


class LiteratureTest(unittest.TestCase):
    def metadata(self):
        return {"DOI": "10.1234/example", "title": "A Synthetic Title", "type": "article-journal",
                "container-title": ["Example Journal"], "ISSN": ["synthetic-id"]}

    def policy(self):
        return {"venues": [{"name": "Example Journal", "issn": ["synthetic-id"],
                            "type": "article-journal", "tier": "selected-journal"}],
                "allowed_tiers": ["selected-journal"]}

    def retrieve(self, identifier, accept):
        if accept.endswith("+json"):
            return json.dumps(self.metadata()).encode(), "https://api.crossref.org/synthetic"
        return b'@article{example, title={A {Synthetic} Title}, doi={10.1234/example}}', "https://api.crossref.org/synthetic"

    def test_registry_bibtex_returned_unchanged_and_approved(self):
        record, _, bib = doi.verify("https://doi.org/10.1234/example", "A Synthetic Title", self.policy(), self.retrieve)
        self.assertTrue(record["gate"]["approved"])
        self.assertEqual(self.retrieve(None, "bibtex")[0], bib)

    def test_title_doi_and_bibtex_mismatches_block(self):
        with self.assertRaises(ValueError):
            doi.verify("10.1234/example", "A Different Title", self.policy(), self.retrieve)
        def wrong(identifier, accept):
            raw, url = self.retrieve(identifier, accept)
            return (raw.replace(b"10.1234/example", b"10.1234/other"), url)
        with self.assertRaises(ValueError):
            doi.verify("10.1234/example", "A Synthetic Title", self.policy(), wrong)
        def wrong_bib(identifier, accept):
            raw, url = self.retrieve(identifier, accept)
            return (raw.replace(b"Synthetic", b"Wrong") if accept == "application/x-bibtex" else raw), url
        with self.assertRaises(ValueError):
            doi.verify("10.1234/example", "A Synthetic Title", self.policy(), wrong_bib)

    def test_unknown_and_preprint_not_promoted_by_venue_name(self):
        data = self.metadata()
        data["type"] = "posted-content"
        self.assertEqual("preprint", doi.venue_gate(data, self.policy())["tier"])
        data["type"] = "article-journal"
        data["ISSN"] = ["another-id"]
        self.assertFalse(doi.venue_gate(data, self.policy())["approved"])

    def test_preprint_subtype_and_malformed_policy_block(self):
        data = self.metadata()
        data["subtype"] = "preprint"
        self.assertFalse(doi.venue_gate(data, self.policy())["approved"])
        with self.assertRaises(ValueError):
            doi.venue_gate(data, {"allowed_tiers": "top-journal"})

    def test_offline_archive_requires_rights_and_detects_content_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "source.txt"
            path.write_text("Synthetic source")
            with self.assertRaises(ValueError):
                archive.index(root, {})
            policy = {"files": {"source.txt": {"source_id": "local-1", "version": "v1", "access_basis": "synthetic",
                                               "permitted_nodes": ["review-node"], "redistribution": "local test"}}}
            first = archive.index(root, policy)
            path.write_text("Changed synthetic source")
            second = archive.index(root, policy)
            self.assertNotEqual(first["files"][0]["sha256"], second["files"][0]["sha256"])
            self.assertEqual("source.txt", second["files"][0]["file"])

    def test_unsafe_redirect_and_invalid_doi_rejected(self):
        with self.assertRaises(ValueError):
            doi.RegistryRedirect().redirect_request(None, None, 302, "", {}, "http://127.0.0.1/private")
        for value in ("not-a-doi", "https://example.invalid/10.1234/example", "https://doi.org/10.1234/x?q=1"):
            with self.assertRaises(ValueError):
                doi.normalize_doi(value)

    def test_exact_quotes_have_page_heading_hash_and_all_occurrences(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.txt"
            source.write_text("# Overview\nAn exact sentence.\f2. Results\nAn exact sentence.", encoding="utf-8")
            matches = quotes.locate(source, "An exact sentence.")
            self.assertEqual([1, 2], [r["page_index"] for r in matches])
            self.assertEqual(["# Overview", "2. Results"], [r["section"] for r in matches])
            self.assertTrue(all(len(r["source_sha256"]) == 64 and r["page_basis"] == "text-page-index" for r in matches))
            with self.assertRaises(ValueError):
                quotes.locate(source, "An invented sentence.")
            with self.assertRaises(ValueError):
                quotes.locate(source, "word " * 41)
            with self.assertRaises(ValueError):
                quotes.locate(source, "字" * 41)


class OptionalAdapterTest(unittest.TestCase):
    def test_classic_mat_metrics(self):
        try:
            from scipy.io import savemat
        except ImportError:
            self.skipTest("optional scipy not installed")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "result.mat"
            savemat(path, {"metrics": {"score": 1.0}})
            self.assertTrue(decision.decide(decision.read_metrics(path), {"minimums": {"score": 0}}))

    def test_hdf5_metrics(self):
        try:
            import h5py
        except ImportError:
            self.skipTest("optional h5py not installed")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "result.h5"
            with h5py.File(path, "w") as f:
                f.create_dataset("metrics/score", data=1.0)
            self.assertEqual({"score": 1.0}, decision.read_metrics(path))

    def test_parquet_metrics(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest("optional pyarrow not installed")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "result.parquet"
            pq.write_table(pa.Table.from_pylist([{"name": "score", "value": 1.0}]), path)
            self.assertEqual({"score": 1.0}, decision.read_metrics(path))

    def test_pdf_physical_page_and_heading(self):
        try:
            from pypdf import PdfWriter
            from pypdf.generic import NameObject, DictionaryObject, DecodedStreamObject
        except ImportError:
            self.skipTest("optional pypdf not installed")
        with tempfile.TemporaryDirectory() as temp:
            writer = PdfWriter()
            page = writer.add_blank_page(width=400, height=400)
            font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
            page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
            stream = DecodedStreamObject()
            stream.set_data(b"BT /F1 12 Tf 10 350 Td (1. Overview) Tj 0 -20 Td (An exact sentence.) Tj ET")
            page[NameObject("/Contents")] = writer._add_object(stream)
            path = Path(temp) / "source.pdf"
            writer.write(path)
            result = quotes.locate(path, "An exact sentence.")[0]
            self.assertEqual(1, result["page_index"])
            self.assertEqual("pdf-physical-page", result["page_basis"])
            self.assertEqual("1. Overview", result["section"])


if __name__ == "__main__":
    unittest.main()
