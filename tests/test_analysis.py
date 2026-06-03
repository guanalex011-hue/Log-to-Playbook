from __future__ import annotations

from log_to_playbook.analyzer import analyze_log


def test_analyze_detects_docker_port_conflict() -> None:
    result = analyze_log(
        "Error starting userland proxy: listen tcp4 0.0.0.0:80: "
        "bind: address already in use"
    )

    assert result.detected_id == "docker-port-conflict"
    assert result.title == "Docker port conflict"
    assert result.category == "docker"
    assert result.risk == "medium"
    assert result.confidence >= 0.8
    assert result.checks[0].command == "sudo lsof -i :80"


def test_analyze_can_filter_by_category() -> None:
    result = analyze_log(
        "ModuleNotFoundError: No module named 'pandas'",
        category="python",
    )

    assert result.detected_id == "python-module-not-found"
    assert result.category == "python"


def test_analyze_unknown_log_returns_safe_fallback() -> None:
    result = analyze_log("totally unfamiliar failure text")

    assert result.detected_id is None
    assert result.confidence == 0
    assert result.risk == "unknown"
    assert "No built-in playbook matched" in result.summary
