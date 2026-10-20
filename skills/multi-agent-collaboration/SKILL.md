---
name: multi-agent-collaboration
description: Coordinate an engineering task across authorized agents with explicit ownership, bounded handoffs and evidence. Use when independent implementation, review or verification adds value; handle ordinary single-agent work directly.
---

Choose the smallest team that resolves the task's uncertainty. Do not spawn agents, send cross-session messages or start watchers unless the user or host instructions authorize them. Existing authorization remains valid; this procedure adds no approval requirement.

Before delegation, state the outcome, acceptance criteria, dependencies, owned files, expected evidence and integration owner. Assign one current owner per thread. Give each worker only the context needed for its decision. Concurrent writers use separate clones or worktrees; never update code underneath a running job.

Use responsibilities as needed: H is the human project decision owner; O coordinates; F implements; P researches; C reviews; V independently verifies; W executes bounded commands; A provides assigned support. I remains a compatibility alias for F. Combine roles for simple work, but an author cannot supply independent verification. Under the governed profile only O/F own production code; V may write isolated verification scripts.

At handoff, identify the exact revision, commands, outputs, unresolved questions and next action. Record it in the project's task system; for the supplied templates, update discussion frontmatter owner and append a dated role entry. Acknowledge evidence actually read without repeating the conversation.

Return defects to the file owner with a reproducer and expected behavior. Settle ordinary implementation choices within authorized scope. Escalate only when a missing requirement, conflicting direction or consequential action actually needs the user's decision.

For a material scope/budget deadlock, present options once, set `owner: H` and `status: blocked`, and stop the affected branch until a trusted human decision reassigns it. Never simulate H or treat a role heading as approval. H overrides project consensus/procedure within host constraints; record criterion changes prospectively and keep prior evidence unchanged.

For adopted governed workflows, use the engineering-governance skill's relevant reference for milestone review, physical-node capability contracts, two-phase migration and worker fix quotas. Routine tasks need not load the entire profile. A node/role label is routing, not authorization or proof of capability.

The coordinator integrates, checks the final artifact and reports the result, validation and material limits. A successful tool invocation or claimed completion does not establish task success. Finish bounded work and exit; use an authorized external scheduler or file watcher for future work, with no idle model calls.
