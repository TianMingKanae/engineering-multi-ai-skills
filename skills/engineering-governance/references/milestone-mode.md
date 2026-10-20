# Milestone mode and token economy

## Trigger contract

Replace scheduled model wakeups with external completion events and scheduler assignments. Shell/file polling can be used to detect events without a model call; it is not a periodic reasoning session. Prefer a one-shot dispatcher invoked by the job scheduler. Never create a watcher unless authorized. O and W wake only for a completion receipt or explicit scheduler report; H's release is routed through an authorized scheduler assignment.

C and V batch review only at these gates:

| Gate | Event value | Review packet and release condition |
|---|---|---|
| Pilot Readout | pilot-readout | Small-run outputs, failures, cost and uncertainty; C reviews, V checks the packet independently. |
| Pre-Main Launch | pre-main-launch | Frozen plan/script revision, preflight, resource estimate, checkpoint strategy and any approved exceptions. V checks pilot artifacts and invariants; do not claim main results exist. |
| CLAIMS Entry | claims-entry | Frozen result inventory, registered criteria, independent verification report and proposed wording before promotion to VERIFIED. |

Routine progress goes into local logs and the queue, not hourly C/V sessions. O merges small questions into one gate packet. The assigned reviewer records gate ID, input revision, evidence hashes, pass/fail/waived conditions and next owner. A failed gate returns to O/F; an unresolved scope or resource choice goes to H. Safety/resource alarms may halt work immediately without waiting for a gate; O/W escalate them rather than launching unscheduled C/V reviews. H can explicitly amend the cadence, with the reason recorded.

## Routing example

```yaml
status: open
owner: C
participants: H, O, F, C, V
milestone: pre-main-launch
event_file: .multi-ai/events/gate-17.json
node: review-node
```

The authorized producer writes a receipt after finalizing the thread. A completion marker named `<run-id>_DONE.flag` must carry the same JSON envelope; existence alone is insufficient.

```json
{
  "event_id": "gate-17-C",
  "kind": "scheduler",
  "thread": "context/discuss/main-launch.md",
  "role": "C",
  "milestone": "pre-main-launch",
  "input_fingerprint": "<SHA-256 of the exact thread bytes>"
}
```

`kind` is `completion` or `scheduler`. C/V require `scheduler` and a matching milestone; O/W accept either kind. Other roles also need a matching receipt in milestone mode. Missing receipts, stale fingerprints and mismatched roles do not wake a model. The event path must stay inside the project. For a new gate, update the thread first, then compute its digest (`hashlib.sha256(path.read_bytes()).hexdigest()`) and publish the receipt atomically. Do not change the thread after sealing the receipt. Approved artifacts and their checksums belong in the gate packet; a thread digest alone does not validate its linked data.

```shell
python scripts/dispatch.py --root /path/to/project --role C --mode milestone --node review-node
```

Add `--config /path/to/runner.json --execute` only for an authorized runner. Standard mode remains available for basic tasks and the quickstart; milestone mode is opt-in on every invocation. The script does not enforce the profile if you invoke standard mode instead, authenticate event producers or start a scheduler. Treat the receipt directory as a trusted local integration surface and apply host access controls.

## Measure savings honestly

Record baseline and milestone-mode model calls, idle calls, uncached input, cache-read/write tokens, output tokens, cost, gate latency and completed work under matched workload and accounting windows. Savings = `1 - milestone_cost / baseline_cost` with positive baseline cost. Separate cache reads from paid-cost estimates and avoid counting duplicate API usage records. Report observed quality/failure rates alongside cost. An idle-overhead reduction above 80% is a target to test, not a repository benchmark or guaranteed outcome. Shell polls do not become token usage unless they invoke a model.
