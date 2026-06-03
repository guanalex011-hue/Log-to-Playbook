# Contributing

Thanks for helping improve Log-to-Playbook.

## Good First Contributions

- Add a new YAML playbook for a common error.
- Improve an existing checklist with safer diagnostic steps.
- Add an example log and expected report.
- Improve documentation or wording.

## Development Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m mypy src
```

## Pull Request Checklist

- Keep changes focused on one behavior or one documentation topic.
- Add or update tests when behavior changes.
- Run lint, type check, tests, and build before opening a PR.
- Update `CHANGELOG.md` for user-facing changes.
- Avoid adding destructive diagnostic commands to built-in playbooks.
- Redact secrets from logs, screenshots, and examples.

## Playbook Guidelines

Playbooks should be specific, safe, and transparent.

- Prefer exact log fragments or tight regex patterns.
- Include likely causes that explain the failure.
- Put read-only checks before any command that changes state.
- Add an `avoid` note when a common fix can be risky.
- Include references when an official source exists.

## Commit Style

Use short, conventional-style prefixes when practical:

- `feat:` for user-facing additions
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `chore:` for maintenance

## Code of Conduct

Participation is covered by the [Code of Conduct](CODE_OF_CONDUCT.md).
