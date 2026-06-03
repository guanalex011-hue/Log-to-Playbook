# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

## Reporting a Vulnerability

Do not publish exploit details, secrets, or private logs in a public issue.

Preferred process:

1. Use GitHub Security Advisories for this repository if available.
2. If private reporting is unavailable, open a public issue with the title
   `Security report` and include only a high-level summary.
3. Wait for a maintainer to coordinate a private disclosure channel before
   sharing sensitive details.

## Security Scope

Relevant issues include:

- Secret redaction bypasses.
- Unsafe command suggestions in built-in playbooks.
- Package supply-chain or release artifact concerns.
- Log handling behavior that leaks sensitive information.

Out of scope:

- Reports that require sharing real private credentials.
- Issues in third-party tools unless Log-to-Playbook directly worsens the risk.
