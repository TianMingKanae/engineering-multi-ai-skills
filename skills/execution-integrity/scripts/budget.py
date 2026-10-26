"""Single-authority attempt reservations and evidenced settlements; no job execution."""
import argparse
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import sqlite3


def amount(value, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"Amount must be finite and >= {minimum}")
    return value


def identifier(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("IDs and labels must be nonempty strings")
    return value


def connect(path):
    path = Path(path).resolve()
    return sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, timeout=10)


def initialize(path, identity, ceiling, max_attempts, unit):
    identifier(identity)
    identifier(unit)
    amount(ceiling)
    if ceiling <= 0 or type(max_attempts) is not int or max_attempts < 1:
        raise ValueError("Positive ceiling and integer attempt limit required")
    # Never recreate an existing ledger or silently reset its policy/history.
    with Path(path).open("xb"):
        pass
    with closing(connect(path)) as db, db:
        db.execute("CREATE TABLE policy (id TEXT, ceiling REAL, max_attempts INTEGER, unit TEXT)")
        db.execute("INSERT INTO policy VALUES (?,?,?,?)", (identity, ceiling, max_attempts, unit))
        db.execute("CREATE TABLE attempts (id TEXT PRIMARY KEY, phase TEXT NOT NULL, reserved REAL NOT NULL, "
                   "charged REAL, status TEXT NOT NULL, basis TEXT, cost_id TEXT UNIQUE, receipt_sha256 TEXT, receipt TEXT)")
        db.execute("CREATE TRIGGER policy_update BEFORE UPDATE ON policy BEGIN SELECT RAISE(ABORT,'policy frozen'); END")
        db.execute("CREATE TRIGGER policy_delete BEFORE DELETE ON policy BEGIN SELECT RAISE(ABORT,'policy frozen'); END")
        db.execute("CREATE TRIGGER policy_insert BEFORE INSERT ON policy BEGIN SELECT RAISE(ABORT,'policy frozen'); END")
        db.execute("CREATE TRIGGER attempt_delete BEFORE DELETE ON attempts BEGIN SELECT RAISE(ABORT,'retain attempts'); END")
        db.execute("CREATE TRIGGER attempt_update BEFORE UPDATE ON attempts WHEN OLD.status != 'RESERVED' "
                   "BEGIN SELECT RAISE(ABORT,'settlement frozen'); END")


def balance(db):
    identity, ceiling, limit, unit = db.execute("SELECT * FROM policy").fetchone()
    rows = db.execute("SELECT reserved,charged,status,basis FROM attempts").fetchall()
    pending = math.fsum(row[0] for row in rows if row[2] == "RESERVED")
    measured = math.fsum(row[1] for row in rows if row[3] == "measurement")
    debits = math.fsum(row[1] for row in rows if row[3] == "policy-debit")
    used = pending + measured + debits
    return dict(id=identity, unit=unit, ceiling=ceiling, max_attempts=limit, attempts=len(rows),
                pending_reserved=pending, measured=measured, policy_debits=debits,
                charged=measured + debits, remaining=max(0, ceiling - used), overrun=max(0, used - ceiling))


def reserve(path, attempt_id, phase, units):
    identifier(attempt_id)
    if phase not in {"preparation", "execution"}:
        raise ValueError("Unknown phase")
    amount(units)
    if units <= 0:
        raise ValueError("Reservation must be positive")
    with closing(connect(path)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        state = balance(db)
        if state["attempts"] >= state["max_attempts"] or units > state["remaining"]:
            raise ValueError("Attempt or resource budget exhausted")
        db.execute("INSERT INTO attempts (id,phase,reserved,status) VALUES (?,?,?,'RESERVED')",
                   (attempt_id, phase, units))
        return dict(attempt=attempt_id, phase=phase, reserved=units, status="RESERVED")


def settle(path, raw):
    receipt = json.loads(raw)
    if set(receipt) != {"attempt", "cost_id", "status", "charged", "basis", "evidence"}:
        raise ValueError("Expected attempt, cost_id, status, charged, basis and evidence")
    identifier(receipt["attempt"])
    identifier(receipt["cost_id"])
    identifier(receipt["evidence"])
    amount(receipt["charged"])
    if receipt["status"] not in {"SUCCEEDED", "FAILED", "CANCELLED"}:
        raise ValueError("Invalid terminal status")
    if receipt["basis"] not in {"measurement", "policy-debit"}:
        raise ValueError("Separate measurement from conservative policy debit")
    with closing(connect(path)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT status FROM attempts WHERE id=?", (receipt["attempt"],)).fetchone()
        if row != ("RESERVED",):
            raise ValueError("Attempt is absent or already settled")
        db.execute("UPDATE attempts SET charged=?,status=?,basis=?,cost_id=?,receipt_sha256=?,receipt=? WHERE id=?",
                   (receipt["charged"], receipt["status"], receipt["basis"], receipt["cost_id"],
                    hashlib.sha256(raw).hexdigest(), raw.decode("utf-8"), receipt["attempt"]))
        # Overruns are preserved honestly, not rejected or clamped to the reservation.
        return balance(db)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    actions = parser.add_subparsers(dest="action", required=True)
    init = actions.add_parser("init")
    init.add_argument("--id", required=True)
    init.add_argument("--ceiling", required=True, type=float)
    init.add_argument("--max-attempts", required=True, type=int)
    init.add_argument("--unit", required=True)
    claim = actions.add_parser("reserve")
    claim.add_argument("--attempt", required=True)
    claim.add_argument("--phase", required=True, choices=("preparation", "execution"))
    claim.add_argument("--units", required=True, type=float)
    finish = actions.add_parser("settle")
    finish.add_argument("--receipt", required=True, type=Path)
    actions.add_parser("status")
    args = parser.parse_args()
    try:
        if args.action == "init":
            initialize(args.ledger, args.id, args.ceiling, args.max_attempts, args.unit)
            result = dict(status="INITIALIZED")
        elif args.action == "reserve":
            result = reserve(args.ledger, args.attempt, args.phase, args.units)
        elif args.action == "settle":
            result = settle(args.ledger, args.receipt.read_bytes())
        else:
            with closing(connect(args.ledger)) as db:
                result = balance(db)
        print(json.dumps(result, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
