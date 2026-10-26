---
name: execution-integrity
description: Seal exact-byte run packets and preserve reservations, failed attempts and resource costs across repairs or host changes. Use for bounded expensive jobs, staged readiness or evidence handoffs; not for ordinary edits needing no execution contract.
---

Identify the authorized phase, accountable implementer, input inventory, shared budget and stopping condition. Preparation, stored-data compatibility, execution permission and accepted outcomes are different facts. A preparation receipt never releases an execution job. Use [packets.md](references/packets.md) to seal and check a declared file inventory, and [budgets.md](references/budgets.md) when durable attempt reservations are needed.

Resolve the runtime and imported dependencies on the target node, recording actual paths, versions and hashes in a local receipt. A matching source file or stored-data check does not establish runtime compatibility. Keep each active run's source/configuration snapshot immutable. Repairs run from a fresh root; preserve the old error, outputs and charged attempts. Hash-pinned configuration and evidence need exact-byte transport, including line endings and encoding.

Reserve bounded work before launching. Keep pending/crashed reservations charged until an evidenced settlement; retain failed-attempt costs. Distinguish measurements from conservative policy debits and estimates. Count distinct process lifetimes once, and do not sum a parent interval with its nested diagnostics. Host-wall totals can exceed elapsed wall time when hosts overlap. Neither included helper launches work, measures a process tree, authorizes spending or implements distributed consensus.

Complete ordinary authorized repairs without adding administrative handoffs. Recheck affected invariants and send one scoped delta packet at the applicable milestone; reuse unchanged accepted evidence. A changed criterion, workload, dependency semantics or resource ceiling requires a prospective decision, not a mechanical-fix label.

Report the narrowest supported outcome: declared bytes intact, preparation checked, command finished, criteria passed or independently verified. Name missing journals, unchecked behavior and historical unmeasured costs. Never turn an intact packet, author test or model exit code into a VERIFIED claim.
