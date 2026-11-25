"""Zero-dependency state, dual-verification, ledger and isolated-briefing helper."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

VALID_OUTCOMES = {"pending", "pass", "fail", "partial"}
VALID_VERDICTS = {"pending", "pass", "fail"}


def _empty_state() -> dict:
    return {
        "version": 1,
        "directions": {},
        "attempts": [],
        "fragments": [],
        "dead_ends": [],
        "rules": [],
    }


def _load(state_path: Path) -> dict:
    if not state_path.exists():
        raise FileNotFoundError(f"Missing harness state file: {state_path}")
    data = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Unsupported harness state format")
    for key, expected in (("directions", dict), ("attempts", list), ("fragments", list),
                          ("dead_ends", list), ("rules", list)):
        if not isinstance(data.get(key), expected):
            raise ValueError(f"Malformed field in harness state: {key}")
    return data


def _save(state_path: Path, data: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=state_path.parent, delete=False) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)
    tmp_path.replace(state_path)


def _require_nonempty(value: str, label: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{label} must be non-empty")
    return text


def _find_attempt(data: dict, attempt_id: str) -> dict:
    for item in data["attempts"]:
        if item["id"] == attempt_id:
            return item
    raise ValueError(f"Unknown attempt id: {attempt_id}")


def init_ledger(state_path: Path, *, force: bool = False) -> dict:
    """Create a fresh harness state JSON file."""
    if state_path.exists() and not force:
        raise FileExistsError(f"State already exists: {state_path}")
    data = _empty_state()
    _save(state_path, data)
    return data


def add_direction(state_path: Path, direction_id: str, goal: str, *, author: str = "O") -> dict:
    """Register or update an exploration direction without prescribing solution steps."""
    data = _load(state_path)
    did = _require_nonempty(direction_id, "direction_id")
    if did in data["directions"]:
        raise ValueError(f"Direction already exists: {did}")
    entry = {
        "id": did,
        "goal": _require_nonempty(goal, "goal"),
        "author": _require_nonempty(author, "author"),
    }
    data["directions"][did] = entry
    _save(state_path, data)
    return entry


def record_attempt(
    state_path: Path,
    attempt_id: str,
    round_num: int,
    direction_id: str,
    author: str,
    method: str,
    outcome: str = "pending",
    *,
    single_verdict: str = "pending",
    cross_verdict: str = "pending",
    objection: str = "",
    artifact: str = "",
) -> dict:
    """Record a round attempt; failures require an explicit objection and pass requires dual approval."""
    data = _load(state_path)
    aid = _require_nonempty(attempt_id, "attempt_id")
    did = _require_nonempty(direction_id, "direction_id")
    if round_num < 1:
        raise ValueError("round_num must be >= 1")
    if did not in data["directions"]:
        raise ValueError(f"Unregistered direction: {did}")
    if any(item["id"] == aid for item in data["attempts"]):
        raise ValueError(f"Duplicate attempt id: {aid}")
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"Invalid outcome: {outcome}")
    if single_verdict not in VALID_VERDICTS or cross_verdict not in VALID_VERDICTS:
        raise ValueError("Verdicts must be pending, pass, or fail")
    if outcome == "pass" and (single_verdict != "pass" or cross_verdict != "pass"):
        raise ValueError("Attempt outcome 'pass' requires both single_verdict and cross_verdict == 'pass'")
    obj = objection.strip()
    if (outcome in {"fail", "partial"} or single_verdict == "fail" or cross_verdict == "fail") and not obj:
        raise ValueError("Failed or partial attempts require a non-empty objection")
    entry = {
        "id": aid,
        "round": int(round_num),
        "direction": did,
        "author": _require_nonempty(author, "author"),
        "method": _require_nonempty(method, "method"),
        "outcome": outcome,
        "single_verdict": single_verdict,
        "cross_verdict": cross_verdict,
        "single_reviewer": "",
        "cross_reviewer": "",
        "objection": obj,
        "artifact": artifact.strip(),
    }
    data["attempts"].append(entry)
    _save(state_path, data)
    return entry


def verify_attempt(
    state_path: Path,
    attempt_id: str,
    scope: str,
    verdict: str,
    reviewer: str,
    *,
    objection: str = "",
) -> dict:
    """Record an independent single-attempt or round cross-check verdict."""
    if scope not in {"single", "cross"}:
        raise ValueError("scope must be 'single' or 'cross'")
    if verdict not in {"pass", "fail"}:
        raise ValueError("verdict must be 'pass' or 'fail'")
    rev = _require_nonempty(reviewer, "reviewer")
    data = _load(state_path)
    attempt = _find_attempt(data, attempt_id)
    if rev == attempt["author"]:
        raise ValueError("Verifier cannot be the attempt author")
    obj = objection.strip()
    if verdict == "fail" and not obj:
        raise ValueError("Failing verification verdict requires a non-empty objection")
    attempt[f"{scope}_verdict"] = verdict
    attempt[f"{scope}_reviewer"] = rev
    if obj:
        attempt["objection"] = f"{attempt['objection']}; [{scope}] {obj}".lstrip("; ")
    verdicts = {attempt["single_verdict"], attempt["cross_verdict"]}
    if "fail" in verdicts:
        attempt["outcome"] = "fail"
    elif verdicts == {"pass"}:
        attempt["outcome"] = "pass"
    _save(state_path, data)
    return attempt


def promote_fragment(
    state_path: Path,
    frag_id: str,
    statement: str,
    source_attempt: str,
    isolated_verifier: str,
    scope: str,
) -> dict:
    """Promote an independently verified intermediate finding (even from a failed attempt)."""
    data = _load(state_path)
    fid = _require_nonempty(frag_id, "frag_id")
    if any(item["id"] == fid for item in data["fragments"]):
        raise ValueError(f"Duplicate fragment id: {fid}")
    attempt = _find_attempt(data, source_attempt)
    verifier = _require_nonempty(isolated_verifier, "isolated_verifier")
    if verifier == attempt["author"]:
        raise ValueError("Isolated verifier cannot be the source attempt author")
    entry = {
        "id": fid,
        "statement": _require_nonempty(statement, "statement"),
        "source_attempt": attempt["id"],
        "isolated_verifier": verifier,
        "scope": _require_nonempty(scope, "scope"),
    }
    data["fragments"].append(entry)
    _save(state_path, data)
    return entry


def exclude_dead_end(
    state_path: Path,
    dead_id: str,
    direction_id: str,
    reason: str,
    evidence: str,
    *,
    revisit_if: str = "",
) -> dict:
    """Record a falsified regime or counterexample so subsequent rounds avoid repeating it."""
    data = _load(state_path)
    did_key = _require_nonempty(dead_id, "dead_id")
    target = _require_nonempty(direction_id, "direction_id")
    if target != "*" and target not in data["directions"]:
        raise ValueError(f"Unregistered direction: {target}")
    if any(item["id"] == did_key for item in data["dead_ends"]):
        raise ValueError(f"Duplicate dead-end id: {did_key}")
    entry = {
        "id": did_key,
        "direction": target,
        "reason": _require_nonempty(reason, "reason"),
        "evidence": _require_nonempty(evidence, "evidence"),
        "revisit_if": revisit_if.strip(),
    }
    data["dead_ends"].append(entry)
    _save(state_path, data)
    return entry


def add_rule(
    state_path: Path,
    rule_id: str,
    pattern: str,
    instruction: str,
    advisor: str,
    *,
    source_rounds: str = "",
) -> dict:
    """Add or update a Process Advisor standing instruction derived from cross-round logs."""
    data = _load(state_path)
    rid = _require_nonempty(rule_id, "rule_id")
    entry = {
        "id": rid,
        "pattern": _require_nonempty(pattern, "pattern"),
        "instruction": _require_nonempty(instruction, "instruction"),
        "advisor": _require_nonempty(advisor, "advisor"),
        "source_rounds": source_rounds.strip(),
    }
    data["rules"] = [r for r in data["rules"] if r["id"] != rid]
    data["rules"].append(entry)
    _save(state_path, data)
    return entry


def _is_stalled(data: dict, direction_id: str) -> bool:
    dir_attempts = [a for a in data["attempts"] if a["direction"] == direction_id]
    recent_fails = [a for a in dir_attempts if a["outcome"] in {"fail", "partial"}]
    has_pass = any(a["outcome"] == "pass" for a in dir_attempts)
    return (not has_pass) and len(recent_fails) >= 2


def build_briefing(state_path: Path, direction_id: str) -> str:
    """Build a focused briefing scoped to one direction plus shared ledger and standing rules."""
    data = _load(state_path)
    if direction_id not in data["directions"]:
        raise ValueError(f"Unregistered direction: {direction_id}")
    direction = data["directions"][direction_id]
    lines = [f"# Briefing: {direction_id}", f"Goal: {direction['goal']}", ""]

    if _is_stalled(data, direction_id):
        lines.extend([
            "## Stall notice",
            "- Repeated failures detected (>= 2 failed/partial attempts without clearance). "
            "Consider re-dispatching literature review (P) on the latest obstruction before retrying.",
            "",
        ])

    lines.append("## Active standing rules")
    if data["rules"]:
        for rule in data["rules"]:
            lines.append(f"- [{rule['id']}] {rule['instruction']} (pattern: {rule['pattern']})")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Verified reusable fragments")
    if data["fragments"]:
        for frag in data["fragments"]:
            lines.append(
                f"- [{frag['id']}] {frag['statement']} "
                f"(scope: {frag['scope']}; source: {frag['source_attempt']}; verifier: {frag['isolated_verifier']})"
            )
    else:
        lines.append("- (none)")
    lines.append("")

    rel_dead = [d for d in data["dead_ends"] if d["direction"] in {direction_id, "*"}]
    lines.append("## Excluded dead ends")
    if rel_dead:
        for dead in rel_dead:
            tail = f"; revisit_if: {dead['revisit_if']}" if dead["revisit_if"] else ""
            lines.append(f"- [{dead['id']}] {dead['reason']} (evidence: {dead['evidence']}{tail})")
    else:
        lines.append("- (none)")
    lines.append("")

    rel_att = [a for a in data["attempts"] if a["direction"] == direction_id]
    lines.append(f"## Prior attempts on {direction_id}")
    if rel_att:
        for att in rel_att:
            art = f"; artifact: {att['artifact']}" if att["artifact"] else ""
            obj = f"; objection: {att['objection']}" if att["objection"] else ""
            lines.append(
                f"- [{att['id']}] Round {att['round']} | method={att['method']} | "
                f"outcome={att['outcome']} (single={att['single_verdict']}, cross={att['cross_verdict']}"
                f"{obj}{art})"
            )
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def status_summary(state_path: Path) -> dict:
    """Summarize round state, pending dual checks and stalled directions."""
    data = _load(state_path)
    pending_dual = [
        a["id"] for a in data["attempts"]
        if a["outcome"] != "fail" and (a["single_verdict"] != "pass" or a["cross_verdict"] != "pass")
    ]
    stalled = sorted(did for did in data["directions"] if _is_stalled(data, did))
    return {
        "directions": len(data["directions"]),
        "attempts": len(data["attempts"]),
        "passed_attempts": sum(1 for a in data["attempts"] if a["outcome"] == "pass"),
        "verified_fragments": len(data["fragments"]),
        "dead_ends": len(data["dead_ends"]),
        "standing_rules": len(data["rules"]),
        "pending_dual_verification": pending_dual,
        "stalled_directions": stalled,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage iterative research harness state and briefings.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize a fresh JSON state file.")
    p_init.add_argument("--state", required=True, type=Path)
    p_init.add_argument("--force", action="store_true")

    p_dir = sub.add_parser("add-direction", help="Register an exploration direction.")
    p_dir.add_argument("--state", required=True, type=Path)
    p_dir.add_argument("--id", required=True)
    p_dir.add_argument("--goal", required=True)
    p_dir.add_argument("--author", default="O")

    p_att = sub.add_parser("record-attempt", help="Record an exploration attempt.")
    p_att.add_argument("--state", required=True, type=Path)
    p_att.add_argument("--id", required=True)
    p_att.add_argument("--round", required=True, type=int)
    p_att.add_argument("--direction", required=True)
    p_att.add_argument("--author", required=True)
    p_att.add_argument("--method", required=True)
    p_att.add_argument("--outcome", default="pending", choices=sorted(VALID_OUTCOMES))
    p_att.add_argument("--single-verdict", default="pending", choices=sorted(VALID_VERDICTS))
    p_att.add_argument("--cross-verdict", default="pending", choices=sorted(VALID_VERDICTS))
    p_att.add_argument("--objection", default="")
    p_att.add_argument("--artifact", default="")

    p_ver = sub.add_parser("verify-attempt", help="Record single or cross verification.")
    p_ver.add_argument("--state", required=True, type=Path)
    p_ver.add_argument("--id", required=True)
    p_ver.add_argument("--scope", required=True, choices=["single", "cross"])
    p_ver.add_argument("--verdict", required=True, choices=["pass", "fail"])
    p_ver.add_argument("--reviewer", required=True)
    p_ver.add_argument("--objection", default="")

    p_frag = sub.add_parser("promote-fragment", help="Promote an isolated-verified intermediate finding.")
    p_frag.add_argument("--state", required=True, type=Path)
    p_frag.add_argument("--id", required=True)
    p_frag.add_argument("--statement", required=True)
    p_frag.add_argument("--source-attempt", required=True)
    p_frag.add_argument("--isolated-verifier", required=True)
    p_frag.add_argument("--scope", required=True)

    p_dead = sub.add_parser("exclude-dead-end", help="Record an excluded dead end.")
    p_dead.add_argument("--state", required=True, type=Path)
    p_dead.add_argument("--id", required=True)
    p_dead.add_argument("--direction", required=True)
    p_dead.add_argument("--reason", required=True)
    p_dead.add_argument("--evidence", required=True)
    p_dead.add_argument("--revisit-if", default="")

    p_rule = sub.add_parser("add-rule", help="Add or update a standing rule from the process advisor.")
    p_rule.add_argument("--state", required=True, type=Path)
    p_rule.add_argument("--id", required=True)
    p_rule.add_argument("--pattern", required=True)
    p_rule.add_argument("--instruction", required=True)
    p_rule.add_argument("--advisor", required=True)
    p_rule.add_argument("--source-rounds", default="")

    p_br = sub.add_parser("briefing", help="Emit an isolated Markdown briefing for one direction.")
    p_br.add_argument("--state", required=True, type=Path)
    p_br.add_argument("--direction", required=True)
    p_br.add_argument("--out", type=Path)

    p_st = sub.add_parser("status", help="Print JSON summary of harness state.")
    p_st.add_argument("--state", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.cmd == "init":
            init_ledger(args.state, force=args.force)
            print(f"INITIALIZED {args.state}")
        elif args.cmd == "add-direction":
            res = add_direction(args.state, args.id, args.goal, author=args.author)
            print(json.dumps(res, sort_keys=True))
        elif args.cmd == "record-attempt":
            res = record_attempt(
                args.state, args.id, args.round, args.direction, args.author, args.method,
                args.outcome, single_verdict=args.single_verdict, cross_verdict=args.cross_verdict,
                objection=args.objection, artifact=args.artifact,
            )
            print(json.dumps(res, sort_keys=True))
        elif args.cmd == "verify-attempt":
            res = verify_attempt(args.state, args.id, args.scope, args.verdict,
                                 args.reviewer, objection=args.objection)
            print(json.dumps(res, sort_keys=True))
        elif args.cmd == "promote-fragment":
            res = promote_fragment(args.state, args.id, args.statement, args.source_attempt,
                                   args.isolated_verifier, args.scope)
            print(json.dumps(res, sort_keys=True))
        elif args.cmd == "exclude-dead-end":
            res = exclude_dead_end(args.state, args.id, args.direction, args.reason,
                                   args.evidence, revisit_if=args.revisit_if)
            print(json.dumps(res, sort_keys=True))
        elif args.cmd == "add-rule":
            res = add_rule(args.state, args.id, args.pattern, args.instruction,
                           args.advisor, source_rounds=args.source_rounds)
            print(json.dumps(res, sort_keys=True))
        elif args.cmd == "briefing":
            text = build_briefing(args.state, args.direction)
            if args.out:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text(text, encoding="utf-8")
            else:
                print(text)
        elif args.cmd == "status":
            print(json.dumps(status_summary(args.state), indent=2, sort_keys=True))
        return 0
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
