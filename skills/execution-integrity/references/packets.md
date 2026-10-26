# Exact-byte packets and staged readiness

Use [packet.py](../scripts/packet.py) for a declared input/evidence inventory. It hashes raw bytes and byte lengths, writes a new manifest exclusively, and checks against a separately protected SHA-256 anchor. It does not acquire data, copy a snapshot, resolve dependencies, launch a command or grant permission.

From the toolkit root, this synthetic example requires no external service:

```shell
python skills/execution-integrity/scripts/packet.py seal --root examples/execution/project --spec examples/execution/packet-spec.json --out packet.local.json
python skills/execution-integrity/scripts/packet.py check --root examples/execution/project --packet packet.local.json --sha256 <emitted-packet-sha256> --require-phase preparation
```

The spec has exactly five fields:

```json
{
  "id": "task-17-preparation",
  "phase": "preparation",
  "files": ["settings.json", "task.txt"],
  "checked": ["declared input inventory"],
  "unchecked": ["target runtime", "execution permission", "outcome quality"]
}
```

`phase` is preparation or execution. An execution-phase check rejects a preparation packet even when every hash matches. A successful check emits PACKET_INTACT, never VERIFIED. Scope labels are the producer's declarations; the helper does not establish their truth. All listed files must exist, be unique, project-local regular files and have no symlinked path components. Missing/changed files and wrong anchors fail. Unlisted files are **not** checked. Include imported helpers, settings, dependency-lock files and actual runtime-resolution receipts when they matter. Do not use this tool to imply closure over undeclared dynamic imports, external libraries or the whole filesystem.

Seal once before the relevant work and protect the emitted anchor in the project's trusted approval/integration record. Check on the target after transfer, immediately before launch and after execution; these checks do not prevent a concurrent writer between checks. Use a read-only snapshot/container or suitable filesystem permissions to enforce immutability. The phase is descriptive data, not an execution authorization token. A separately accepted release must bind the packet anchor, target readiness, budget and task scope.

## Bytes, runtimes and repair roots

Do not normalize a hash-pinned file after sealing. A CRLF/LF conversion, BOM insertion or whitespace edit is a byte change. Where Git transports exact-byte inputs, adopt targeted attributes such as `execution/frozen/** -text` **before** sealing, then verify the destination bytes. Avoid blanket conversion of source files or rewriting old receipts. The preregistration helper's known-text conversion tolerance applies at its seal step only; it does not relax this packet contract or post-seal checks.

Record actual runtime executable resolution and imported dependency paths/versions/hashes in a locally held receipt; use a lockfile plus observed import resolution, not a guessed installation path. A correct executable hash alone does not pin every shared library. Treat real paths and machine inventories as private. A stored-fixture check establishes only its stated arithmetic/schema property, not fresh execution quality or cross-host equivalence.

Fix an authorized mechanical defect in the edit checkout, test it, and materialize a new run root/packet. Preserve the failed root, attempt ID and old cost; never patch underneath a live job. Existing unmodified evidence can be referenced by its accepted hash rather than rerun. Changed behavior, criteria or scope needs prospective review, with the old verdict retained.
