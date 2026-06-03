from __future__ import annotations

from log_to_playbook.loader import load_builtin_playbooks, validate_playbook


def test_builtin_playbooks_have_mvp_coverage() -> None:
    playbooks = load_builtin_playbooks()
    categories = {playbook.category for playbook in playbooks}

    assert len(playbooks) >= 30
    assert {"laravel", "docker", "node", "python", "linux"} <= categories


def test_validate_playbook_rejects_missing_required_fields() -> None:
    errors = validate_playbook({"id": "missing-fields"}, source="inline")

    assert "title is required" in errors
    assert "category is required" in errors
    assert "patterns must contain at least one pattern" in errors
