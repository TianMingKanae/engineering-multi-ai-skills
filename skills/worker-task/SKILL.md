---
name: worker-task
description: Execute a bounded engineering job with explicit commands, resources and output evidence. Use for builds, tests, data jobs, simulations and benchmarks; return design or algorithm changes to their owner unless implementation is assigned.
---

Confirm the task owner, input revision, command, working directory, resource limit, acceptance criteria and expected artifacts. Do not claim work already owned by someone else. Record the claim before executing when a shared queue is used.

Use a documented preflight or small representative run for expensive or newly configured jobs. Check dependencies, resources and output paths. Never invent a dry-run flag or infer that an existing output means this run completed.

Run the command through an authorized execution tool. Capture exact arguments, timestamps, exit code, logs and artifact paths. For long work, use the host's background facility and the command's actual checkpoint support. A detached launch is a handoff, not completion.

On failure, classify the cause and attempt at most one bounded retry when safe and plausibly transient or mechanical. Do not retry migrations or external mutations without evidence of idempotency. Mechanical fixes are in scope only when they cannot alter the computation or behavior under test. Changes to algorithms, dependencies with semantic effects, seeds, thresholds or acceptance criteria go to the implementation owner.

Under the governed profile, W has no production-code authority beyond a recorded mechanical allowance. Default limits are one isolated patch and one safe retry per stable task ID across all wakes/nodes; claim the allowance before editing and never reset it by migration. Use `<role>-fix:` commits and obtain O/F review before main execution or claim integration. Pool size, initialization and path changes can change numerical behavior or function resolution: they are allowed only after declared invariants/preflight establish unchanged semantics. Never change equations, objectives, tolerances or registered criteria. Uncertain or exhausted repairs block to O/F; O escalates top-level choices to H. Dispatcher attempts are not this repair budget.

Check assigned node capabilities locally, not from the model's identity. For migration: quiesce/checkpoint, publish named state/artifact hashes, obtain target READY, transfer the single-writer lease through O, then require target STARTED. Never run both hosts on one checkpoint. In Milestone Mode wake only on a matching completion/scheduler receipt, not an idle model timer.

When blocked, return the exact command and revision, environment, relevant log tail, expected behavior and retry outcome. On success, reopen expected outputs and compare with acceptance criteria before marking done. Transfer only intended artifacts through authorized sharing. Separate command success from an independently verified conclusion.

If the project explicitly adopts a lean execution profile with broader assigned repairs, follow that recorded scope instead of demanding routine O/H acknowledgment. Preserve production ownership and independent checking; uncertain semantics still need review. Use execution-integrity for exact-byte packets and stable reservations across repair roots. Preparation and stored-data checks do not release new execution. Preserve measured failure costs, policy debits and unknown outstanding work separately.
