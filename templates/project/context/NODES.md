# Local node capability registry

Keep real machine details, private network/entitlement facts and credentials out of public templates. Use local-only records or approved access-controlled storage for sensitive preflight evidence. A role or model name does not establish capability.

| Node label | Eligible roles | Required capability | Verified preflight/time | Capacity/stop limit | Artifact access | Current lease |
|---|---|---|---|---|---|---|

Synthetic routing examples: `access-node` for entitled source retrieval, `compute-node` for suitable compute resources, `scheduler-node` for bounded background scheduling. These labels assert no real entitlement or hardware configuration.

An affinity-routed thread declares `node: <node-label>`. Supply the matching `--node` to the dispatcher after verifying capabilities. A mismatched or missing node label skips that assignment; the CLI label itself is not authentication. Inadequate capabilities require a handoff, never a silent change to algorithms, runtime or assumptions.
