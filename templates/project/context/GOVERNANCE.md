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
