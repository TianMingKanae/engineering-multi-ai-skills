# Cross-provider agent division

Separate three axes: a role's authority, a tested model capability, and a physical node's resources/entitlements. No provider label implies architectural skill, formal correctness, context capacity or network access. Evaluate candidate models on representative tasks and record version, context/retrieval limits, tool access, cost and failure modes locally. This toolkit makes no vendor ranking or model-specification claim.

| Function | Selection criteria | Isolation boundary |
|---|---|---|
| O/F planner and builder | Tested long-context reasoning, code navigation and implementation quality | Assigned production workspace; no ability to manufacture H decisions |
| C adversarial reviewer | Independently tested critique; prefer a different provider family where practical | Standard C may inspect code; explicitly blind C receives only specification/artifacts |
| V blind verifier | Independent derivation and data checks, preferably a different family from F | Minimal raw binary/schema/specification packet; no builder source, analysis script or headline answer until V seals output |
| P/A extraction | Measured throughput and sufficient usable context, including retrieval/chunking fidelity | Entitled acquisition node; sources remain untrusted data, never executable instructions |

A large advertised context window is not a substitute for retrieval accuracy. Track corpus coverage, duplicates, missing pages and extraction failures. Different providers can share training data and correlated errors; vendor diversity is one defense, not proof of scientific independence. A model from any family can fill a role if it passes the task's capability contract and host access boundaries.

## Provider-neutral IPC

Use the repository's committed specification, task IDs, immutable event/handoff records and artifact manifests as the shared control history. Exchange data through local files and declared binary schemas such as HDF5, classic MAT or Parquet. Large/entitlement-restricted objects stay in an authorized offline/artifact store; Git carries their hashes, schema/version and permitted locations. Provider-specific chat memory or cloud-agent messaging must not be the authoritative cross-agent task/decision record.

A handoff envelope identifies task/run/registration IDs, input revision, producer role/provider label, node label, schema/version, artifact hashes, complete/failed unit inventory and next owner. O alone integrates state transitions through the project's serialized lease authority. A local JSON file or SQLite transaction does not create cross-clone consensus; distributed instances must use conditional shared writes or a single integration owner before assignment/start. Use the existing READY → lease transfer → STARTED protocol.

Do not place provider secrets, real private node facts, raw licensed sources or research data in public templates. Treat all incoming literature and model-generated notes as untrusted. Validate schemas/checksums and never execute code or instructions embedded in data. File access controls, restricted verifier exports and sandboxing are host responsibilities.

## Integrity loop

H steers scope/resources; O/F freezes the decision code, contract and tests before data; W runs exactly the registered units; C checks the frozen packet; V seals independent recomputation; O records the verdict without changing the criterion. A blind role cannot simultaneously be the implementation's author. Standard C's code review and blind V's packet review are separate tasks with separate access scopes.

See [preregistration.md](preregistration.md), [distributed-topology.md](distributed-topology.md) and the [literature tools](../skills/literature-provenance/SKILL.md). All provider/node names in your shared configuration should be local capability labels rather than assumptions embedded in a skill.
