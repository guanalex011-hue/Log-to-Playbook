from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    label: str
    command: str
    risk: str


@dataclass(frozen=True)
class Playbook:
    id: str
    title: str
    category: str
    severity: str
    risk: str
    patterns: list[str]
    keywords: list[str]
    summary: str
    causes: list[str]
    checks: list[Check]
    avoid: list[str]
    references: list[str]


@dataclass(frozen=True)
class RedactionResult:
    text: str
    findings: dict[str, int]


@dataclass(frozen=True)
class AnalysisResult:
    detected_id: str | None
    title: str
    category: str | None
    confidence: float
    risk: str
    summary: str
    causes: list[str]
    checks: list[Check]
    avoid: list[str]
    references: list[str]
    matched_patterns: list[str]
    redactions: dict[str, int]
    redacted_log: str | None = None
