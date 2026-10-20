"""Run one explicit argv command, with a unique log and JSON status record."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save(path: Path, result: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    version = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
    p.add_argument("--version", action="version", version=f"%(prog)s {version}")
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--id", required=True)
    p.add_argument("--timeout", type=int)
    p.add_argument("command", nargs=argparse.REMAINDER)
    args = p.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", args.id):
        p.error("id must contain only letters, digits, underscores and hyphens")
    if not command:
        p.error("supply an argv command after --")
    if args.timeout is not None and args.timeout < 1:
        p.error("timeout must be positive")
    root = args.root.resolve()
    if not root.is_dir():
        p.error("root must be an existing directory")
    try:
        folder = root / ".multi-ai/runs"
        folder.mkdir(parents=True, exist_ok=True)
        run_id = f"{args.id}-{uuid.uuid4().hex}"
        output = folder / f"{run_id}.log"
        record = folder / f"{run_id}.json"
        result = dict(id=args.id, run_id=run_id, command=command, cwd=str(root), started=now(),
                      ended=None, status="running", exit_code=None, log=output.name)
        save(record, result)
        try:
            with output.open("w", encoding="utf-8") as log:
                child = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT,
                                       timeout=args.timeout, shell=False)
            result.update(exit_code=child.returncode,
                          status="succeeded" if child.returncode == 0 else "failed")
        except subprocess.TimeoutExpired:
            result.update(status="timed_out", error="direct command exceeded timeout")
        except KeyboardInterrupt:
            result.update(status="interrupted", error="wrapper interrupted")
        except OSError as exc:
            result.update(status="failed", error=str(exc))
        result["ended"] = now()
        save(record, result)
        print(json.dumps(result))
        return 0 if result["status"] == "succeeded" else (130 if result["status"] == "interrupted" else 1)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
