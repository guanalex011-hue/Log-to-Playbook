from __future__ import annotations

import json
import subprocess
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "log_to_playbook.cli", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_version() -> None:
    result = run_cli("--version")

    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_analyze_file_as_json(tmp_path) -> None:
    log_file = tmp_path / "error.log"
    log_file.write_text("SQLSTATE[HY000]: General error: 1364 Field 'name'", encoding="utf-8")

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
