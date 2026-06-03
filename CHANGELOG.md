# Changelog

All notable changes to Log-to-Playbook will be documented in this file.

The project follows semantic versioning.

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
