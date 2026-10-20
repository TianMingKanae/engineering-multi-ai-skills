"""Local, provider-neutral engineering task dispatcher. Preview is the default."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROLE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")
MILESTONES = {"pilot-readout", "pre-main-launch", "claims-entry"}


@dataclass(frozen=True)
class Thread:
    path: Path
    relative: str
    owner: str
    status: str
    last_role: str | None
    fingerprint: str
    milestone: str | None = None
    event_file: str | None = None
    node: str | None = None


def read_thread(path: Path, root: Path) -> Thread:
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Thread must be a regular project file: {path.name}")
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Missing frontmatter: {path.name}")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError(f"Unterminated frontmatter: {path.name}")
    fields = {}
    for line in lines[1:end]:
        match = re.match(r"^\s*(owner|status|milestone|event_file|node)\s*:\s*(.*?)\s*$", line)
        if not match:
            continue
        key, value = match.groups()
        if key in fields:
            raise ValueError(f"Duplicate {key}: {path.name}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key] = value
    if not fields.get("owner") or not fields.get("status"):
        raise ValueError(f"Missing owner/status: {path.name}")
    if not ROLE.fullmatch(fields["owner"]):
        raise ValueError(f"Owner must be one role: {path.name}")
    if fields["status"] not in {"open", "closed", "resolved", "blocked"}:
        raise ValueError(f"Unknown status: {path.name}")
    if "milestone" in fields and fields["milestone"] not in MILESTONES:
        raise ValueError(f"Unknown milestone: {path.name}")
    if "node" in fields and not ROLE.fullmatch(fields["node"]):
        raise ValueError(f"Node must be one identifier: {path.name}")
    headers = re.findall(r"^### ([A-Za-z][A-Za-z0-9_-]*)\s+\d{4}-\d{2}-\d{2}\S*.*$",
                         "\n".join(lines[end + 1:]), re.MULTILINE)
    return Thread(path, path.relative_to(root).as_posix(), fields["owner"],
                  fields["status"], headers[-1] if headers else None,
                  hashlib.sha256(raw).hexdigest(), fields.get("milestone"),
                  fields.get("event_file"), fields.get("node"))


def eligible(thread: Thread, root: Path, role: str, mode: str, node: str | None) -> bool:
    if role.upper() == "H" or thread.owner.upper() == "H":
        return False  # H is always a human gate, including legacy open threads.
    if thread.status != "open" or thread.owner != role or thread.last_role == role:
        return False
    if thread.node is not None and thread.node != node:
        return False
    if mode == "standard":
        return True
    if role.upper() in {"C", "V"} and thread.milestone not in MILESTONES:
        return False
    if not thread.event_file:
        return False
    receipt_path = root / thread.event_file
    if (Path(thread.event_file).is_absolute() or receipt_path.is_symlink()
            or not receipt_path.resolve().is_relative_to(root.resolve())):
        raise ValueError(f"Event receipt must be inside the project: {thread.relative}")
    if not receipt_path.exists():
        return False
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise ValueError(f"Event receipt must be an object: {thread.relative}")
    required = {"thread": thread.relative, "role": role, "input_fingerprint": thread.fingerprint}
    if any(receipt.get(k) != v for k, v in required.items()):
        return False  # Stale flags cannot release a revised assignment.
    if not isinstance(receipt.get("event_id"), str) or not receipt["event_id"].strip():
        return False
    if receipt.get("kind") not in {"completion", "scheduler"}:
        return False
    if role.upper() in {"C", "V"}:
        return receipt.get("kind") == "scheduler" and receipt.get("milestone") == thread.milestone
    return True


def pending(root: Path, role: str, mode: str = "standard", node: str | None = None) -> list[Thread]:
    # Parse every candidate first: malformed routing cannot cause partial dispatch.
    threads = [read_thread(p, root) for p in sorted((root / "context/discuss").glob("*.md"))]
    return [t for t in threads if eligible(t, root, role, mode, node)]


def load_config(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError("Runner config must be an object")
    cmd = cfg.get("command")
    if not isinstance(cmd, list) or not cmd or not all(isinstance(a, str) and a for a in cmd):
        raise ValueError("command must be a nonempty argv array")
    if not any("{prompt}" in a for a in cmd):
        raise ValueError("command must contain {prompt}")
    for key, default in (("timeout_seconds", 900), ("max_attempts", 2)):
        value = cfg.get(key, default)
        if type(value) is not int or value < 1:
            raise ValueError(f"{key} must be a positive integer")
        cfg[key] = value
    return cfg


def write_state(path: Path, state: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


@contextmanager
def role_lock(root: Path, role: str):
    folder = root / ".multi-ai"
    folder.mkdir(exist_ok=True)
    lock = folder / f"dispatch-{role}.lock"
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ValueError(f"Role {role} is locked; inspect {lock} before removing a stale lock") from None
    try:
        with os.fdopen(fd, "w") as f:
            f.write(str(os.getpid()))
        yield folder
    finally:
        lock.unlink(missing_ok=True)


def dispatch_pass(root: Path, role: str, cfg: dict, folder: Path,
                  mode: str = "standard", node: str | None = None) -> bool:
    todo = pending(root, role, mode, node)
    state_path = folder / f"dispatch-{role}.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    if not isinstance(state, dict):
        raise ValueError("Dispatcher state must be an object")
    failed = False
    for thread in todo:
        key = f"{thread.relative}:{thread.fingerprint}"
        rec = state.get(key, {})
        if rec.get("status") == "done":
            continue
        if rec.get("attempts", 0) >= cfg["max_attempts"]:
            print(f"EXHAUSTED {thread.relative}", file=sys.stderr, flush=True)
            failed = True
            continue
        current = read_thread(thread.path, root)
        if current != thread or not eligible(current, root, role, mode, node):
            print(f"CHANGED {thread.relative}; deferred", flush=True)
            continue
        prompt = (f"Work as role {role} in project {root}. Read AGENTS.md if present, then "
                  f"{thread.relative} and relevant installed skills. Follow the host's instructions "
                  "and existing authorization. Complete only the assigned bounded task. "
                  f"Append a dated '### {role} <ISO timestamp>' entry with evidence and next action, "
                  "and update frontmatter owner/status on handoff. H is the human decision owner, "
                  "never an agent. Escalate an unresolved scope/resource decision to owner H with "
                  "status blocked; do not impersonate H or invent approval. "
                  "Read the project's role write boundaries and fix budget. Do not create unrelated files.")
        command = [a.replace("{prompt}", prompt) for a in cfg["command"]]
        log = folder / f"dispatch-{role}-{time.time_ns()}.log"
        rec = {"attempts": rec.get("attempts", 0) + 1, "status": "running", "log": log.name}
        state[key] = rec
        write_state(state_path, state)
        reason = ""
        try:
            with log.open("w", encoding="utf-8") as output:
                result = subprocess.run(command, cwd=root, stdout=output, stderr=subprocess.STDOUT,
                                        timeout=cfg["timeout_seconds"], shell=False)
            if result.returncode:
                reason = f"runner exit {result.returncode}"
            else:
                after = read_thread(thread.path, root)
                if after.status == "open" and after.owner == role and after.last_role != role:
                    reason = "runner exited without a role entry or handoff"
        except subprocess.TimeoutExpired:
            reason = "runner timed out"
        except (OSError, ValueError) as exc:
            reason = str(exc)
        except KeyboardInterrupt:
            rec.update(status="failed", reason="interrupted")
            write_state(state_path, state)
            raise
        rec.update(status="failed" if reason else "done", reason=reason)
        write_state(state_path, state)
        print(f"{rec['status'].upper()} {thread.relative}: {reason or 'role entry or handoff recorded'}", flush=True)
        failed |= bool(reason)
    return failed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    version = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
    parser.add_argument("--version", action="version", version=f"%(prog)s {version}")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--role", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--mode", choices=("standard", "milestone"), default="standard")
    parser.add_argument("--node", help="Local node routing label; capabilities still require preflight")
    args = parser.parse_args(argv)
    if not ROLE.fullmatch(args.role):
        parser.error("role must be a single identifier")
    if args.role.upper() == "H":
        parser.error("H is reserved for human decisions and cannot run as an agent")
    if args.node is not None and not ROLE.fullmatch(args.node):
        parser.error("node must be a single identifier")
    if args.poll_seconds < 1:
        parser.error("poll-seconds must be positive")
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("root must be an existing directory")
    try:
        if not args.execute:
            if args.watch:
                parser.error("watch requires execute; preview is one read-only pass")
            for thread in pending(root, args.role, args.mode, args.node):
                print(f"PENDING {thread.relative}")
            return 0
        if args.config is None:
            parser.error("execute requires config")
        cfg = load_config(args.config)
        with role_lock(root, args.role) as folder:
            while True:
                failed = dispatch_pass(root, args.role, cfg, folder, args.mode, args.node)
                if not args.watch:
                    return int(failed)
                time.sleep(args.poll_seconds)
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
