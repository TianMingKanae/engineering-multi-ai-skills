---
name: multi-agent-collaboration
description: Coordinate an engineering task across authorized agents with explicit ownership, bounded handoffs and evidence. Use when independent implementation, review or verification adds value; handle ordinary single-agent work directly.
---

Choose the smallest team that resolves the task's uncertainty. Do not spawn agents, send cross-session messages or start watchers unless the user or host instructions authorize them. Existing authorization remains valid; this procedure adds no approval requirement.

Before delegation, state the outcome, acceptance criteria, dependencies, owned files, expected evidence and integration owner. Assign one current owner per thread. Give each worker only the context needed for its decision. Concurrent writers use separate clones or worktrees; never update code underneath a running job.

Use responsibilities as needed: O coordinates; P proposes; I implements; C reviews; V independently verifies; W executes bounded commands. Combine roles for simple work. A result's author cannot supply its independent verification.

At handoff, identify the exact revision, commands, outputs, unresolved questions and next action. Record it in the project's task system; for the supplied templates, update discussion frontmatter owner and append a dated role entry. Acknowledge evidence actually read without repeating the conversation.

Return defects to the file owner with a reproducer and expected behavior. Settle ordinary implementation choices within authorized scope. Escalate only when a missing requirement, conflicting direction or consequential action actually needs the user's decision.

The coordinator integrates, checks the final artifact and reports the result, validation and material limits. A successful tool invocation or claimed completion does not establish task success. Finish bounded work and exit; use an authorized external scheduler or file watcher for future work, with no idle model calls.
