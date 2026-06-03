from __future__ import annotations

import json
import os
import subprocess
import sys
from io import StringIO
from pathlib import Path

from log_to_playbook.cli import main

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    return subprocess.run(
        [sys.executable, "-m", "log_to_playbook.cli", *args],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )


def test_cli_version() -> None:
    result = run_cli("--version")

    assert result.returncode == 0
    assert "0.2.0" in result.stdout


def test_cli_analyze_file_as_json(tmp_path) -> None:
    log_file = tmp_path / "error.log"
    log_file.write_text(
        "SQLSTATE[HY000]: General error: 1364 Field 'name'",
        encoding="utf-8",
    )

    result = run_cli("analyze", str(log_file), "--format", "json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["detected"] == "laravel-mysql-missing-default"
    assert payload["risk"] == "low"


def test_cli_validate_playbooks() -> None:
    result = run_cli("validate-playbooks")

    assert result.returncode == 0
    assert "Validated" in result.stdout
    assert "playbooks" in result.stdout


def test_cli_changelog_shows_packaged_changelog() -> None:
    result = run_cli("changelog")

    assert result.returncode == 0
    assert "# Changelog" in result.stdout
    assert "0.1.2" in result.stdout
    assert "update-info" in result.stdout


def test_cli_update_info_can_run_without_network() -> None:
    result = run_cli("update-info", "--no-network")

    assert result.returncode == 0
    assert "Current version: 0.2.0" in result.stdout
    assert "Latest version: not checked" in result.stdout
    assert "Changelog:" in result.stdout


def test_main_without_command_prints_help(capsys) -> None:
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Turn logs and stack traces" in captured.out


def test_main_analyze_stdin_markdown(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        sys,
        "stdin",
        StringIO("ModuleNotFoundError: No module named 'pandas'"),
    )

    exit_code = main(["analyze", "-", "--format", "markdown"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Log Diagnosis Report" in captured.out
    assert "Python module not found" in captured.out


def test_main_new_playbook_writes_template(tmp_path) -> None:
    output = tmp_path / "playbook.yml"

    exit_code = main(["new-playbook", "--output", str(output)])

    assert exit_code == 0
    assert "your-playbook-id" in output.read_text(encoding="utf-8")


def test_main_ai_configure_show_and_set_model(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOG2PLAYBOOK_CONFIG", str(tmp_path / "config.json"))

    configure_code = main(
        [
            "ai",
            "configure",
            "--provider-name",
            "manual",
            "--base-url",
            "https://api.example.com/v1",
            "--api-key-env",
            "EXAMPLE_API_KEY",
            "--model",
            "example-model",
        ]
    )
    show_code = main(["ai", "show"])
    model_code = main(["ai", "set-model", "better-model"])
    show_again_code = main(["ai", "show"])

    captured = capsys.readouterr()
    assert configure_code == 0
    assert show_code == 0
    assert model_code == 0
    assert show_again_code == 0
    assert "Provider: manual" in captured.out
    assert "Base URL: https://api.example.com/v1" in captured.out
    assert "Default model: better-model" in captured.out


def test_main_ai_test_dry_run(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("LOG2PLAYBOOK_CONFIG", str(tmp_path / "config.json"))
    main(
        [
            "ai",
            "configure",
            "--provider-name",
            "local",
            "--base-url",
            "http://localhost:1234/v1",
            "--model",
            "local-model",
            "--no-api-key-required",
        ]
    )

    exit_code = main(["ai", "test", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Configuration OK" in captured.out
    assert "http://localhost:1234/v1/chat/completions" in captured.out
