---
name: distributed-orchestration
description: Plan heterogeneous agent assignments and rebalance independent work across capability-bound nodes. Use for cross-provider review, cross-host handoffs or deadline-threatening tail batches; retain human authority and do not migrate a live writer.
---

Separate role, model/provider and physical node. Select a builder for the actual planning/code task, an independently evaluated critic/verifier from another provider when useful, and an extractor with sufficient tested context/throughput. Provider diversity is a defense against correlated errors, not evidence of superior reasoning or proof of independence. Do not assign privileges from a model brand.

Exchange committed specifications, append-only handoffs and content-addressed artifacts through provider-neutral files/Git. Keep executable source out of the blind verifier's packet. Restrict actual file/tool access through the host; a prompt alone cannot create blindness. Large binary outputs live in an approved artifact store with checksums and a Git-tracked manifest.

Use [the scheduler reference](references/scheduling.md) and [rebalance.py](scripts/rebalance.py) for deterministic tail-batch plans. Only queued or explicitly released independent units can be reassigned. Preserve IDs, seeds, inputs and the total workload. Running jobs must quiesce and transfer their lease before becoming released. Target capacity is bounded by free slots, memory and capabilities, not advertised core count alone.

The planner is read-only by default. Explicit apply checks the exact source-state hash and the reviewed node snapshot, and uses a local exclusive lock. This is a single-writer integration mechanism, not distributed consensus: serialize cross-clone plan application through an authorized coordinator or conditional shared store. Obtain target READY and STARTED acknowledgments before claiming migration succeeded.

Use homogeneous full-capacity waves when independent job sizes permit; record partial final waves and stragglers. Never promise 100% utilization or alter an experiment's selection/criteria to keep a node busy. H decides material resource/scope changes; O/F handles authorized mechanical adaptation.

Keep preparation, stored compatibility and execution release distinct. Pin actual resolved runtime/dependency evidence and exact transferred configuration bytes; a common stored-data check does not prove cross-host backend equivalence. Keep matched comparisons on the same node when required, and disclose host/workload confounding before aggregation. Carry outstanding reservations and failed costs to the successor through the same budget authority; never duplicate a ledger into fresh capacity. Record exclusive role/provider transitions in the [role topology template](../../templates/project/context/ROLES.md).
