---
name: engineering-plan
description: Define an engineering change or experiment before implementation, with observable acceptance criteria and proportionate validation. Use for substantial changes, migrations, benchmarks or ambiguous requirements; keep routine fixes lightweight.
---

Read relevant code, tests and project constraints. State the problem, desired behavior, affected interfaces and out-of-scope work. Resolve facts from artifacts; batch unresolved questions that materially affect the outcome, with recommended choices. Continue independent work while awaiting an answer.

Define observable pass/fail criteria and how to exercise them. Match validation to risk: a bug may need a reproducer and regression check; a migration may need compatibility checks and rollback. Settle critical assumptions before high-cost or irreversible work. Do not impose design approval when the user's instruction already authorizes the change.

For experiments or performance claims, record the hypothesis, primary metric, baseline, workload, seeds or sampling, resource budget, failure accounting and success threshold before inspecting results. Compare arms with equivalent effort. Separate exploratory observations from confirmatory results; label post-result changes and never apply a new rule retroactively.

For long jobs, exercise the launch and a small representative unit first. Record resource limits, output paths and actual resume behavior. Use only dry-run interfaces the command really supports. Launch through the host's authorized background facility; do not keep a model session waiting for hours.

When the project adopts Milestone Mode, batch C/V checks at Pilot Readout, Pre-Main Launch and CLAIMS Entry. Freeze one evidence packet per gate and route it through an authorized scheduler receipt; routine progress is not a reason for a model wake. Record node capability/entitlement preflight and a migration plan before assigning expensive work. If scope, governing assumptions or budget need a top-level choice, block with owner H. Preserve H's trusted decision reference and label any amendment or waiver; do not retroactively relabel observed failure as a passed registered test.

Assess outputs using the original criteria. Preserve failed cases, skipped work and negative results. Have important conclusions reviewed or independently verified when warranted. Record decisions and limits in the project's evidence ledger, then report what was established.
