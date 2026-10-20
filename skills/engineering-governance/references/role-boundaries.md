# Role boundaries, local fix quota and blind verification

## Single-letter governed profile

| Role | Responsibility | Write boundary |
|---|---|---|
| H | Human principal; scope, resource ceilings and final project decisions | Human decisions through a trusted channel; never a model identity |
| O | Orchestrator and integration owner | Assigned production code, governance and approved integration |
| F | Primary implementation/solver owner | Assigned production code and tests |
| W | Batch/command worker | Queue state, outputs, logs and explicitly permitted mechanical repairs |
| P | Literature/evidence researcher | Cited research notes and proposals; no production edits |
| C | Critic | Findings and gate decisions; no production edits |
| V | Blind verifier | New independent verification scripts/reports in an isolated verifier workspace; no solver edits |
| A | Auxiliary | Explicit bounded support assignment; no production authority by default |

Only O/F own production changes. I in the basic walkthrough is an alias for F's responsibility; do not create two overlapping implementation owners. The dispatcher still matches the literal owner label and does not rewrite I to F. V's verification scripts are an explicit, narrow exception to "only O/F write code": they are independent test artifacts, never a patch to the implementation. Combining F and V in one session does not provide independence. Model/provider and physical node are separate configuration choices.

## Local self-fix quota

Default worker budget: **one mechanical patch and one safe retry per stable task ID**, across wakes, fingerprints, nodes and migrations. O/F must explicitly set any different quota before work; W cannot replenish it by renaming a file or restarting. Record `fix_limit`, `fixes_used`, `retry_limit`, `retries_used`, owning node and review owner in the queue. Claim a repair allowance before editing using the project's shared task/lease mechanism. Parallel clones must not each spend the same allowance.

A candidate mechanical repair may change paths, create a missing directory, correct launch wiring, adjust a process pool or restore initialization only when O/F's declared invariants show no computational semantics change. Check function resolution and versions. Duplicate module names, pool-dependent randomness, reduction order, runtime/solver selection, precision or fallback behavior make it **non-mechanical until proven otherwise**. Resource changes still need capacity checks. Never promise bitwise equality based on the category of change alone.

W must not alter equations, objectives, physical assumptions, seeds, datasets, tolerances, acceptance thresholds, search effort, result readers or registered criteria. An initialization change that selects another backend is not mechanical. Uncertain fixes, exhausted quotas or repeated failure produce a bug bundle to O/F and block the job. O escalates scope/resource choices to H.

For an allowed fix: record quota consumption, apply the smallest isolated change, repeat preflight and the safe retry, compare the declared invariants, and commit only named files with `<role>-fix:`. Example: `W-fix: resolve approved launcher path for task-17`. O/F reviews the separate patch before main execution or merging its outputs into a claim. Keep the old error and quota record even if the patch succeeds. The dispatcher retry counter limits runner invocations, **not** this task-level repair/retry budget.

## Blind binary verification

1. O packages immutable raw result files (for example, MAT/HDF5), hashes, input IDs, units/schema, a separately stated mathematical/specification contract, registered criteria and tolerances. These are data and public task requirements, not solver implementation. Keep the contract fixed before V starts.
2. V receives a minimal workspace with that packet. Do not expose the solver, its analysis script, claimed headline number or explanatory comments before V commits an independent recomputation script and output. Git worktrees alone do not hide implementation in a shared Git object database: use a separate minimal export and host file/tool restrictions when blindness matters.
3. Re-derive using the contract/first principles, not the solver's reader or report generator. Check shapes, units, missing/failed cases, residuals and invariants. Use safe data readers; never deserialize untrusted executable objects or execute callbacks from artifact files. Tool availability is a preflight, not a reason to infer the result.
4. Seal V's script/output revision and hashes, then reveal the author's comparison packet. Report VERIFIED / WRONG / DOUBTFUL / UNVERIFIABLE with expected criteria, absolute/relative differences and scope. If the schema or contract is insufficient, stop as UNVERIFIABLE rather than guess. O maps unresolved checks to PROVISIONAL or NOT SHOWN in the claim ledger; failed evidence can VOID an existing claim.
5. No self-verification. Another authorized independent actor validates V's own newly asserted outcomes when needed. Record accidental solver exposure as loss of blindness; do not label that run blind. H can waive a workflow gate, but a waiver never upgrades evidence to VERIFIED.

Example: `V: seal independent check for artifact-set-17`. Binary outputs alone cannot verify an undocumented model or prove general correctness; name the properties actually tested.
