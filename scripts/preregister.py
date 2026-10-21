"""Seal committed decision code before a registered result exists; record one immutable verdict."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def local(root, name):
    path = root / name
    if Path(name).is_absolute() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("All registered paths must be project-local regular files")
    return path


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def seal(root, identity, spec):
    root = Path(root).resolve()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", identity):
        raise ValueError("Registration ID must be a stable filename identifier")
    receipt = local(root, f"context/registrations/{identity}.json")
    if receipt.exists():
        raise ValueError("Registration already exists; use an explicit new prospective amendment")
    result = local(root, spec["result"])
    if result.suffix.lower() not in {".sqlite", ".h5", ".hdf5", ".mat", ".parquet", ".bin"}:
        raise ValueError("Register a declared binary result format, not an editable prose verdict")
    if result.exists():
        raise ValueError("Registered result already exists; cannot preregister retrospectively")
    command = spec["test_command"]
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise ValueError("test_command must be an argv array")
    if not isinstance(spec["tests"], list) or not spec["tests"]:
        raise ValueError("Committed evaluator tests are required")
    timeout = spec.get("timeout_seconds", 60)
    if type(timeout) is not int or timeout <= 0:
        raise ValueError("timeout_seconds must be positive")
    revision = git(root, "rev-parse", "HEAD").decode().strip()
    files, git_files = {}, {}
    paths = [spec["evaluator"], spec["contract"], *spec["tests"], *spec.get("extra_files", [])]
    for name in paths:
        path = local(root, name)
        committed = git(root, "show", f"{revision}:{name}")
        working = path.read_bytes()
        # Git checkouts may convert text line endings; freeze both identities.
        text_suffixes = {".py", ".json", ".toml", ".yaml", ".yml", ".txt", ".md", ".lock", ".ini", ".cfg", ".in"}
        equivalent = working == committed
        if path.suffix.lower() in text_suffixes:
            equivalent = working.replace(b"\r\n", b"\n") == committed.replace(b"\r\n", b"\n")
        if not equivalent:
            raise ValueError(f"File is not identical to the committed revision: {name}")
        files[name] = sha(path)
        git_files[name] = hashlib.sha256(committed).hexdigest()
    test = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, shell=False)
    if test.returncode:
        raise ValueError("Decision tests failed; registration not sealed")
    # Tests themselves may have written files: check result absence and code again.
    if result.exists() or any(sha(local(root, name)) != value for name, value in files.items()):
        raise ValueError("Tests created registered data or changed a registered file")
    record = dict(id=identity, revision=revision, created=datetime.now(timezone.utc).isoformat(),
                  files=files, git_files=git_files, spec=spec, test_exit=0,
                  test_output_sha256=hashlib.sha256((test.stdout + test.stderr).encode()).hexdigest())
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open("x", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=2, allow_nan=False) + "\n")
    return receipt, sha(receipt)


def database(root):
    path = local(root, "context/CLAIMS.sqlite")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.execute("CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, finalized INTEGER NOT NULL, record TEXT NOT NULL)")
    conn.execute("CREATE TRIGGER IF NOT EXISTS no_claim_delete BEFORE DELETE ON claims BEGIN SELECT RAISE(ABORT,'claims cannot be deleted'); END")
    conn.execute("CREATE TRIGGER IF NOT EXISTS no_final_edit BEFORE UPDATE ON claims WHEN OLD.finalized=1 BEGIN SELECT RAISE(ABORT,'finalized claims cannot be edited'); END")
    conn.commit()
    return conn


def export_ledger(root, conn):
    rows = [json.loads(row[0]) for row in conn.execute("SELECT record FROM claims ORDER BY id")]
    lines = ["# Generated claims ledger", "", "SQLite is authoritative; do not edit this projection.", "",
             "| Registration | Status | Passed | Result SHA-256 | Reason |", "|---|---|---|---|---|"]
    for row in rows:
        values = [row["id"], row["status"], row.get("passed"), row.get("result_sha256", ""), row.get("reason", "")]
        lines.append("| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in values) + " |")
    path = local(root, "context/CLAIMS.generated.md")
    tmp = path.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def evaluate(root, receipt_path, expected_receipt_sha):
    root = Path(root).resolve()
    receipt_path = Path(receipt_path).resolve()
    if not re.fullmatch(r"[a-f0-9]{64}", expected_receipt_sha) or sha(receipt_path) != expected_receipt_sha:
        raise ValueError("Receipt does not match the trusted pre-run anchor")
    registration = json.loads(receipt_path.read_text(encoding="utf-8"))
    identity, spec = registration["id"], registration["spec"]
    record = dict(id=identity, status="PROVISIONAL", passed=None, receipt_sha256=expected_receipt_sha,
                  input_revision=registration["revision"], reason="evaluation reserved; unfinished is not a pass")
    conn = database(root)
    try:
        # Reserve and commit before running: crashes cannot permit an invisible second attempt.
        try:
            conn.execute("INSERT INTO claims VALUES (?,0,?)", (identity, json.dumps(record)))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Registration already consumed; prior attempt must be preserved") from None
        try:
            for name, expected in registration["files"].items():
                path = local(root, name)
                committed = git(root, "show", f"{registration['revision']}:{name}")
                if sha(path) != expected or hashlib.sha256(committed).hexdigest() != registration["git_files"][name]:
                    raise ValueError(f"Frozen file changed: {name}")
            result_path = local(root, spec["result"])
            record["result_sha256"] = sha(result_path)
            process = subprocess.run([sys.executable, str(local(root, spec["evaluator"])),
                                      "--result", str(result_path), "--contract", str(local(root, spec["contract"]))],
                                     cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                     timeout=spec.get("timeout_seconds", 60), shell=False)
            record["decision_output_sha256"] = hashlib.sha256((process.stdout + process.stderr).encode()).hexdigest()
            if sha(result_path) != record["result_sha256"]:
                raise ValueError("Result mutated during evaluation")
            if process.returncode:
                raise ValueError(f"Evaluator failed with exit {process.returncode}")
            output = json.loads(process.stdout)
            if not isinstance(output, dict) or type(output.get("passed")) is not bool:
                raise ValueError("Evaluator must emit one JSON object with a boolean passed field")
            record.update(passed=output["passed"], status="PROVISIONAL" if output["passed"] else "NOT SHOWN",
                          reason="criteria passed; independent CLAIMS gate pending" if output["passed"] else "registered criteria failed")
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            record.update(passed=False, status="NOT SHOWN", reason=str(exc))
        except KeyboardInterrupt:
            record.update(passed=False, status="NOT SHOWN", reason="evaluation interrupted")
        record["finished"] = datetime.now(timezone.utc).isoformat()
        conn.execute("UPDATE claims SET finalized=1,record=? WHERE id=? AND finalized=0", (json.dumps(record), identity))
        conn.commit()
        export_ledger(root, conn)
        return record
    finally:
        conn.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    version = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
    p.add_argument("--version", action="version", version=f"%(prog)s {version}")
    commands = p.add_subparsers(dest="action", required=True)
    freeze = commands.add_parser("seal")
    freeze.add_argument("--root", type=Path, required=True)
    freeze.add_argument("--id", required=True)
    freeze.add_argument("--spec", type=Path, required=True)
    run = commands.add_parser("evaluate")
    run.add_argument("--root", type=Path, required=True)
    run.add_argument("--registration", type=Path, required=True)
    run.add_argument("--receipt-sha256", required=True)
    args = p.parse_args()
    try:
        if args.action == "seal":
            path, anchor = seal(args.root, args.id, json.loads(args.spec.read_text(encoding="utf-8")))
            print(json.dumps(dict(receipt=str(path), sha256=anchor)))
        else:
            result = evaluate(args.root, args.registration, args.receipt_sha256)
            print(json.dumps(result))
            return 0 if result["passed"] else 1
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        p.exit(1, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
