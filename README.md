# Log-to-Playbook

Paste an error. Get a checklist.

[![Version](https://img.shields.io/badge/version-0.3.0-blue)](https://github.com/guanalex011-hue/Log-to-Playbook/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Log-to-Playbook is a local-first CLI tool that turns logs, stack traces, terminal output, and deploy failures into practical debugging checklists.

It helps you answer:

- What probably failed?
- What should I check first?
- Which commands are safe to run?
- How risky is the next step?
- Which playbook matched this log?

It works without AI. Built-in YAML playbooks do the matching, so your logs can stay on your machine.

## Quick Start

Install from GitHub:

```bash
python -m pip install "log-to-playbook @ git+https://github.com/guanalex011-hue/Log-to-Playbook.git@v0.3.0"
```

Analyze a log file:

```bash
log2playbook analyze ./error.log
```

Or pipe a log directly:

```bash
echo "ModuleNotFoundError: No module named 'pandas'" | log2playbook analyze -
```

If `log2playbook` is not on your PATH, use:

```bash
python -m log_to_playbook.cli analyze ./error.log
```

## Example

Input:

```text
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```

Command:

```bash
log2playbook analyze ./error.log --format markdown
```

Output:

```markdown
# Log Diagnosis Report

## Summary

Docker failed to start because the requested host port is already in use.

## Detected Pattern

- Docker port conflict
- Confidence: 0.99
- Risk: medium

## Likely Causes

- A host web server is already listening on the port.
- Another container is using the same host port.
- A previous service did not stop cleanly.

## Checklist

1. Check which process owns the port.
   `sudo lsof -i :80`
   Risk: low
2. Check running containers.
   `docker ps`
   Risk: low
```

## Common Commands

| Goal | Command |
| --- | --- |
| Analyze a file | `log2playbook analyze ./error.log` |
| Analyze stdin | `cat ./error.log \| log2playbook analyze -` |
| Output Markdown | `log2playbook analyze ./error.log --format markdown` |
| Output JSON | `log2playbook analyze ./error.log --format json` |
| Filter by category | `log2playbook analyze ./error.log --category docker` |
| Redact emails too | `log2playbook analyze ./error.log --privacy` |
| Export a report | `log2playbook analyze ./error.log --format markdown --output report.md` |
| Validate playbooks | `log2playbook validate-playbooks` |
| Create a playbook template | `log2playbook new-playbook` |
| Show changelog | `log2playbook changelog` |
| Check update info | `log2playbook update-info` |
| Run health checks | `log2playbook doctor` |
| Configure AI provider | `log2playbook ai configure --base-url URL --model MODEL` |
| Test AI provider | `log2playbook ai test` |
| Set default AI model | `log2playbook ai set-model MODEL` |

## Supported Categories

The current MVP ships with 30 built-in playbooks across:

- Docker
- Laravel/PHP
- Linux server basics
- Node.js/npm
- Python/pip

More categories can be added by contributing YAML playbooks.

## Output Formats

Use the format that fits your workflow:

- `text` for terminal reading
- `markdown` for reports, issues, and documentation
- `json` for automation and AI coding agents

Example:

```bash
log2playbook analyze ./error.log --format json
```

## Safety and Privacy

Log-to-Playbook is designed to be safe by default:

- Logs are analyzed locally.
- Basic secrets are redacted before output.
- Diagnostic commands include risk labels.
- Built-in playbooks should prefer read-only checks first.
- Destructive commands should not be suggested as the first step.

Redacted values include API keys, bearer tokens, password-like environment variables, private key blocks, database URLs, and optional email addresses when `--privacy` is enabled.

## Health Check

Run `doctor` when setup feels suspicious, before opening an issue, or before wiring the CLI into automation:

```bash
log2playbook doctor
```

For offline environments:

```bash
log2playbook doctor --no-network
```

For automation:

```bash
log2playbook doctor --no-network --format json
```

The report checks package importability, Python runtime, built-in playbooks, AI provider configuration, and update information.

## AI Provider Integration

Log-to-Playbook can add an optional AI explanation layer using any OpenAI-compatible chat completions provider.

Configure a provider with a manual base URL and default model:

```bash
log2playbook ai configure \
  --provider-name openai \
  --base-url https://api.openai.com/v1 \
  --api-key-env OPENAI_API_KEY \
  --model gpt-4o-mini
```

For local or gateway providers that do not require an API key:

```bash
log2playbook ai configure \
  --provider-name local \
  --base-url http://localhost:1234/v1 \
  --model local-model \
  --no-api-key-required
```

Test the provider:

```bash
log2playbook ai test
```

Set the default model:

```bash
log2playbook ai set-model gpt-4o-mini
```

Analyze with AI suggestions:

```bash
log2playbook analyze ./error.log --ai --format markdown
```

AI mode is optional. Pattern-based playbooks remain the source of truth, and logs are redacted before being sent to the configured provider.

## Development Setup

Clone the repository:

```bash
git clone https://github.com/guanalex011-hue/Log-to-Playbook.git
cd Log-to-Playbook
```

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run checks:

```bash
python -m ruff check .
python -m mypy src
python -m pytest --cov=log_to_playbook --cov-report=term-missing --cov-fail-under=80
python -m build
```

## Documentation

- [Usage guide](docs/usage.md)
- [AI provider guide](docs/ai-providers.md)
- [Playbook authoring guide](docs/playbook-authoring.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Release process](RELEASE.md)

## Project Status

Current version: `0.3.0`

This is an early MVP. The core CLI, built-in playbooks, redaction, output renderers, OpenAI-compatible AI provider integration, package metadata, health checks, update/changelog commands, examples, and release artifacts are in place. The next major additions are a local web UI and integrations such as GitHub Actions and editor extensions.

## License

Log-to-Playbook is released under the [MIT License](LICENSE).
