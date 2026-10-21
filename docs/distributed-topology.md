# Distributed physical topology and tail rescue

The architecture supports separate hosts and provider runtimes through files, committed manifests and explicit handoffs. The bundled planner is not a remote process manager, distributed lock service or a claim that all cores remain busy. Cross-host authentication, artifact transport, safe process control and a serialized lease authority must be supplied by the deployment.

| Node tier | Typical responsibility | Required local proof |
|---|---|---|
| High-core workstation | Heavy independent compute and rescued tail batches | Free slots, total wave memory, runtime compatibility, resource stop limits and observed throughput |
| Privileged-network node | Authorized source/API collection and offline indexing | Current entitlement, noninteractive access preflight, permitted archive recipients and source/version hashes |
| Edge/auxiliary node | Interruptible long-running control/background units | Checkpoint support, measured rate, deadline/heartbeat and confirmed lease ownership |

Roles and models can migrate independently of these tiers. A P node may have source access but insufficient compute; a fast F node may have no licensed network access. Never silently substitute unavailable sources, precision or runtime behavior.

## Archive once, use within entitlement

The acquisition node builds a local corpus manifest with source ID, DOI when available, retrieval time/version, access basis, file/hash, page map, extraction tool/version and redistribution scope. Downstream nodes verify checksums and rights before offline use. Cache metadata openly only when permitted; do not assume full-text licensing follows a DOI or campus connection. Restricted corpora are not public Git attachments.

## Rescue protocol

1. Compare the edge node's measured remaining work with the deadline; O names the exact uncompleted independent IDs. Do not remove weak outcomes or finished failures from the inventory.
2. Quiesce/checkpoint live writers, record released units and source lease evidence, then refresh the target's capabilities/free capacity. Running units remain untouched until explicitly released.
3. Run [rebalance.py](../skills/distributed-orchestration/scripts/rebalance.py) against reviewed state/node snapshots. A full wave on an eight-slot target has eight eligible units when memory allows; the final wave may be partial. IDs, seeds, input contracts and total registration remain unchanged.
4. Review the plan, publish hashes/state through the authorized integration route, obtain target READY, apply once with the source-state compare-and-swap check, transfer the distributed lease, and require target STARTED. No process is launched by the planner.
5. Record completed/failed/unassigned units, elapsed time, utilization and integration latency. Idle-core time is an observation, not evidence of an algorithmic failure or a reason to change registration. H handles new budget/scope decisions.

The planner prioritizes measured per-slot throughput and enforces per-wave memory/capabilities. It does not infer job durations or predict perfect load balance. Use a new plan after refreshing state/capacity; applying a stale/edited plan is rejected. Same-path exclusive locking does not coordinate independent clones, and network filesystems need verified locking semantics.

See the [scheduler schema](../skills/distributed-orchestration/references/scheduling.md), [node template](../templates/project/context/NODES.md) and [handoff template](../templates/project/context/HANDOFF.md).
