from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from log_to_playbook.models import Playbook
from log_to_playbook.normalizer import normalize_text

EXACT_PATTERN_SCORE = 50
REGEX_PATTERN_SCORE = 30
KEYWORD_SCORE = 10
CATEGORY_HINT_SCORE = 5
AMBIGUITY_PENALTY = 10


@dataclass(frozen=True)
class Match:
    playbook: Playbook
    score: int
    confidence: float
    matched_patterns: list[str]


def match_playbooks(
    text: str,
    playbooks: Sequence[Playbook],
    *,
    category: str | None = None,
) -> list[Match]:
    """Score and rank playbooks for the provided text."""
    normalized = normalize_text(text)
    candidates = [
        candidate
        for playbook in playbooks
        if (candidate := _score_playbook(normalized, playbook, category=category))
        is not None
    ]

    if not candidates:
        return []

    matched_categories = {candidate.playbook.category for candidate in candidates}
    penalty = (
        AMBIGUITY_PENALTY
        if category is None and len(matched_categories) > 1
        else 0
    )
    adjusted = [
        Match(
            playbook=candidate.playbook,
            score=max(candidate.score - penalty, 1),
            confidence=_confidence(max(candidate.score - penalty, 1)),
            matched_patterns=candidate.matched_patterns,
        )
        for candidate in candidates
    ]
    return sorted(
        adjusted,
        key=lambda item: (item.score, item.playbook.id),
        reverse=True,
    )


def _score_playbook(
    text: str,
    playbook: Playbook,
    *,
    category: str | None,
) -> Match | None:
    if category is not None and playbook.category != category:
        return None

    lower_text = text.lower()
    score = 0
    matched_patterns: list[str] = []

    for pattern in playbook.patterns:
        pattern_score = _score_pattern(text, lower_text, pattern)
        if pattern_score:
            score += pattern_score
            matched_patterns.append(pattern)

    for keyword in playbook.keywords:
        if keyword.lower() in lower_text:
            score += KEYWORD_SCORE

    if category is not None and category == playbook.category and score:
        score += CATEGORY_HINT_SCORE

    if score == 0:
        return None

    return Match(
        playbook=playbook,
        score=score,
        confidence=_confidence(score),
        matched_patterns=matched_patterns,
    )


def _score_pattern(text: str, lower_text: str, pattern: str) -> int:
    if pattern.startswith("regex:"):
        expression = pattern.removeprefix("regex:").strip()
        if re.search(expression, text, flags=re.IGNORECASE | re.MULTILINE):
            return REGEX_PATTERN_SCORE
        return 0

    if pattern.lower() in lower_text:
        return EXACT_PATTERN_SCORE
    return 0


def _confidence(score: int) -> float:
    return round(min(score / 100, 0.99), 2)
