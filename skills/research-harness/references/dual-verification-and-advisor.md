# Dual-scope adversarial verification and process adaptation

## 1. Dual-scope adversarial review

Single-reviewer verification misses systematic assumptions shared across an entire round. Split verification into two explicit checks that must **both** pass before any attempt clears a round:

1. **Per-attempt verifier (`single`):** Reads one candidate solution in isolation, starting from the presumption that every algebraic step, baseline match, unit conversion, script assertion and citation is wrong until justified directly from code, raw output or primary text.
2. **Round side-by-side verifier (`cross`):** Reads all candidate attempts from the same round side by side. Specifically checks:
   - Did multiple directions silently use the same narrow test subset, seed or default approximation?
   - Does a counterexample or edge case in Direction B falsify a hidden assumption in Direction A?
   - Did two attempts apply unequal tuning, iteration budgets or baseline definitions while appearing consistent internally?

Never treat an author's own rerun or script check as either `single` or `cross` verification. An attempt reaches `outcome: pass` only when both `single` and `cross` record `pass` from reviewers distinct from the attempt author.

## 2. Isolated lemma extraction

At the end of a round, an independent auditor inspects partial and failed attempts to salvage valid sub-results:
1. Isolate candidate lemma or verified diagnostic fact from surrounding failed proof/code.
2. Rewrite it self-contained with all preconditions (`scope`) explicit.
3. Have a verifier who did not author the source attempt check the standalone fragment in isolation.
4. Record it in `context/LEDGER.md`; do not promote fragments with implicit or unverified preconditions.

## 3. Process advisor and `STANDING_INSTRUCTIONS.md`

The orchestrator tracks round assignments and cannot simultaneously retain full multi-round failure logs without diluting its context. Assign a separate **Process Advisor** pass at round close (or after recurring failures):
- Read cross-round objections in `context/ATTEMPTS.md` and divergence between `single` and `cross` verdicts.
- Identify recurring process failures (for example: omitted corner cases, unverified third-party assumptions, mismatched baselines, skipped failure counts).
- Append or update concise guardrails in `context/STANDING_INSTRUCTIONS.md` targeting those failure modes for future provers and verifiers.
- Keep the Process Advisor strictly methodological: it may refine verification checklists, briefing focus and slot allocation heuristics, but it must never express an opinion on which scientific claim is true or which direction will succeed.

## 4. Consolidation and final exposition audit

After a candidate clears dual verification and the orchestrator closes remaining high-value exploration:
1. Compare surviving verified solutions and select the cleanest result meeting the project's criteria.
2. Expand it into the manuscript or technical report (`technical-writing` skill), keeping every boundary condition intact.
3. Run a final correspondence check between the formatted document and the verified ledger (`critic-review` / `claim-ledger`) so exposition edits introduce no silent generalizations, changed numbers or missing qualifiers.
