# Changelog

User-facing changes are recorded here by release. `VERSION` is the current toolkit version; Git tags and GitHub Releases identify the exact released revision. Versions apply to the toolkit as a whole, not independently to each skill.

## [Unreleased]

## [0.4.0] - 2026-10-26

### Added

- `execution-integrity` skill for staged readiness, immutable run roots, exact-byte evidence transport and durable attempt accounting.
- `packet.py` to seal declared project-local files and validate a protected manifest anchor, byte inventory and preparation/execution phase. Success means PACKET_INTACT, not execution permission or independent verification.
- `budget.py` with frozen local budget policy, transactional reservations, total attempt limits, preserved pending/failed attempts, unique cost IDs and immutable evidenced settlements. Reports measured costs, policy debits, outstanding reservations and overruns separately.
- Synthetic packet/cost examples and behavioral regression tests, including concurrent reservation admission, failed-cost carry, duplicate accounting rejection and byte/phase mismatch rejection.
- Lean execution and operational-health guides; EXECUTION, ROLES and OPERATIONS project records for scoped delta review, exclusive provider transitions and actual event-to-delivery evidence.

### Changed

- Governance and worker guidance now distinguish conservative defaults from an explicitly adopted, bounded lean profile; ordinary authorized repairs need no administrative acknowledgment.
- Claim and distributed-handoff guidance separates stored compatibility, source integrity, execution coverage and outcome quality. Merged reviewer/verifier responsibilities retain independence and exposure limits.
- README architecture connects preparation packets, execution release and resource reservations; VERSION, release metadata and root CLI versions advance together.

### Upgrade notes

- Existing dispatcher, planner and preregistration CLIs remain unchanged. New tools are opt-in and do not start jobs, modify credentials or create automations. Operational health/cooldown records are deployment guidance, not a new provider adapter.
- Adopt the lean profile explicitly in the target project's governance record before overriding conservative role/repair defaults. It never waives independent outcome checks or prospectively registered criteria.
- Packet hashes are exact-byte identities, including encoding and line endings; configure transport before sealing and protect the emitted anchor externally. Only declared files are checked. Runtime/import resolution and snapshot immutability still need target-host controls.
- Keep one authoritative budget ledger; never merge per-clone copies as fresh capacity. Reservations do not enforce process limits, settlement evidence is operator-supplied, and SQLite triggers are not a security boundary. Unknown crashed work stays reserved until evidenced settlement.

## [0.3.1] - 2026-10-21

### Fixed

- `dispatch.py` recognizes `### ROLE MM-DD HH:MM` entry headers as well as ISO timestamps, so a role that already wrote the last entry in that format is not dispatched again.
- A thread with several owners (`owner: C, F`) is skipped with a warning instead of stopping dispatch for every thread, including when it changes during a pass; a runner that hands off to several owners counts as a handoff.
- `preregister.py evaluate` called before the registered result file exists stops without consuming the registration; failures after reservation still finalize as NOT SHOWN.
- Preregistration seal accepts Git checkout CRLF/LF conversion for more source formats, including MATLAB `.m`, R, Julia, shell/PowerShell, CSV/TSV, SQL, C/C++, JavaScript/TypeScript, XML and TeX/BibTeX.
- An interrupted `preregister.py evaluate` is recorded as `UNFINISHED`, not `PROVISIONAL`, so it cannot read as supporting evidence in the generated ledger.
- The preregistration line-ending regression test now writes the opposite of each committed Git blob's line endings, so both LF and CRLF source blobs exercise distinct working/Git hashes without changing text content.

### Changed

- `rebalance.py --apply` now requires `--nodes` and checks the plan against that node snapshot, instead of trusting the topology stored in the plan file.

### Upgrade notes

- **CLI change:** `rebalance.py --apply plan.json --state state.json` must now also pass `--nodes nodes.json`, the same node snapshot the plan was made from. A plan made from a different snapshot is rejected and the state is left unchanged.
- Threads with `owner: C, F` are no longer dispatched to anyone; give each thread one owner to dispatch it.
- Ledger readers should treat `UNFINISHED` as a distinct status: no verdict, not a pass. Earlier interrupted evaluations recorded as PROVISIONAL with reason "evaluation reserved" keep their stored record; review them through an audit, not by rewriting the row.

## [0.3.0]

### Added

- `distributed-orchestration` skill and a deterministic capacity/memory/capability-aware planner for independent tail units, with read-only planning and explicit stale-state-checked apply.
- Cross-provider capability and neutral IPC architecture documentation, physical high-core/network/edge topology, offline-archive rights records and safe straggler rescue procedures.
- `preregister.py` to seal committed evaluator/contract/test files before named binary data exist, bind a trusted receipt hash and record one immutable machine verdict per registration.
- Automatic NOT SHOWN accounting for failed criteria or evaluator integrity/errors, a SQLite claims ledger and regenerated Markdown projection; successful criteria remain PROVISIONAL pending independent verification.
- `literature-provenance` skill with DOI content-negotiation/BibTeX identity checks, explicit venue tiers, exact short quote/page/heading location and rights-gated offline corpus indexing.
- Optional scalar HDF5/classic MAT/Parquet metric adapters and PDF extraction, synthetic fixtures and regression tests.
- Expanded NODES and new PREREGISTRATION templates with model/provider capability labels, pre-run anchors, unit inventories and amendment provenance.

### Changed

- README architecture now connects cross-provider roles, physical node tiers, frozen decision scripts, raw artifacts and independent CLAIMS review.
- Governance/planning/claim procedures explicitly require pre-data decision-code tests, registered failures and independently isolated verifier packets.
- VERSION, README release metadata, CLI version output and this release record advance together to 0.3.0.
- Pre-registration records both Git-content and working-file hashes so ordinary Windows text checkout conversion is supported without allowing changes after sealing.

### Upgrade notes

- Existing standard/milestone dispatcher routing remains available; new planners and preregistration tools are explicit opt-in commands, not background services.
- Apply tail plans only after source quiescence and reviewed lease transfer. The local lock is not distributed consensus; serialize cross-clone state and ledger integration through an authorized authority.
- Register evaluators only after committing their complete declared file inventory and running meaningful tests. Pin the receipt in a protected pre-run approval; local timestamps alone cannot prove data were unseen.
- A negative/error consumes the registration and stays NOT SHOWN. An approved new attempt requires a new ID with a disclosed parent/reason, never silent reruns or overwritten failures.
- Install only required optional binary/PDF adapters; core tools remain standard-library based. Optional tests explicitly skip without dependencies. Classic MAT support is schema-limited, not universal.
- Configure venue policy locally and verify acquisition/redistribution rights. Preprint/unknown tiers are blocked by default; no venue label proves correctness. Quote page extraction and heading detection have explicit limitations.
- No guarantee is made about vendor superiority, perfect utilization, savings percentages, adversary-proof storage or scientific validity from a machine criterion alone.

## [0.2.0]

### Added

- `engineering-governance` skill with four reusable patterns: H human authority and decision gates, milestone review and token accounting, physical-node affinity and migration, and role boundaries with worker fix quotas and blind verification.
- Governance architecture diagrams and before/after comparisons, plus project templates for decisions, node capabilities, migration handoffs and task-level repair allowances.
- Optional `--mode milestone` routing using completion/scheduler receipts bound to the exact thread fingerprint. C/V require a matching Pilot Readout, Pre-Main Launch or CLAIMS Entry scheduler gate.
- Optional `--node` routing for explicitly node-bound assignments; stale, mismatched and missing event receipts do not dispatch work.
- Twelve governance regression tests, bringing the toolkit test suite to 28 tests.
- Central `VERSION`, CLI `--version`, this changelog, maintainer instructions, a release checklist and release-metadata validation.

### Changed

- H is reserved for human decisions in every dispatcher mode; H-owned threads never run as a model, even if accidentally marked open.
- Skills, project rules and templates now describe H/O/F/W/P/C/V/A responsibilities. I remains the basic-mode compatibility label for F's implementation responsibility.
- Governance distinguishes human waivers from verified evidence, task-level repair quotas from runner retries, local node labels from actual capability proof, and local locks from distributed leases.
- Blind verification requires a minimal raw-artifact/specification packet and independently sealed outputs rather than source-visible worktrees.

### Upgrade notes

- Existing quickstart and basic workflows keep standard routing by default. Milestone Mode is opt-in on each invocation; it does not create a scheduler or watcher.
- Rename any former automated role H. A thread with `node:` now requires a matching `--node`; omit that field for unbound basic assignments.
- Adopt governance templates deliberately. File ACLs, human/event authentication, distributed leases and task-level fix quotas remain host/project responsibilities.
- No matched-workload benchmark establishes an 80% token/cost reduction; this remains a measurement target.

## [0.1.0] - 2026-10-19

### Added

- Initial public toolkit with five engineering skills, collaboration templates, a provider-neutral dispatcher and a command runner.
- Read-only task preview, bounded retries/timeouts, per-role local locks and 16 tool tests.
- MIT License, Mermaid collaboration diagram and a three-minute quickstart with an intentionally failing practice task and four acceptance tests.

[Unreleased]: https://github.com/TianMingKanae/engineering-multi-ai-skills/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/TianMingKanae/engineering-multi-ai-skills/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/TianMingKanae/engineering-multi-ai-skills/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/TianMingKanae/engineering-multi-ai-skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/TianMingKanae/engineering-multi-ai-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/TianMingKanae/engineering-multi-ai-skills/releases/tag/v0.1.0
