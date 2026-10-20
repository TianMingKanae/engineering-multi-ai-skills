# Changelog

User-facing changes are recorded here by release. `VERSION` is the current toolkit version; Git tags and GitHub Releases identify the exact released revision. Versions apply to the toolkit as a whole, not independently to each skill.

## [Unreleased]

No unreleased changes.

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

[Unreleased]: https://github.com/TianMingKanae/engineering-multi-ai-skills/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/TianMingKanae/engineering-multi-ai-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/TianMingKanae/engineering-multi-ai-skills/releases/tag/v0.1.0
