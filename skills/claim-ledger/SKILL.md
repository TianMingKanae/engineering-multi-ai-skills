---
name: claim-ledger
description: Maintain evidence-backed engineering conclusions and their limits. Use when a result is accepted, independently reproduced, revised, invalidated or reported; do not require a ledger for trivial edits.
---

Use the project's conclusion register, or context/CLAIMS.md in the starter. Name the statement, status, exact input revision, evidence paths and commands, author, verifier when applicable, date and scope limits. The integration owner maintains it; others propose evidence-backed changes.

Statuses:
- VERIFIED: acceptance criteria passed and an independent person, agent or appropriately independent automated check reproduced the relevant outcome. Name the verifier and method.
- PROVISIONAL: supporting evidence exists but a named check or dependency remains open.
- NOT SHOWN: the specified test did not establish the statement. Preserve the observed result and failure accounting.
- VOID: evidence or assumptions were invalidated or superseded. Keep the reason and replacement reference.

Distinguish "tests passed" from "safe in production", and "faster on workload X" from a universal speedup. State the narrowest supported conclusion. An author's second run strengthens evidence but does not constitute independent verification.

Update entries alongside evidence when practical. Do not silently overwrite a conclusion after new results; record the transition and reason. Reports may include new work outside the ledger if clearly identified as unverified. No edit is needed when evidence still supports the existing statement.
