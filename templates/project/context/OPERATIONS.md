# Task monitoring and recovery record

This is a deployment contract, not dispatcher configuration. Use existing authorized automation; the template creates none.

| Task/event and input fingerprint | Ownership epoch | Dispatch/run ID and actual start | Exit/failure and log | Role artifact/hash | Integration receipt | Required human delivery | Last activity / freshness bound |
|---|---|---|---|---|---|---|---|

| Fault class | Observed error/evidence | Bounded recovery owner | Next eligible time / deadline | Cumulative attempts/cost | Actual continuation receipt | Untested legs |
|---|---|---|---|---|---|---|

States may include idle, dispatching, task-failed, quota-wait, retry-exhausted and unknown. These are observations, not proof of a healthy chain. Define freshness against the specific task. Preserve paused routes, honor provider reset signals and never create a second provider as an unrecorded fallback.
