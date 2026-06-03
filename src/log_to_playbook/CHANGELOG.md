# Changelog

All notable changes to Log-to-Playbook will be documented in this file.

The project follows semantic versioning.

## [0.2.0] - 2026-06-03

### Added

- OpenAI-compatible AI provider configuration via `log2playbook ai configure`.
- Manual provider base URL support for OpenAI, OpenRouter, local gateways, and
  other chat-completions-compatible providers.
- `log2playbook ai show`, `log2playbook ai set-model`, and `log2playbook ai test`.
- Optional API-key-free mode for local providers.
- `log2playbook analyze --ai` for provider-backed explanations while keeping
  pattern-based playbooks as the source of truth.

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
