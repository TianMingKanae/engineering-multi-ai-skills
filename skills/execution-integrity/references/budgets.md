# Durable attempt reservations

[budget.py](../scripts/budget.py) is a local SQLite accounting reference. One authoritative ledger fixes a budget ID, unit, ceiling and total attempt limit. A `BEGIN IMMEDIATE` transaction serializes reservations against charged plus outstanding amounts. The ledger does not launch jobs, monitor processes, authenticate evidence, enforce operating-system limits or merge databases across clones.

```shell
python skills/execution-integrity/scripts/budget.py --ledger budget.local.sqlite init --id task-17 --ceiling 60 --max-attempts 3 --unit host-wall-seconds
python skills/execution-integrity/scripts/budget.py --ledger budget.local.sqlite reserve --attempt task-17-prep-1 --phase preparation --units 20
python skills/execution-integrity/scripts/budget.py --ledger budget.local.sqlite settle --receipt examples/execution/cost-receipt.json
python skills/execution-integrity/scripts/budget.py --ledger budget.local.sqlite status
```

The example settlement is a synthetic receipt, **not a measurement from running these commands**:

```json
{
  "attempt": "task-17-prep-1",
  "cost_id": "synthetic-process-lifetime-1",
  "status": "FAILED",
  "charged": 7,
  "basis": "measurement",
  "evidence": "synthetic fixture; replace with the actual meter receipt and hash"
}
```

Reserve before any launch. If the reservation is rejected, do not start work. An attempt ID can be used only once; failure, cancellation, changing nodes, phases or packet hashes does not restore its attempt slot. Pending reservations survive reopening the ledger and remain charged conservatively, even after a wrapper crashes. Settle only with evidence that owned work has stopped and its cost is known; an unknown still-running job must remain RESERVED. A zero-cost settlement needs real evidence of no work. The original raw receipt and its SHA-256 are stored with the terminal row. Repeated settlements and deleting/fixing terminal records through the supplied schema/API are rejected.

`basis` is measurement or policy-debit. Status reports these totals separately from pending reservations. Estimates belong in planning, never in measured totals. Settlements above a reservation are recorded in full and expose `overrun`; they are not clamped or rejected to hide cost. Positive subsequent reservations are then blocked until an externally authorized prospective budget handles the situation. The tool records an overrun after the fact; the launcher must enforce its reserved deadline/resource bound while work runs.

Use one declared unit per ledger and one non-overlapping accounting scope. CPU seconds, summed host-driver wall seconds, elapsed global time, API tokens and currency are different quantities. Paired local measurements may be compared; do not pool absolute cross-host performance without registered compatibility evidence. Do not add a parent process-tree total to child diagnostics already contained in that total. Assign each independently charged lifetime/segment a stable `cost_id`; duplicate IDs are rejected. Different IDs do not prove disjointness: audit interval/lifetime lineage externally. Retain raw nested diagnostics as nonadditive evidence. Record preparation/import/transfer/reader costs once; do not recursively meter writing the accounting receipt itself. Disclose historical gaps instead of fabricating retroactive measurements.

Use separate, prospectively allocated ledgers for disjoint host caps when appropriate; their ceilings must reconcile with the overall budget and cannot be silently transferred. Coordinate all users of one budget through the same authoritative service/file on a filesystem with tested SQLite locking. Never copy the ledger per node and treat each copy as fresh capacity, combine it with Git merge, or reset it for a retry. Host access controls and a protected external history are needed against a party that can replace the database or drop its triggers. SQLite history is not a tamper-proof security boundary. The declared phase is an accounting label; it does not authorize execution.
