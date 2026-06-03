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
