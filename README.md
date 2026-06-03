# Log-to-Playbook

Paste an error. Get a checklist.

[![Version](https://img.shields.io/badge/version-0.1.1-blue)](https://github.com/guanalex011-hue/Log-to-Playbook/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Log-to-Playbook is a local-first CLI tool that turns error logs, stack traces,
terminal output, and deployment failures into practical debugging playbooks.

It is designed to help developers, sysadmins, students, support teams, and AI
coding agents move from "what does this error mean?" to a safer first diagnosis
checklist.

## Why It Exists

Logs are often long, noisy, and difficult to act on. Log-to-Playbook detects
known failure patterns and returns:

- a short diagnosis
- likely causes
- a step-by-step checklist
- safe diagnostic commands
- a risk label
- matched playbook references

The base system works without AI by using built-in YAML playbooks. AI can be
added later as an explanation layer, but pattern-based diagnosis remains the
source of truth.

## Product Principles

- **Local-first:** logs do not need to leave your machine.
- **Pattern-first:** the MVP works without an AI provider.
- **AI-optional:** AI suggestions must be clearly labeled as suggestions.
- **Safe by default:** destructive commands should not be suggested as a first
  step.
- **Reusable:** every diagnosis pattern can become a playbook.
- **Transparent:** users can inspect which playbook matched their log.

## Current Version

The current implementation is versioned as **v0.1.1**.

MVP capabilities:

- `log2playbook analyze` for files and stdin
- built-in YAML playbooks across Laravel/PHP, Docker, Node.js/npm,
  Python/pip, and Linux server basics
- text, Markdown, and JSON output
- confidence scoring
- risk labels
- command suggestions
- secret redaction before analysis output
- playbook validation
- release workflow and changelog

## Installation

For local development:

```bash
python -m pip install -e ".[dev]"
```

After installation, the CLI is available as:

```bash
log2playbook --version
```

## Documentation

- [Usage guide](docs/usage.md)
- [Playbook authoring guide](docs/playbook-authoring.md)
- [Release process](RELEASE.md)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Usage

Analyze a log file:

```bash
log2playbook analyze ./error.log
```

Read from stdin:

```bash
cat ./error.log | log2playbook analyze -
```

Render Markdown:

```bash
log2playbook analyze ./error.log --format markdown
```

Render JSON:

```bash
log2playbook analyze ./error.log --format json
```

Filter by category:

```bash
log2playbook analyze ./error.log --category docker
```

Validate built-in playbooks:

```bash
log2playbook validate-playbooks
```

Create a starter playbook:

```bash
log2playbook new-playbook
```

## Example

Input:

```text
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```

Output:

```markdown
# Log Diagnosis Report

## Summary

Docker failed to start because the requested host port is already in use.

## Detected Pattern

- Docker port conflict
- Confidence: 0.92
- Risk: medium

## Likely Causes

- A host web server is already listening on the port.
- Another container is using the same host port.
- A previous service did not stop cleanly.

## Checklist

1. Check which process owns the port.
   `sudo lsof -i :80`
2. Check running containers.
   `docker ps`

## Risk Notes

Stopping a production host service can interrupt live traffic.
```

## Playbook Format

Playbooks are YAML files. Each playbook defines the patterns to match, the
diagnosis, safe checks, risk notes, and references.

```yaml
id: docker-port-conflict
title: Docker port conflict
category: docker
severity: medium
risk: medium

patterns:
  - "bind: address already in use"
  - "port is already allocated"
  - "Error starting userland proxy"

keywords:
  - docker
  - port
  - bind

summary: >
  Docker failed to start because the requested host port is already in use.

causes:
  - A host web server is already listening on the port.
  - Another container is using the same host port.
  - A previous service did not stop cleanly.

checks:
  - label: Check which process owns the port
    command: "sudo lsof -i :80"
    risk: low
  - label: Check running containers
    command: "docker ps"
    risk: low

avoid:
  - "Do not kill a production process before identifying what service owns it."

references:
  - "https://docs.docker.com/"
```

## Architecture

```text
src/log_to_playbook/
  analyzer.py      # analysis orchestration
  cli.py           # command-line interface
  loader.py        # YAML playbook loading and validation
  matcher.py       # pattern scoring and ranking
  models.py        # typed result/playbook models
  normalizer.py    # log cleanup
  redactor.py      # secret redaction
  renderer.py      # text, Markdown, and JSON output
  playbooks/       # built-in YAML playbooks
```

## Matching Model

The MVP uses a transparent scoring model:

```text
score = exact_pattern_score
      + regex_pattern_score
      + keyword_score
      + category_hint_score
      - ambiguity_penalty
```

The result includes a confidence score so users can tell whether the diagnosis
is strong or only a rough lead.

## Safety

Log-to-Playbook redacts common secrets before rendering output or preparing data
for future AI-assisted modes:

- API keys
- bearer tokens
- password-like environment variables
- private key blocks
- database URLs
- optional email addresses when privacy mode is enabled

Diagnostic commands include per-step risk labels. Destructive commands should be
kept out of built-in playbooks unless they are clearly marked and avoidable.

## Release

The project uses semantic versioning. The current release line starts at
`0.1.x`.

Release files:

- `CHANGELOG.md` records user-facing changes.
- `RELEASE.md` documents the release process.
- `.github/workflows/ci.yml` runs tests and linting.
- `.github/workflows/release.yml` builds release artifacts for version tags.

## Roadmap

- **Phase 1:** CLI MVP, built-in playbooks, Markdown/JSON output, redaction.
- **Phase 2:** local web UI for paste/upload/export workflows.
- **Phase 3:** optional AI explanations and draft playbook generation.
- **Phase 4:** GitHub Action, Docker image, VS Code extension, and chat
  integrations.

## License

Log-to-Playbook is released under the [MIT License](LICENSE).
