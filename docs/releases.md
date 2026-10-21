# Versioning and releases

## Version contract

`VERSION` is the single source for the toolkit's stable `MAJOR.MINOR.PATCH` version. The dispatcher, command runner and preregistration CLI read it for `--version`; distribute VERSION alongside the root scripts. Standalone skill helper scripts ship under the same release without requiring the root VERSION file after skill installation. Skills and templates do not repeat version metadata in every file.

Use a minor increment for a meaningful capability or governance module and a patch increment for compatible fixes/documentation updates. Explicitly describe behavioral incompatibilities even before 1.0. Keep published tags immutable; never move an old tag to new code. GitHub Releases expose the publication timestamps.

## For each change

Add user-facing changes under Unreleased in CHANGELOG.md, grouping additions, behavior changes, fixes and upgrade notes as appropriate. Internal-only changes need not claim a new feature or performance result. Keep private project details, environment identifiers, raw data and credentials out of notes and attached artifacts.

## Prepare a release

1. Set VERSION, update the README version badge/link and move the completed Unreleased entries into a matching changelog heading. Leave Unreleased ready for future work.
2. Run `python scripts/validate.py` and `python -m unittest discover -s tests -v`. Check the three root command-line tools with `--version`. Install requirements-optional.txt in a disposable environment and rerun for a complete binary/PDF adapter release check; absent extras produce explicit skips. The quickstart fixture intentionally fails until a reader fixes it; do not confuse that practice task with release-test failure.
3. Review upgrade notes and scan the actual publication tree for private information. Inspect the intended diff and ensure no runtime state, logs or credentials are staged.
4. Commit and push only the intended changes. Tag that exact commit as `v<VERSION>` and push the tag through the authorized repository workflow.
5. Publish a GitHub Release for that existing tag using the corresponding changelog entry, including its upgrade notes. Avoid generated notes that accidentally include unrelated private context. Confirm the release points to the intended commit, the README link resolves and `--version` agrees with the published tag.

The validator checks the VERSION format, the current changelog heading, README version badge/link, skill metadata, local documentation links and Python syntax. Remote tag/release state still needs explicit verification during publication; the validator never publishes anything.
