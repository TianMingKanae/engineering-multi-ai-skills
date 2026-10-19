---
name: worker-task
description: Execute a bounded engineering job with explicit commands, resources and output evidence. Use for builds, tests, data jobs, simulations and benchmarks; return design or algorithm changes to their owner unless implementation is assigned.
---

Confirm the task owner, input revision, command, working directory, resource limit, acceptance criteria and expected artifacts. Do not claim work already owned by someone else. Record the claim before executing when a shared queue is used.

Use a documented preflight or small representative run for expensive or newly configured jobs. Check dependencies, resources and output paths. Never invent a dry-run flag or infer that an existing output means this run completed.

Run the command through an authorized execution tool. Capture exact arguments, timestamps, exit code, logs and artifact paths. For long work, use the host's background facility and the command's actual checkpoint support. A detached launch is a handoff, not completion.

On failure, classify the cause and attempt at most one bounded retry when safe and plausibly transient or mechanical. Do not retry migrations or external mutations without evidence of idempotency. Mechanical fixes are in scope only when they cannot alter the computation or behavior under test. Changes to algorithms, dependencies with semantic effects, seeds, thresholds or acceptance criteria go to the implementation owner.

When blocked, return the exact command and revision, environment, relevant log tail, expected behavior and retry outcome. On success, reopen expected outputs and compare with acceptance criteria before marking done. Transfer only intended artifacts through authorized sharing. Separate command success from an independently verified conclusion.
