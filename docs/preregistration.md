# Frozen decisions and negative-result provenance

Freeze the decision evaluator, acceptance contract, dependency/adapter files and unit tests in Git before the registered result is created. A criterion must come from that committed contract, not parameters selected after reading outcomes. Unit tests must cover boundary, negative, missing-data and invalid-input cases; a reviewer must verify that the declared test command really executes them. The tool records test exit/output hashes but cannot prove a malicious test command or evaluator is meaningful.

## Reference workflow

The [synthetic example](../examples/preregistration/) evaluates a scalar metric from a binary result using a frozen minimum. It illustrates wiring, not a statistical method. Real interval/win-rate criteria must include their independently reviewed computation, raw-data schema, failure accounting and tests in the frozen file inventory. Binary formats do not by themselves establish an independent derivation.

1. Commit the evaluator, contract and tests (plus any imported local code, runtime lock and input/seed inventory). Populate [PREREGISTRATION.md](../templates/project/context/PREREGISTRATION.md).
2. Before producing the named result, run:

```shell
python scripts/preregister.py seal --root . --id run-1 --spec examples/preregistration/spec.json
```

Seal checks that declared files match the exact committed revision, runs the declared tests, then rechecks file hashes and result absence. A failed check creates no registration. It emits a receipt under context/registrations/ and its SHA-256. The evaluator/contract/tests may be reused by future **explicitly registered** runs, but each stable registration is consumed once.

For known text formats, Git checkout CRLF/LF conversion is accepted at sealing; the receipt records both the committed Git-content hash and the actual working-file hash. Evaluation requires both original identities and rejects even a line-ending change after sealing. Binary declared files must match committed bytes exactly; arbitrary clean/smudge transformations are not accepted.

3. Publish/commit the receipt and pin its hash in an authenticated pre-run approval or protected integration record before launch. The registered job must carry that anchor. A local timestamp/result-path absence alone cannot attest that no data was previously observed elsewhere.
4. Produce the exact registered result using the approved job. The example expects a SQLite `metrics(name,value)` table. Optional adapters support scalar HDF5 `metrics/<name>`, classic MAT `metrics` structures and Parquet `name,value` rows; install only needed packages from requirements-optional.txt. These are declared metric schemas, not universal readers for arbitrary binary files.
5. Evaluate using the **trusted pre-run** receipt hash:

```shell
python scripts/preregister.py evaluate --root . --registration context/registrations/run-1.json --receipt-sha256 <trusted-sha256>
```

The tool verifies the receipt anchor and frozen Git/file hashes, reserves the registration in context/CLAIMS.sqlite before invoking code, hashes the binary result before/after, and accepts only one JSON object with a real boolean `passed`. It records output hashes and the result identity. Decision failure, code mutation, missing/malformed data or evaluator errors finalize as NOT SHOWN. A passed criterion is PROVISIONAL until the independent CLAIMS gate; it is never automatically VERIFIED. CLI exit 1 can mean an honestly logged negative result—inspect the ledger.

The machine ledger is authoritative and automatically projected to context/CLAIMS.generated.md. Finalized rows are immutable through the supplied SQLite schema/API; repeated evaluation of an existing ID is rejected. A crash after reservation leaves a visible unfinished PROVISIONAL entry that blocks silent retries. Recover it through an authorized audit/amendment, preserving the original record; never delete the row. An approved new attempt needs a new ID, reason, parent registration and prospective criteria. Do not disguise repeated sampling as a repair.

## Trust and deployment boundaries

These checks protect the normal execution path, not against an actor with permission to replace the receipt, command, registry database or trusted anchor. Use protected Git approvals, host ACLs and serialized ledger integration; keep result producers and decision approvers separate. Git history is audit evidence, not a trusted wall clock or distributed mutex. Never merge independently written SQLite databases; serialize verdict integration or ingest immutable verdict records into an authorized central ledger. Include all relevant adapters/dependencies and verify the runtime environment; only declared files are hashed.

An evaluator is executable trusted code, not a sandbox. V uses a separate minimal raw-data/specification packet and a different implementation. H may change future direction or waive process, but cannot change a historical registered fail into a pass. Preserve all failures and workload IDs. No script can establish honesty if its host and approval authority are both compromised.
