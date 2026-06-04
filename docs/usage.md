# Usage Guide

## Analyze a File

```bash
log2playbook analyze ./error.log
```

## Analyze Stdin

```bash
cat ./error.log | log2playbook analyze -
```

## Choose an Output Format

```bash
log2playbook analyze ./error.log --format text
log2playbook analyze ./error.log --format markdown
log2playbook analyze ./error.log --format json
```

## Filter by Category

```bash
log2playbook analyze ./error.log --category docker
```

Available categories:

- `docker`
- `laravel`
- `linux`
- `node`
- `python`

## Privacy Mode

Privacy mode also redacts email addresses:

```bash
log2playbook analyze ./error.log --privacy
```

## Export a Report

```bash
log2playbook analyze ./error.log --format markdown --output report.md
```

## Validate Playbooks

```bash
log2playbook validate-playbooks
```

## View Changelog

```bash
log2playbook changelog
```

## Check Update Information

Check the installed version against the latest GitHub release:

```bash
log2playbook update-info
```

Show local update information without a network request:

```bash
log2playbook update-info --no-network
```

Render update information as JSON:

```bash
log2playbook update-info --format json
```

## Run Health Checks

Check the local CLI, packaged playbooks, AI provider configuration, and update
information:

```bash
log2playbook doctor
```

Skip the GitHub release check in offline environments:

```bash
log2playbook doctor --no-network
```

Render a structured health report for automation:

```bash
log2playbook doctor --no-network --format json
```

## Configure an AI Provider

Use any OpenAI-compatible chat completions provider by setting a base URL,
API-key source, and default model:

```bash
log2playbook ai configure \
  --provider-name openai \
  --base-url https://api.openai.com/v1 \
  --api-key-env OPENAI_API_KEY \
  --model gpt-4o-mini
```

Show the saved configuration:

```bash
log2playbook ai show
```

Set a new default model:

```bash
log2playbook ai set-model gpt-4o-mini
```

Test the provider:

```bash
log2playbook ai test
```

Add an AI suggestion to a report:

```bash
log2playbook analyze ./error.log --ai --format markdown
```
