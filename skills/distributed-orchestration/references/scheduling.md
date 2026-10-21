# Deterministic tail-batch planning

Run `python skills/distributed-orchestration/scripts/rebalance.py --state state.json --nodes nodes.json --out plan.json`. Apply a reviewed plan with `--apply plan.json --state state.json`. Planning does not launch processes or transfer a lease.

State schema: `{"tasks": [{"id": "job-1", "status": "queued", "required_capabilities": ["compute"], "memory_mb": 64, "seed": 1}]}`. Status is queued, released, running, assigned, done or blocked. Released means source quiescence/lease release was confirmed outside the planner. Existing assigned/running/done work is never stolen.

Node schema: `{"nodes": [{"id": "compute-node", "tier": "high-core", "ready": true, "free_slots": 8, "free_memory_mb": 8192, "capabilities": ["compute"], "throughput": 1.0}]}`. Tiers describe high-core, privileged-network or edge nodes; scheduling still uses measured capability, availability and per-slot throughput. Node snapshots are local observations, not an entitlement or identity check. Refresh immediately before use.

Each wave assigns up to free_slots units per node while respecting total wave memory. Faster observed nodes are considered first; IDs break ties. Full eight-slot waves contain eight units when eligible work/memory permits; tails remain explicit partial waves. Heterogeneous runtimes can still create idle cores. Tasks not fitting any ready node are reported as unassigned, never silently dropped or reported done. A high-throughput extractor's context limit is a separate agent requirement, not a compute-slot count.

The plan binds the state and node snapshot hashes and each task's complete payload hash. Apply rejects stale state, duplicate/foreign units, changed payloads and invalid wave capacity/capability assignments. It writes a new state with assigned node/wave and a plan hash. A local O_EXCL lock and atomic replacement protect that state path only. Shared-filesystem locking semantics must be tested; independent Git clones still require a serialized integration/lease authority. Git merge alone is not compare-and-swap across live nodes.

For rescue: checkpoint source, record released units and source lease evidence, refresh target preflight, plan/review, commit/publish manifest, obtain READY, integrate the assignment once, and require STARTED. Preserve the original registration and sampling units; repeated or missing units are integrity failures, not scheduling details.
