# Cross-node handoff record

Use one record per handoff. All fields describe the authorized task; do not include credentials or restricted source text.

| Field | Value |
|---|---|
| Handoff / stable task ID | Record both |
| Source / target node labels | Match the local capability registry |
| Source run and lease | Source must be quiescent before release |
| Input revision / parameter hashes | Exact revision and immutable input inventory |
| Checkpoint / log / artifact hashes | Include location and approved transfer route |
| Runtime / compatibility preflight | Record target's independent check |
| Remaining work / budget | Include stop conditions and resume support |
| Readiness deadline / escalation owner | O; scope/resource decisions go to H |
| Source stopped | Timestamp and evidence |
| State published | Named commit and artifact manifest, not a blanket add |
| Target READY | Handoff ID, accepted hashes, node and preflight result |
| Lease transferred | O confirms source release and target ownership |
| Target STARTED | Same handoff ID plus new run ID and timestamp |
| Failure / rollback decision | Inspect both nodes before any restart |
| Ownership epoch / old provider stop | One active successor; standby is not active; preserve valid in-flight jobs |
| Phase / checked and unchecked scope | Preparation and stored compatibility are not execution permission |
| Budget authority / carried costs | Same ledger; failed and pending attempts survive transfer |
| Required continuation/delivery | Actual task response and any required human notification, not just a PID |

Keep accepted hashes consistent across READY, lease transfer and STARTED. If no portable checkpoint exists, plan an explicit new run. A local process lock does not provide a distributed lease or numerical parity evidence.
