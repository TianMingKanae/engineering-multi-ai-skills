---
status: open
owner: I
participants: O, I, C
---
# Normalize labels consistently

## Task

Fix normalize_label in labels.py so labels produce stable keys.

Acceptance criteria:
- Lowercase letters.
- Remove leading and trailing whitespace.
- Collapse each run of whitespace, including tabs and newlines, into one hyphen.
- Return an empty string for empty or whitespace-only input.

Owns: labels.py and an appended entry in this thread. Keep test_labels.py unchanged.
Validation: run the four supplied unittest tests and report the observed output.
Handoff: append an I entry and change the frontmatter owner to C.

### O 2026-10-19T00:00:00+00:00
This is a synthetic onboarding task. The implementation handles a single space but does not meet all whitespace requirements. Fix the function, run the supplied tests and hand the evidence to C. No additional agents or runner configuration are required.
