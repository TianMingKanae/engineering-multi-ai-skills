# Isolated briefings, attempts record and intermediate ledger

Long-horizon discovery fails in two predictable ways: workers waste context re-reading full logs (and mimic earlier mistakes), or rejected runs bury genuinely useful lemmas and dead-end exclusions inside prose notes. Separate the **attempts record**, the **verified intermediate ledger** and **per-direction briefings**.

## 1. Record of attempts (`context/ATTEMPTS.md`)

Log every round attempt, pass or fail, with the minimal facts needed to avoid repeating errors:
- `round`, `attempt_id`, `direction`, `author` and `method`
- `artifact` (exact script, revision or output path, never a summary alone)
- `single_verdict` and `cross_verdict` (`pending`, `pass` or `fail`)
- `objection` (required whenever `outcome` or either verdict is `fail` or `partial`)

Synthetic example row:

```markdown
| Round | ID | Direction | Author | Method | Single | Cross | Outcome | Objection / Artifact |
|---|---|---|---|---|---|---|---|---|
| 1 | a-1a | dir-norm | F | Constant step size 0.1 | pass | fail | fail | Counterexample at weight ratio 4:1 violates bound (`out/a1a.txt`) |
```

## 2. Verified intermediate ledger (`context/LEDGER.md`)

Reserve `context/CLAIMS.md` for headline project conclusions. Use `LEDGER.md` for intermediate building blocks that speed up later rounds:

- **Confirmed fragments:** Even if attempt `a-1a` failed its main goal, a sub-lemma established along the way can be salvaged. Extract it as a standalone statement with explicit scope (`When weights sum to 1 and step <= 1/L...`), re-verify it in isolation via an `isolated_verifier` distinct from `author`, and list its exact `frag_id`, `source_attempt` and `scope`.
- **Excluded dead ends:** When a bound, parameter regime or hypothesis is falsified cleanly, record `dead_id`, `direction` (or `*` if global), `reason`, `evidence` and `revisit_if` (the exact assumption whose change would re-open that direction). Later explorers skip dead ends unless that revisit condition is triggered.

## 3. Per-direction isolated briefings

Never feed all threads into every worker. Before dispatching a round, assemble a focused briefing for each direction containing only:
1. Target `direction` goal and success criterion.
2. Active guardrails from `context/STANDING_INSTRUCTIONS.md`.
3. Confirmed reusable fragments from `context/LEDGER.md`.
4. Excluded dead ends matching that `direction` or global (`*`).
5. Prior attempts and failing objections **for that direction only**, pointing to long scripts or outputs by file path.

Synthetic briefing excerpt:

```markdown
# Briefing: dir-norm
Goal: Bound contraction factor under non-uniform weights.

## Active standing rules
- [rule-1] Verify boundary ratios > 3:1 before asserting global monotonicity.

## Verified reusable fragments
- [frag-1] Trace sum remains non-increasing for step <= 1 / trace(M) (scope: positive-definite M; isolated verifier: C).

## Excluded dead ends
- [dead-1] Constant unscaled step 0.1 fails at weight ratio 4:1 (`out/a1a.txt`; revisit_if: normalized weights).

## Prior attempts on dir-norm
- [a-1a] Round 1 | outcome=fail | objection: Counterexample at weight ratio 4:1 (`out/a1a.txt`).
```

If a direction accumulates two or more failures on the same obstruction with no new confirmed fragment, treat it as **stalled** and re-dispatch literature review (`P`) with the narrow obstruction query before spending more prover slots.
