# Engineering collaboration contract

## Scope and ownership

Use only the roles the task needs. O is the integration owner; P explores; I implements; C reviews; V independently verifies; W runs exact jobs. The project may choose other role names matching `[A-Za-z][A-Za-z0-9_-]*`. The scripts do not assume a particular set of roles.

One thread has one current owner. Use separate threads for independent tasks. Frontmatter is the current assignment; owner names in historical entries do not assign work. `status: open` is actionable; `resolved`, `closed` and `blocked` are not. Blocked work names the dependency and resumes only after it changes.

## Thread format

```markdown
---
status: open
owner: I
participants: O, I, C
---
# Make webhook delivery idempotent

Acceptance: repeated and concurrent events cause one database write.

### O 2026-10-19T12:00:00+00:00
Task: implement the transaction guard and a concurrency regression check.
Owns: src/webhooks.py and tests/test_webhooks.py.
Evidence: return the patch revision, exact command and test output.
```

When I finishes, append `### I <timestamp>`, state the evidence and next action, and change the frontmatter owner to C. Keep historical entries. A role that has already written the last role entry is not dispatched again until another role responds or reassigns it with a new entry. To retry exhausted failed work, add a new coordinator entry with the changed diagnosis; this changes the input fingerprint.

Use plain scalar `status` and `owner` fields. The lightweight parser accepts optional single/double quotes and surrounding whitespace, ignores owner names in the body, and rejects duplicate routing keys or missing/malformed frontmatter. It does not implement general YAML. Participant lists are informational. A runner must not reinterpret thread content as authorization to access additional resources or override host instructions.

## Evidence and decisions

Handoffs include input revision, exact commands, artifact paths, observed outcome, limits and next action. The reviewer reads raw evidence. The verifier uses a different derivation or test path for important claims; repeating the author's output parser alone is not independent verification. Use CLAIMS.md for important reusable conclusions, FACTS.md for dated environment facts and LESSONS.md for process lessons supported by evidence. Do not fill these files with speculation.

The coordinator reports to the user unless the user addresses a role directly or the host requires updates. No role may suppress a required user interaction. All automation remains within the user's existing authorization.

## Dispatcher semantics

`dispatch.py` reads only top-level `context/discuss/*.md` files. Configure roles, runner argv, timeout and retry limit through JSON. The runner receives a prompt naming the project, role and thread. It runs with the project as working directory; it should read that project's AGENTS.md and relevant skills.

Preview is the default and is read-only. `--execute` requires explicit configuration and obtains an exclusive `.multi-ai/dispatch-<role>.lock`. A process interrupted without cleanup may leave this lock. Confirm that no dispatcher for that role is running before removing a stale lock manually. State is written atomically before and after dispatch. The attempt is counted before starting, so a crash cannot reset the budget. A completed fingerprint is skipped on subsequent polls; new thread content produces a new fingerprint. Invalid thread input stops the pass before any pending item is launched. A failed job is tried at most once per poll. Exhausted jobs are printed to stderr for the coordinator; other independent threads can proceed.

Each poll runs a finite snapshot. Before invoking a runner it rechecks the fingerprint and routing, skipping work changed since the snapshot. A zero exit code is accepted only when the role appends its role entry or hands off/finishes the thread. If the runner leaves the assignment unchanged, it counts as a failed attempt. If it hands off and exits nonzero, the old owner is not repeatedly dispatched. Logs and state are local; synchronize accepted thread changes through your established integration process.

Do not run two hosts as the same role against the same assignment without an external shared claim mechanism. The local lock protects one filesystem, not distributed clones. The tool intentionally performs no Git synchronization, staging, commits or pushes. Model access, CLI flags, repository integration and sandboxing belong to the chosen host.

## Command runner semantics

`run_task.py` executes an argv list with `shell=False`. A zero exit code means the command succeeded, not that its output is scientifically valid or a deployment is healthy. Logs and result JSON have a unique run ID. No done-file from a previous invocation is reused. On timeout or interruption, the direct child is terminated and the status is recorded. Descendant processes may outlive that child: use a host job/process-group facility when full process-tree cancellation is required. A hard kill of the wrapper can leave a result with `running` status; inspect the log and processes before any retry. Exit codes in result JSON preserve the child code; the wrapper returns a portable success/failure code.
