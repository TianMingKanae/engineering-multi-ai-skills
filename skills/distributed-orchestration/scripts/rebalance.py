"""Deterministic independent-unit planner; explicit apply uses local compare-and-swap."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def validate(state, topology):
    tasks, nodes = state["tasks"], topology["nodes"]
    for items in (tasks, nodes):
        ids = [x["id"] for x in items]
        if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
            raise ValueError("IDs must be unique nonempty strings")
    for task in tasks:
        if task["status"] not in {"queued", "released", "running", "assigned", "done", "blocked"}:
            raise ValueError("Unknown task status")
        integer(task["memory_mb"], "task memory", 1)
        if not isinstance(task.get("required_capabilities", []), list) or not all(isinstance(x, str) for x in task.get("required_capabilities", [])):
            raise ValueError("Task capabilities must be strings")
    for node in nodes:
        integer(node["free_slots"], "free slots")
        integer(node["free_memory_mb"], "free memory")
        if type(node.get("ready")) is not bool:
            raise ValueError("ready must be boolean")
        if not isinstance(node.get("capabilities", []), list) or not all(isinstance(x, str) for x in node.get("capabilities", [])):
            raise ValueError("Node capabilities must be strings")
        speed = node.get("throughput", 1.0)
        if type(speed) not in (int, float) or not math.isfinite(speed) or speed <= 0:
            raise ValueError("throughput must be finite and positive")


def plan(state, topology):
    validate(state, topology)
    remaining = sorted((t for t in state["tasks"] if t["status"] in {"queued", "released"}), key=lambda t: t["id"])
    nodes = sorted((n for n in topology["nodes"] if n["ready"] and n["free_slots"]),
                   key=lambda n: (-n.get("throughput", 1.0), n["id"]))
    assignments = []
    wave = 0
    while remaining:
        progress = False
        for node in nodes:
            slots, memory = node["free_slots"], node["free_memory_mb"]
            for task in remaining[:]:
                if not slots:
                    break
                if (set(task.get("required_capabilities", [])) <= set(node.get("capabilities", []))
                        and task.get("memory_mb", 0) <= memory):
                    assignments.append(dict(task_id=task["id"], task_hash=digest(task), node=node["id"], wave=wave))
                    remaining.remove(task)
                    slots -= 1
                    memory -= task.get("memory_mb", 0)
                    progress = True
        if not progress:
            break
        wave += 1
    result = dict(state_hash=digest(state), topology_hash=digest(topology), topology=topology,
                  assignments=assignments, unassigned=[t["id"] for t in remaining],
                  untouched=[t["id"] for t in state["tasks"] if t["status"] not in {"queued", "released"}])
    result["plan_hash"] = digest(result)
    return result


def apply(state_path, proposed, topology):
    state_path = Path(state_path)
    lock = state_path.with_name(state_path.name + ".lock")
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.close(fd)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        # The node snapshot comes from the reviewed nodes file, never from the plan itself.
        if digest(topology) != proposed.get("topology_hash"):
            raise ValueError("Plan was not made from this node snapshot; refresh nodes and plan again")
        # Recompute the entire plan, not just attacker-controlled summary hashes.
        expected = plan(state, topology)
        if proposed != expected:
            raise ValueError("Stale or modified plan; refresh state/topology and review again")
        by_id = {x["task_id"]: x for x in proposed["assignments"]}
        for task in state["tasks"]:
            if task["id"] in by_id:
                entry = by_id[task["id"]]
                task.update(status="assigned", node=entry["node"], wave=entry["wave"], plan_hash=proposed["plan_hash"])
        tmp = state_path.with_name(state_path.name + ".tmp")
        tmp.write_text(json.dumps(state, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        os.replace(tmp, state_path)
        return state
    finally:
        lock.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--state", required=True, type=Path)
    p.add_argument("--nodes", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--apply", type=Path)
    args = p.parse_args()
    try:
        if args.apply:
            if args.out or not args.nodes:
                p.error("apply requires nodes and does not accept out")
            apply(args.state, json.loads(args.apply.read_text(encoding="utf-8")),
                  json.loads(args.nodes.read_text(encoding="utf-8")))
            print("APPLIED: assignments recorded; leases/start acknowledgments remain required")
        else:
            if not args.nodes or not args.out:
                p.error("planning requires nodes and out")
            result = plan(json.loads(args.state.read_text(encoding="utf-8")), json.loads(args.nodes.read_text(encoding="utf-8")))
            with args.out.open("x", encoding="utf-8") as f:
                f.write(json.dumps(result, indent=2) + "\n")
            print(f"PLANNED {len(result['assignments'])}; UNASSIGNED {len(result['unassigned'])}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
