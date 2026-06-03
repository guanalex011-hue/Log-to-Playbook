from __future__ import annotations

from log_to_playbook.updates import (
    UpdateInfo,
    get_packaged_changelog,
    get_update_info,
    render_update_info,
)


def test_get_packaged_changelog_contains_latest_entry() -> None:
    changelog = get_packaged_changelog()

    assert changelog.startswith("# Changelog")
    assert "## [0.1.2]" in changelog
    assert "update-info" in changelog


def test_get_update_info_reports_newer_release() -> None:
    def fetcher(_url: str, _timeout: float) -> dict[str, str]:
        return {
            "tag_name": "v0.1.3",
            "html_url": "https://github.com/example/releases/tag/v0.1.3",
            "body": "Bug fixes",
        }

    info = get_update_info(current_version="0.1.2", fetcher=fetcher)

    assert info.latest_version == "0.1.3"
    assert info.update_available is True
    assert info.latest_url == "https://github.com/example/releases/tag/v0.1.3"


def test_get_update_info_handles_network_failure() -> None:
    def fetcher(_url: str, _timeout: float) -> dict[str, str]:
        raise OSError("offline")

    info = get_update_info(current_version="0.1.2", fetcher=fetcher)

    assert info.latest_version is None
    assert info.update_available is None
    assert "offline" in str(info.error)


def test_render_update_info_includes_changelog_url() -> None:
    rendered = render_update_info(
        UpdateInfo(
            current_version="0.1.2",
            latest_version="0.1.2",
            update_available=False,
            latest_url="https://github.com/example/releases/tag/v0.1.2",
            changelog_url="https://github.com/example/CHANGELOG.md",
            latest_notes="",
            error=None,
        )
    )

    assert "Current version: 0.1.2" in rendered
    assert "Latest version: 0.1.2" in rendered
    assert "Status: up to date" in rendered
    assert "Changelog: https://github.com/example/CHANGELOG.md" in rendered
