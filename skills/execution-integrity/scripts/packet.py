"""Seal/check a declared project-local byte inventory; never launch or approve a job."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(root, name):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("Use a project-relative POSIX file path")
    parts = name.split("/")
    if PurePosixPath(name).is_absolute() or any(x in {"", ".", ".."} for x in parts):
        raise ValueError("File paths must stay inside the project")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlinked inventory paths are not supported")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("File path escapes the project")
    return path


def labels(values):
    if not isinstance(values, list) or not all(isinstance(x, str) and x.strip() for x in values):
        raise ValueError("Scope labels must be nonempty strings in an array")
    if len(set(values)) != len(values):
        raise ValueError("Duplicate scope label")
    return values


def scope(record):
    if set(record) != {"id", "phase", "files", "checked", "unchecked"}:
        raise ValueError("Expected id, phase, files, checked and unchecked")
    if not isinstance(record["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", record["id"]):
        raise ValueError("Invalid packet ID")
    if record["phase"] not in {"preparation", "execution"}:
        raise ValueError("Phase must be preparation or execution")
    checked, unchecked = labels(record["checked"]), labels(record["unchecked"])
    if set(checked) & set(unchecked):
        raise ValueError("A scope label cannot be checked and unchecked")


def seal(root, spec, output):
    root = Path(root).resolve()
    output = Path(output).absolute()
    scope(spec)
    names = spec["files"]
    if not isinstance(names, list) or not names or not all(isinstance(x, str) for x in names):
        raise ValueError("Declare a nonempty file array")
    if len(set(names)) != len(names):
        raise ValueError("Duplicate inventory file")
    files = {}
    for name in sorted(names):
        path = local(root, name)
        if path.resolve() == output.resolve():
            raise ValueError("The packet cannot inventory itself")
        if not path.is_file():
            raise ValueError(f"Inventory file missing: {name}")
        raw = path.read_bytes()
        files[name] = dict(sha256=digest(raw), bytes=len(raw))
    packet = dict(spec, files=files)
    raw = (json.dumps(packet, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode()
    with output.open("xb") as handle:
        handle.write(raw)
    return dict(packet_sha256=digest(raw), files=len(files), phase=spec["phase"], status="SEALED")


def check(root, packet_path, anchor, required_phase=None):
    root = Path(root).resolve()
    raw = Path(packet_path).read_bytes()
    if not isinstance(anchor, str) or not re.fullmatch(r"[a-f0-9]{64}", anchor) or digest(raw) != anchor:
        raise ValueError("Packet does not match the protected anchor")
    packet = json.loads(raw)
    scope(packet)
    if required_phase is not None and packet["phase"] != required_phase:
        raise ValueError("Packet phase does not match the requested phase")
    if not isinstance(packet["files"], dict) or not packet["files"]:
        raise ValueError("Missing inventory")
    for name, expected in packet["files"].items():
        path = local(root, name)
        data = path.read_bytes()
        if expected != dict(sha256=digest(data), bytes=len(data)):
            raise ValueError(f"Inventory bytes changed: {name}")
    return dict(status="PACKET_INTACT", id=packet["id"], phase=packet["phase"],
                checked=packet["checked"], unchecked=packet["unchecked"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    create = actions.add_parser("seal")
    create.add_argument("--root", type=Path, required=True)
    create.add_argument("--spec", type=Path, required=True)
    create.add_argument("--out", type=Path, required=True)
    verify = actions.add_parser("check")
    verify.add_argument("--root", type=Path, required=True)
    verify.add_argument("--packet", type=Path, required=True)
    verify.add_argument("--sha256", required=True)
    verify.add_argument("--require-phase", choices=("preparation", "execution"))
    args = parser.parse_args()
    try:
        if args.action == "seal":
            result = seal(args.root, json.loads(args.spec.read_text(encoding="utf-8")), args.out)
        else:
            result = check(args.root, args.packet, args.sha256, args.require_phase)
        print(json.dumps(result))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
