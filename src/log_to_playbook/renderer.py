from __future__ import annotations

from dataclasses import asdict
import json

from log_to_playbook.models import AnalysisResult


def result_to_dict(result: AnalysisResult) -> dict[str, object]:
    payload: dict[str, object] = {
        "detected": result.detected_id,
        "title": result.title,
        "category": result.category,
        "confidence": result.confidence,
        "risk": result.risk,
        "summary": result.summary,
        "causes": result.causes,
        "checks": [asdict(check) for check in result.checks],
        "avoid": result.avoid,
        "references": result.references,
        "matched_patterns": result.matched_patterns,
        "redactions": result.redactions,
    }
    if result.redacted_log is not None:
        payload["redacted_log"] = result.redacted_log
    return payload


def render_json(result: AnalysisResult) -> str:
    return json.dumps(result_to_dict(result), indent=2, ensure_ascii=False)


def render_markdown(result: AnalysisResult) -> str:
    lines = [
        "# Log Diagnosis Report",
        "",
        "## Summary",
        "",
        result.summary,
        "",
        "## Detected Pattern",
        "",
        f"- {result.title}",
        f"- Confidence: {result.confidence:.2f}",
        f"- Risk: {result.risk}",
    ]

    if result.matched_patterns:
        lines.extend(["", "Matched patterns:"])
        lines.extend(f"- `{pattern}`" for pattern in result.matched_patterns)

    lines.extend(["", "## Likely Causes", ""])
    if result.causes:
        lines.extend(f"- {cause}" for cause in result.causes)
    else:
        lines.append("- No built-in cause list is available.")

    lines.extend(["", "## Checklist", ""])
    if result.checks:
        for index, check in enumerate(result.checks, start=1):
            lines.append(f"{index}. {check.label}.")
            if check.command:
                lines.append(f"   `{check.command}`")
            lines.append(f"   Risk: {check.risk}")
    else:
        lines.append("1. Inspect the full error context and recent changes before changing production state.")

    lines.extend(["", "## Commands", ""])
    commands = [check.command for check in result.checks if check.command]
    if commands:
        lines.extend(f"- `{command}`" for command in commands)
    else:
        lines.append("- No command suggestion is available.")

    lines.extend(["", "## Risk Notes", ""])
    if result.avoid:
        lines.extend(f"- {item}" for item in result.avoid)
    else:
        lines.append("- Prefer read-only diagnostic commands before making changes.")

    if result.references:
        lines.extend(["", "## References", ""])
        lines.extend(f"- {reference}" for reference in result.references)

    if result.redactions:
        lines.extend(["", "## Redactions", ""])
        lines.extend(f"- {name}: {count}" for name, count in sorted(result.redactions.items()))

    if result.redacted_log is not None:
        lines.extend(["", "## Redacted Log", "", "```text", result.redacted_log, "```"])

    return "\n".join(lines)


def render_text(result: AnalysisResult) -> str:
    lines = [
        f"Detected: {result.title}",
        f"Confidence: {result.confidence:.2f}",
        f"Risk: {result.risk}",
        "",
        "Likely cause:",
        result.summary,
        "",
        "Checklist:",
    ]

    if result.checks:
        for index, check in enumerate(result.checks, start=1):
            lines.append(f"{index}. {check.label}")
            if check.command:
                lines.append(f"   {check.command}")
            lines.append(f"   Risk: {check.risk}")
    else:
        lines.append("1. Inspect the full error context and recent changes before changing production state.")

    if result.avoid:
        lines.extend(["", "Risk notes:"])
        lines.extend(f"- {item}" for item in result.avoid)

    return "\n".join(lines)
