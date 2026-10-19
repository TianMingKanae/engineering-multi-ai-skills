# engineering-multi-ai-skills

Practical skills and a file-based workflow for engineering teams using multiple AI agents. Works with software, infrastructure, data pipelines, benchmarks and other engineering tasks. No model, vendor, machine or programming language is required.

Use one agent for ordinary work. Add separate implementers, reviewers or verifiers when independent work will resolve a concrete uncertainty. A skill does not create agents or grant permissions: use delegation and tool access already authorized in your environment.

## Skills

| Skill | Use it for |
|---|---|
| [multi-agent-collaboration](skills/multi-agent-collaboration/SKILL.md) | Split a task, define ownership, hand off evidence and converge on a decision. |
| [engineering-plan](skills/engineering-plan/SKILL.md) | Define scope, acceptance criteria, validation and rollback before substantial implementation or an experiment. |
| [critic-review](skills/critic-review/SKILL.md) | Review correctness, failure handling, security, performance and reported evidence. |
| [worker-task](skills/worker-task/SKILL.md) | Execute a bounded assigned job, capture outputs and report reproducible failures. |
| [claim-ledger](skills/claim-ledger/SKILL.md) | Keep engineering conclusions tied to evidence, status and limits. |

`skills/` holds the canonical copies. Copy selected folders into your agent's configured skill directory. For example, to install into a project's Claude skill directory:

```powershell
$destination = 'C:\path\to\your-project\.claude\skills'
New-Item -ItemType Directory -Force $destination | Out-Null
Copy-Item -Recurse .\skills\* $destination
```

Review existing same-named skills before copying. Other hosts can use the same SKILL.md instructions through their loader or as explicit task context. Select only skills relevant to the task.

## Collaboration starter

[templates/project/](templates/project/) contains AGENTS.md, CLAUDE.md and empty context records to adapt in a target repository. Merge the instruction files with existing project rules. Keep the relative layout of `context/`; create one discussion file per topic from [thread.md](templates/thread.md).

| Role | Owns |
|---|---|
| O — coordinator | Scope, ownership, integration and user-facing updates. |
| P — proposer | Options, research and design rationale, when needed. |
| I — implementer | Code and focused tests. |
| C — reviewer | Independent review of the patch and evidence. |
| V — verifier | Independent reproduction of important outcomes. |
| W — worker | Exact assigned commands and artifact collection. |

These are responsibilities, not mandatory sessions. Combine roles when independence is unnecessary. For important decisions, a useful flow is O → P/I → C → V → O; skip stages that add no evidence. Use separate clones or worktrees for concurrent writes and decide who integrates before starting.

### Example: duplicate webhook delivery

1. O opens a thread: a repeated event must cause one database write. Assign I and define the test and owned files.
2. I implements the idempotency check, runs a focused test and hands C the diff plus output.
3. C checks concurrent deliveries, transaction boundaries and error paths. Return any defect to I.
4. V independently reproduces the concurrency check when risk warrants it. O records the conclusion and reports the observed behavior and limits.

See [workflow.md](docs/workflow.md) for the thread contract and failure handling.

## Optional execution tools

Python 3.10+ and its standard library are sufficient. Tools accept `--root` and never configure credentials, synchronize Git, commit, push or change sandbox settings.

### Preview or dispatch assigned work

```powershell
python scripts/dispatch.py --root C:\path\to\project --role I
```

This previews open threads owned by I, without writing state or starting a model. To connect an agent CLI, copy [runner.example.json](examples/runner.example.json), replace its argument array with your installed CLI's supported syntax, and use:

```powershell
python scripts/dispatch.py --root C:\path\to\project --role I --config C:\path\to\runner.json --execute
```

Add `--watch --poll-seconds 300` to poll local files. Arrange synchronization separately from an idle clone; never pull files underneath active jobs. `{prompt}` is substituted into one argument without shell evaluation. No CLI flags or model names are assumed. Each thread is dispatched once per successful input fingerprint; failures get at most `max_attempts` total attempts, with no retry in the same poll. A successful runner must append its role entry or hand the thread to another owner. State, logs and a per-role lock live in `.multi-ai/`. Only one dispatcher per role and project may run at once.

### Run an engineering command

```powershell
python scripts/run_task.py --root C:\path\to\project --id unit-tests -- python -m unittest discover -s tests
```

The command runs without a shell. A log and JSON result under `.multi-ai/runs/` record timestamps, command, exit code and status. Optional `--timeout 600` bounds the direct command. Use your host's background-job facility if detachment is needed. Checkpointing and resumability belong to the command; the wrapper never assumes them or retries automatically.

## Validation

```powershell
python scripts/validate.py
python -m unittest discover -s tests -v
```

Tests use local subprocesses and temporary projects, with no paid model calls or external services.
