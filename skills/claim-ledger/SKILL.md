---
name: claim-ledger
description: Maintain evidence-backed engineering conclusions and their limits. Use when a result is accepted, independently reproduced, revised, invalidated or reported; do not require a ledger for trivial edits.
---

Use the project's conclusion register, or context/CLAIMS.md in the starter. Name the statement, status, exact input revision, evidence paths and commands, author, verifier when applicable, date and scope limits. The integration owner maintains it; others propose evidence-backed changes.

In the governed profile, a CLAIMS Entry milestone reviews the frozen result inventory before promotion. Record the gate ID, relevant H decision/waiver, artifact hashes and verifier revision. For blind verification, give V only raw binary results, schema/units, inputs and a separately specified contract; V seals its independent script/output before seeing the solver implementation or headline comparison. An insufficient contract is UNVERIFIABLE, not a guessed pass. Blindness requires an isolated packet/workspace; a shared Git worktree does not hide source. See the engineering-governance role-boundaries reference for the full protocol.

Statuses:
- VERIFIED: acceptance criteria passed and an independent person, agent or appropriately independent automated check reproduced the relevant outcome. Name the verifier and method.
- PROVISIONAL: supporting evidence exists but a named check or dependency remains open.
- NOT SHOWN: the specified test did not establish the statement. Preserve the observed result and failure accounting.
- VOID: evidence or assumptions were invalidated or superseded. Keep the reason and replacement reference.

Distinguish "tests passed" from "safe in production", and "faster on workload X" from a universal speedup. State the narrowest supported conclusion. An author's second run strengthens evidence but does not constitute independent verification.

H may override project direction or a procedural gate, but cannot change what the old evidence established. Keep human waivers separate from VERIFIED. Cross-node results need parity evidence or explicit environment limits. Do not claim token/cost reductions without a matched baseline and deduplicated measurements; an 80% reduction is a proposed target until measured.

When using the toolkit's preregister.py, the machine source is context/CLAIMS.sqlite, projected to CLAIMS.generated.md. A consumed registration cannot be silently evaluated again, and finalized failures are not overwritten. Link its ID, protected receipt anchor, result hash and frozen evaluator revision from the curated ledger. Passed machine criteria remain PROVISIONAL. New approved runs disclose a parent/reason; use serialized integration rather than merging independently written databases. Role/provider diversity or a prestigious venue never substitutes for independent evidence.

Update entries alongside evidence when practical. Do not silently overwrite a conclusion after new results; record the transition and reason. Reports may include new work outside the ledger if clearly identified as unverified. No edit is needed when evidence still supports the existing statement.
