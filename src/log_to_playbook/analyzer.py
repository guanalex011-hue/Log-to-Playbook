from __future__ import annotations

from collections.abc import Sequence

from log_to_playbook.loader import load_builtin_playbooks
from log_to_playbook.matcher import match_playbooks
from log_to_playbook.models import AnalysisResult, Playbook
from log_to_playbook.normalizer import normalize_text
from log_to_playbook.redactor import redact_text


def analyze_log(
    text: str,
    *,
    category: str | None = None,
    privacy: bool = False,
    playbooks: Sequence[Playbook] | None = None,
    include_redacted_log: bool = False,
) -> AnalysisResult:
    """Analyze log text and return the best matching playbook result."""
    redacted = redact_text(text, privacy=privacy)
    normalized = normalize_text(redacted.text)
    available_playbooks = (
        list(playbooks) if playbooks is not None else load_builtin_playbooks()
    )
    matches = match_playbooks(normalized, available_playbooks, category=category)

    if not matches:
        return AnalysisResult(
            detected_id=None,
            title="Unknown log pattern",
            category=category,
            confidence=0,
            risk="unknown",
            summary=(
                "No built-in playbook matched this log. Start with a safe, "
                "read-only inspection of the surrounding stack trace and "
                "recent changes."
            ),
            causes=[],
            checks=[],
            avoid=[],
            references=[],
            matched_patterns=[],
            redactions=redacted.findings,
            redacted_log=redacted.text if include_redacted_log else None,
        )

    best = matches[0]
    playbook = best.playbook
    return AnalysisResult(
        detected_id=playbook.id,
        title=playbook.title,
        category=playbook.category,
        confidence=best.confidence,
        risk=playbook.risk,
        summary=playbook.summary,
        causes=playbook.causes,
        checks=playbook.checks,
        avoid=playbook.avoid,
        references=playbook.references,
        matched_patterns=best.matched_patterns,
        redactions=redacted.findings,
        redacted_log=redacted.text if include_redacted_log else None,
    )
