# Playbook Authoring Guide

Playbooks are YAML records packaged under `src/log_to_playbook/playbooks`.

## Required Fields

- `id`
- `title`
- `category`
- `risk`
- `patterns`
- `summary`

## Recommended Fields

- `severity`
- `keywords`
- `causes`
- `checks`
- `avoid`
- `references`

## Example

```yaml
id: docker-port-conflict
title: Docker port conflict
category: docker
severity: medium
risk: medium

patterns:
  - "bind: address already in use"
  - "port is already allocated"

keywords:
  - docker
  - port

summary: Docker failed because the requested host port is already in use.

causes:
  - A host web server is already listening on the port.
  - Another container is using the same host port.

checks:
  - label: Check which process owns the port
    command: "sudo lsof -i :80"
    risk: low

avoid:
  - Do not stop a production service before identifying it.

references:
  - "https://docs.docker.com/"
```

## Safety Rules

- Prefer read-only diagnostic commands.
- Mark commands with a realistic `risk`.
- Avoid destructive commands in built-in playbooks.
- Redact secrets in examples.
- Prefer official references when available.
