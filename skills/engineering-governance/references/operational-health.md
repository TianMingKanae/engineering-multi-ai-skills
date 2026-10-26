# Verify the monitoring chain

A watcher PID proves only that a process exists. CLI exit zero proves only that the CLI exited successfully. A configured schedule, synthetic routing test or stored receipt does not establish current unattended delivery. Verify the smallest actual end-to-end chain authorized for the task:

```mermaid
flowchart LR
    E[Assigned event / completion] --> D[Actual dispatch and task fingerprint]
    D --> X[Exit / explicit failure receipt]
    X --> T[Task artifact / role response]
    T --> I[Integration receipt]
    I --> H[Human delivery when required]
```

Keep event/task ID, input fingerprint, ownership epoch, dispatch/run ID, timestamps, exit result, artifact hashes and integration/delivery receipt. Test startup with already-pending assignments, not only newly fetched commits. After synchronization recheck current ownership. Unknown or stale receipt state is UNKNOWN, not healthy; an acknowledged task without a required continuation is a visible delivery gap. Synthetic tests cover routing only and must be labeled as such. Use [OPERATIONS.md](../../../templates/project/context/OPERATIONS.md) for task-specific freshness and response expectations; no universal timeout fits every job.

On a fault, distinguish missing executable, authentication/access error, synchronization failure, quota/rate limit, task failure and missing continuation. Preserve the exact failed attempt and one bounded authorized recovery. Check the installed CLI's own help on the actual target; do not copy launcher flags from another host/version. Reuse the existing registered provider. Do not start a duplicate watcher or revive an explicitly paused automation to hide a gap.

For quota/rate limits, honor a reliable provider reset/Retry-After signal; otherwise use a bounded configured cooldown, an overall retry/deadline budget and an explicit escalation condition. Do not wake a model during cooldown or reset cumulative resource charges. Persist the blocked status and next eligible time; do not report quota-wait as successful work. A provider adapter must classify its structured error, not infer permission or remaining quota from a guessed log string. The toolkit dispatcher still uses its existing generic bounded retries; these health/cooldown fields are a deployment contract, not a newly implemented provider adapter.

Recover only owned processes and assigned work. Preserve unrelated applications, active jobs and immutable run roots. Prove the repaired chain with an actual bounded task and required response/delivery receipt; report any untested leg explicitly. Use scoped milestone review for outcome evidence; operational recovery alone cannot authorize new costly execution or verify a claim.
