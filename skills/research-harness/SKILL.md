---
name: research-harness
description: Run iterative multi-direction research, proof discovery and mechanism debugging loops using neutral orchestration, isolated briefings, dual-scope adversarial verification, verified intermediate ledgers and cross-round process adaptation.
---

# Iterative research harness

Use this pattern when single-shot implementation or linear note-taking cannot resolve an open research question, solver discrepancy or competing design hypothesis. Rather than one thread accumulating unbounded history, divide exploration into rounds with isolated context, dual verification and persistent structured memory.

## Roles and neutrality

- **Neutral orchestrator (`O`):** tracks global round state, partitions exploration budget across explicit `directions`, dispatches briefing writers and evaluates verifier consensus. The orchestrator does not derive proofs, fix solver equations or declare a hypothesis likely or dead on intuition; only ledgered evidence promotes or excludes a claim.
- **Literature reviewer (`P`):** supplies initial definitions, bounds and prior results before Round 1, and can be re-dispatched mid-run whenever a direction stalls repeatedly on the same technical obstruction.
- **Parallel explorers / provers (`F`, `W` or designated workers):** each slot receives one assigned `direction` and its tailored briefing, choosing its own concrete derivation or experiment without seeing noisy transcripts from unrelated directions.
- **Dual-scope adversarial verifiers (`C` and `C-cross`):** start from the assumption that every step, assumption, baseline comparison, number and citation is incomplete or incorrect until checked directly. Acceptance requires clearing **both** per-attempt review and round-wide side-by-side comparison.
- **Isolated auditor and process advisor:** separate from the orchestrator so neither role overflows its context window or self-certifies intermediate work.

## Round workflow

1. **Scope directions:** Orchestrator registers competing hypotheses or sub-claims in `context/ATTEMPTS.md` (and optional machine state via `scripts/harness_ledger.py`), assigning *what* to test rather than dictating *how*.
2. **Write isolated briefings:** For each assigned direction, compile a targeted briefing containing active `STANDING_INSTRUCTIONS.md` guardrails, reusable entries from `context/LEDGER.md`, relevant excluded dead ends and only the prior attempts and objections for that direction. Pass large specs or data by file path for selective reading.
3. **Run parallel exploration:** Explorers test assigned directions independently and record artifact paths, exact commands and outputs.
4. **Execute dual verification:**
   - *Single-attempt audit:* verify internal derivations, boundary conditions, code/artifact correspondence and source citations for each attempt in isolation.
   - *Round side-by-side audit:* inspect all attempts from the round together to expose shared blind spots, unstated assumptions or mismatched comparison baselines across directions.
   - Detailed protocol: [dual-verification-and-advisor.md](references/dual-verification-and-advisor.md).
5. **Update persistent memory (`ATTEMPTS.md` and `LEDGER.md`):**
   - Record every attempt (including failures and partial results) with its method and exact failing objection in `ATTEMPTS.md`.
   - Extract confirmed intermediate lemmas, invariants or diagnostic mechanisms—even from otherwise rejected attempts—rewrite them as self-contained statements, verify each in isolation with an independent auditor, and promote them into `context/LEDGER.md`.
   - Log verified counterexamples or excluded regimes under Excluded Dead Ends in `LEDGER.md` with explicit revisit conditions so later rounds do not repeat them.
   - Formats and synthetic example: [briefing-and-ledger.md](references/briefing-and-ledger.md).
6. **Adapt standing instructions (`Process Advisor`):** At round close, an advisor reviews verification logs across rounds for recurring mistakes or verifier blind spots and updates `context/STANDING_INSTRUCTIONS.md` for future rounds. If one direction stalls repeatedly on the same objection (`>= 2` failures without progress), re-dispatch `P` for targeted literature lookup before launching more explorer calls.
7. **Consolidate verified output:** Once a direction clears dual verification and any remaining high-value alternatives are exhausted, compare accepted solutions, draft the final manuscript or report against the verified ledger, and audit the compiled deliverable (`technical-writing` + `critic-review` / `claim-ledger`) to ensure no new error entered during exposition.

## Optional state and briefing helper

```shell
python scripts/harness_ledger.py init --state context/harness_state.json
python scripts/harness_ledger.py add-direction --state context/harness_state.json --id dir-scale --goal "Verify step-size invariance under norm constraint"
python scripts/harness_ledger.py briefing --state context/harness_state.json --direction dir-scale
python scripts/harness_ledger.py status --state context/harness_state.json
```

Paths above are relative to this skill directory. The helper enforces dual-verifier pass conditions, non-self-verified fragment promotion and failure objections in local JSON with standard-library Python only; it never runs models, schedules jobs or touches Git. Keep headline empirical verdicts in `context/CLAIMS.md` and reserve `context/LEDGER.md` for verified intermediate building blocks and excluded dead ends.
