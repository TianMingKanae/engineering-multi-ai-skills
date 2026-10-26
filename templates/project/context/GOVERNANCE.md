# Project governance profile

Complete this record when adopting the governed profile. This file documents policy; the dispatcher does not load it as configuration.

| Field | Project setting |
|---|---|
| Profile | basic or governed; record the adopted choice |
| H approval channel | Trusted human decision reference mechanism; never a role heading alone |
| Scope and stop limits | Authorized work, resource budget and stop conditions |
| Production writers | O and F; I is a compatibility alias for F |
| Review gates | pilot-readout, pre-main-launch, claims-entry |
| Worker patch allowance | 1 per stable task ID across all nodes/wakes unless explicitly changed |
| Worker safe retry allowance | 1 per task; retry only idempotent/safe work |
| Event producer | Authorized scheduler identity and local receipt directory |
| Node registry | NODES.md with local capability/preflight evidence |
| Shared lease/claim mechanism | Integration owner and single-writer acknowledgment protocol |
| Cost accounting | Matched baseline/window, model calls, token classes, cost and gate latency |
| Optional lean execution | Explicitly adopted or not; accountable implementer, named files/repair scope, task limits and affected independent review |
| Execution integrity | EXECUTION.md: preparation versus release, exact bytes, reservations and preserved failed costs |
| Role transitions / operational health | ROLES.md ownership epoch and OPERATIONS.md actual task/delivery receipts |

An H decision must identify scope, source and next owner. Preserve old results and distinguish prospective amendments from human waivers. Never convert a waiver into independent verification.

## Human decision record

| Decision ID | Trusted H reference | Scope/budget change | Prior criterion retained | Next owner | Date |
|---|---|---|---|---|---|

## Gate packets

| Gate ID | Milestone | Input revision | Artifact inventory/hash | C outcome | V outcome | Waiver/decision reference |
|---|---|---|---|---|---|---|

## Task-level worker allowance

| Stable task ID | Lease/node | Fix limit/used | Retry limit/used | Invariants/preflight | Fix commit | O/F review |
|---|---|---|---|---|---|---|

Claim an allowance before editing through the shared claim mechanism. Migrations, new thread fingerprints and runner restarts never reset these counters. Dispatcher attempt limits are separate.

When a lean profile is explicitly adopted, record its authorized exceptions to the writer/worker defaults. Do not add administrative waits between already-authorized fixes, host preparation and integration. Keep the applicable milestone, registered criteria and independent review of changed evidence. Reviewed deltas can reference unchanged accepted packet hashes. A preparation receipt never substitutes for execution release.
