from __future__ import annotations

from log_to_playbook.redactor import redact_text


def test_redacts_common_secrets() -> None:
    redacted = redact_text(
        "OPENAI_API_KEY=sk-abc123\n"
        "Authorization: Bearer token123\n"
        "DATABASE_URL=mysql://user:pass@localhost/app"
    )

    assert "sk-abc123" not in redacted.text
    assert "token123" not in redacted.text
    assert "user:pass" not in redacted.text
    assert redacted.findings["env_secret"] == 1
    assert redacted.findings["bearer_token"] == 1
    assert redacted.findings["database_url"] == 1


def test_privacy_mode_redacts_email_addresses() -> None:
    redacted = redact_text("Contact admin@example.com", privacy=True)

    assert "admin@example.com" not in redacted.text
    assert "[REDACTED_EMAIL]" in redacted.text
