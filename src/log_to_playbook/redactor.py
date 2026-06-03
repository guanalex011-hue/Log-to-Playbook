from __future__ import annotations

import re

from log_to_playbook.models import RedactionResult

REDACTION_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "private_key",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
            flags=re.DOTALL,
        ),
        "[REDACTED_PRIVATE_KEY]",
    ),
    (
        "bearer_token",
        re.compile(r"(Authorization:\s*Bearer\s+)[A-Za-z0-9._~+/=-]+", flags=re.IGNORECASE),
        r"\1[REDACTED_TOKEN]",
    ),
    (
        "env_secret",
        re.compile(
            r"\b([A-Z0-9_]*(?:API_KEY|TOKEN|SECRET|PASSWORD|PASS|PWD)[A-Z0-9_]*\s*=\s*)[^\s]+",
            flags=re.IGNORECASE,
        ),
        r"\1[REDACTED]",
    ),
    (
        "database_url",
        re.compile(
            r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb|redis)://[^\s'\"<>]+",
            flags=re.IGNORECASE,
        ),
        "[REDACTED_DB_URL]",
    ),
)

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def redact_text(text: str, *, privacy: bool = False) -> RedactionResult:
    """Redact common secrets from log text."""
    redacted = text
    findings: dict[str, int] = {}

    for name, pattern, replacement in REDACTION_RULES:
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            findings[name] = count

    if privacy:
        redacted, count = EMAIL_PATTERN.subn("[REDACTED_EMAIL]", redacted)
        if count:
            findings["email"] = count

    return RedactionResult(text=redacted, findings=findings)
