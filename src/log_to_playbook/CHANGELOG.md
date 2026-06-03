# Changelog

All notable changes to Log-to-Playbook will be documented in this file.

The project follows semantic versioning.

## [0.1.2] - 2026-06-03

### Added

- `log2playbook changelog` command for viewing the packaged changelog.
- `log2playbook update-info` command for checking the installed version,
  latest GitHub release, changelog URL, and release notes.
- Offline-safe `--no-network` mode for update information.

## [0.1.1] - 2026-06-03

### Added

- MIT license and package license metadata.
- Contributor, security, support, governance, and code of conduct documents.
- Issue forms, pull request template, CODEOWNERS, Dependabot, and security
  workflow scaffolding.
- Usage and playbook authoring documentation.
- Example log and rendered report fixtures.
- Type-checking and coverage threshold steps for CI.

## [0.1.0] - 2026-06-03

### Added

- Initial CLI MVP for analyzing logs from files or stdin.
- Built-in YAML playbooks for Laravel/PHP, Docker, Node.js/npm, Python/pip, and
  Linux server basics.
- Text, Markdown, and JSON renderers.
- Secret redaction for API keys, bearer tokens, password-like values, private
  keys, database URLs, and optional email privacy mode.
- Playbook validation command.
- Python package metadata and `log2playbook` console script.
- CI and release workflow scaffolding.
