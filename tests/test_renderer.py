from __future__ import annotations

import json

from log_to_playbook.analyzer import analyze_log
from log_to_playbook.renderer import render_json, render_markdown, render_text


def test_render_markdown_contains_expected_sections() -> None:
    result = analyze_log("ModuleNotFoundError: No module named 'pandas'")
    rendered = render_markdown(result)

    assert "# Log Diagnosis Report" in rendered
    assert "## Summary" in rendered
    assert "## Checklist" in rendered
    assert "Python module not found" in rendered


def test_render_json_is_machine_readable() -> None:
    result = analyze_log("npm ERR! ERESOLVE unable to resolve dependency tree")
    payload = json.loads(render_json(result))

    assert payload["detected"] == "node-npm-dependency-conflict"
    assert payload["confidence"] > 0
    assert payload["checks"][0]["label"]


def test_render_text_is_human_readable() -> None:
    result = analyze_log("Permission denied: '/var/www/html/storage'")
    rendered = render_text(result)

    assert "Detected:" in rendered
    assert "Checklist:" in rendered


def test_renderers_include_ai_suggestion() -> None:
    result = analyze_log("ModuleNotFoundError: No module named 'pandas'")
    result.ai_suggestion = "Check the active virtual environment first."

    assert "AI Suggestion" in render_markdown(result)
    assert "Check the active virtual environment first." in render_text(result)
    assert json.loads(render_json(result))["ai_suggestion"] == (
        "Check the active virtual environment first."
    )
