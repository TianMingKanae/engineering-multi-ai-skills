---
name: critic-review
description: Review an engineering design, code change or result against requirements and raw evidence. Use for independent correctness, security, reliability, performance and evidence review before integration or consequential claims.
---

Read requirements, patch and relevant outputs yourself. Review the actual revision being integrated. Another role's summary is not proof; do not edit unrelated code to manufacture a finding.

Apply relevant lenses:
- Acceptance: does each required condition pass, including boundaries and failures?
- Correctness: state transitions, concurrency, invariants, compatibility and data integrity.
- Failure handling: swallowed exceptions, fallbacks, partial success and misleading completion.
- Security: trust boundaries, authorization, credentials and injection in changed paths.
- Performance: measured workload, resource limits, comparable baselines and realistic cost.
- Evidence: selection bias, repeated comparisons, skipped failures, uncertainty and overclaiming.

Estimate confidence that each candidate is a real, material defect. Report findings at 80–100 with severity, precise location, failing condition and remedy. Keep 50–79 as labeled notes, and lower-confidence points only as specific cheap checks. Confidence is separate from severity; a speculative severe scenario is not a confirmed finding.

State whether acceptance criteria are met, corrections are needed or the result remains unverified. "No actionable findings" is valid. Give the owner a reproducer rather than silently changing files outside your assignment. Review does not authorize merge, publication or deployment.
