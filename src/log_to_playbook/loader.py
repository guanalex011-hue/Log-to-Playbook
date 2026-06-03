from __future__ import annotations

from collections.abc import Iterable
from importlib import resources
from typing import Any

import yaml

from log_to_playbook.models import Check, Playbook

REQUIRED_FIELDS = ("id", "title", "category", "risk", "patterns", "summary")


class PlaybookValidationError(ValueError):
    """Raised when a YAML playbook does not satisfy the expected schema."""


def load_builtin_playbooks() -> list[Playbook]:
    """Load all packaged YAML playbooks."""
    playbooks: list[Playbook] = []
    playbook_root = resources.files("log_to_playbook.playbooks")

    for resource in sorted(playbook_root.iterdir(), key=lambda item: item.name):
        if resource.suffix not in {".yaml", ".yml"}:
            continue
        playbooks.extend(
            load_playbooks_from_text(
                resource.read_text(encoding="utf-8"),
                source=resource.name,
            )
        )

    return playbooks


def load_playbooks_from_text(text: str, *, source: str = "<string>") -> list[Playbook]:
    """Load one or more playbooks from YAML text."""
    raw_items: list[dict[str, Any]] = []

    for document in yaml.safe_load_all(text):
        if document is None:
            continue
        if isinstance(document, list):
            raw_items.extend(_require_mapping(item, source=source) for item in document)
        else:
            raw_items.append(_require_mapping(document, source=source))

    playbooks = []
    for item in raw_items:
        errors = validate_playbook(item, source=source)
        if errors:
            raise PlaybookValidationError(f"{source}: " + "; ".join(errors))
        playbooks.append(_to_playbook(item))

    return playbooks


def validate_playbook(raw: dict[str, Any], *, source: str) -> list[str]:
    """Return schema validation errors for a raw playbook mapping."""
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if not raw.get(field):
            errors.append(f"{field} is required")

    patterns = raw.get("patterns")
    if not isinstance(patterns, list) or not patterns:
        errors.append("patterns must contain at least one pattern")

    checks = raw.get("checks", [])
    if checks is not None and not isinstance(checks, list):
        errors.append("checks must be a list")

    if not isinstance(source, str) or not source:
        errors.append("source is required")

    return errors


def _require_mapping(value: Any, *, source: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PlaybookValidationError(f"{source}: playbook entry must be a mapping")
    return value


def _as_str_list(value: Iterable[Any] | None) -> list[str]:
    if value is None:
        return []
    return [str(item) for item in value]


def _to_playbook(raw: dict[str, Any]) -> Playbook:
    return Playbook(
        id=str(raw["id"]),
        title=str(raw["title"]),
        category=str(raw["category"]),
        severity=str(raw.get("severity", raw.get("risk", "unknown"))),
        risk=str(raw["risk"]),
        patterns=_as_str_list(raw.get("patterns")),
        keywords=_as_str_list(raw.get("keywords")),
        summary=str(raw["summary"]).strip(),
        causes=_as_str_list(raw.get("causes")),
        checks=[
            Check(
                label=str(check.get("label", "Inspect the related log context")),
                command=str(check.get("command", "")),
                risk=str(check.get("risk", "low")),
            )
            for check in raw.get("checks", [])
            if isinstance(check, dict)
        ],
        avoid=_as_str_list(raw.get("avoid")),
        references=_as_str_list(raw.get("references")),
    )
