# Toolkit maintenance

This repository ships a public, provider-neutral engineering toolkit. The role agreements under templates/project/ are starter artifacts for downstream projects, not this repository's active agent identity.

- Keep examples synthetic. Never add private research details, source snapshots, personal paths, node identities, credentials or actual project data.
- Record user-facing changes under Unreleased in CHANGELOG.md. Do not bump a version for every edit; follow docs/releases.md when preparing a release.
- VERSION is authoritative. A release must align its changelog heading, README version badge/link, CLI output, immutable Git tag and GitHub Release. Do not repeat version numbers in each skill.
- Run scripts/validate.py for changed skills/docs/metadata. Run the tool tests when changing execution/routing, and run the full tests/ suite before release.
- The quickstart's labels.py intentionally contains a practice bug. Its tests should fail before the exercise; do not fix that fixture as part of routine toolkit maintenance.
- Review the intended staged files and publication content before pushing. Deployment, credentials, permissions and recurring automation are outside routine maintenance unless authorized by the user.
