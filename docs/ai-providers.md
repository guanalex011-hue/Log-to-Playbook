# AI Provider Guide

Log-to-Playbook supports optional AI explanations through OpenAI-compatible
chat completions APIs.

The pattern-based playbook match remains the source of truth. AI output is an
extra suggestion layer.

## Configure OpenAI

```bash
export OPENAI_API_KEY=your_api_key_here

log2playbook ai configure \
  --provider-name openai \
  --base-url https://api.openai.com/v1 \
  --api-key-env OPENAI_API_KEY \
  --model gpt-4o-mini
```

PowerShell:

```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
```

## Configure Another OpenAI-Compatible Provider

Use the provider's OpenAI-compatible base URL:

```bash
log2playbook ai configure \
  --provider-name openrouter \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
  --model provider/model-name
```

## Configure a Local Provider

For local gateways that do not require an API key:

```bash
log2playbook ai configure \
  --provider-name local \
  --base-url http://localhost:1234/v1 \
  --model local-model \
  --no-api-key-required
```

## Test the Provider

Run a real provider check:

```bash
log2playbook ai test
```

Validate the saved config without network access:

```bash
log2playbook ai test --dry-run
```

## Set the Default Model

```bash
log2playbook ai set-model gpt-4o-mini
```

## Show Configuration

```bash
log2playbook ai show
```

Stored API keys are masked in output. Prefer `--api-key-env` over storing a key
directly in the config file.

## Analyze with AI

```bash
log2playbook analyze ./error.log --ai --format markdown
```

Before sending text to the provider, Log-to-Playbook applies the same redaction
rules used by local analysis.
