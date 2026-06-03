from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import resources
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from log_to_playbook import __version__

LATEST_RELEASE_API_URL = (
    "https://api.github.com/repos/guanalex011-hue/Log-to-Playbook/releases/latest"
)
CHANGELOG_URL = (
    "https://github.com/guanalex011-hue/Log-to-Playbook/blob/main/CHANGELOG.md"
)

ReleaseFetcher = Callable[[str, float], Mapping[str, Any]]


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str | None
    update_available: bool | None
    latest_url: str | None
    changelog_url: str
    latest_notes: str
    error: str | None


def get_packaged_changelog() -> str:
    """Return the changelog bundled with the installed package."""
    return (
        resources.files("log_to_playbook")
        .joinpath("CHANGELOG.md")
        .read_text(encoding="utf-8")
    )


def get_update_info(
    *,
    current_version: str = __version__,
    check_remote: bool = True,
    timeout: float = 5.0,
    fetcher: ReleaseFetcher | None = None,
) -> UpdateInfo:
    """Return local and remote release information."""
    if not check_remote:
        return UpdateInfo(
            current_version=current_version,
            latest_version=None,
            update_available=None,
            latest_url=None,
            changelog_url=CHANGELOG_URL,
            latest_notes="",
            error=None,
        )

    fetch_release = fetcher or _fetch_latest_release
    try:
        payload = fetch_release(LATEST_RELEASE_API_URL, timeout)
    except (HTTPError, OSError, URLError) as exc:
        return UpdateInfo(
            current_version=current_version,
            latest_version=None,
            update_available=None,
            latest_url=None,
            changelog_url=CHANGELOG_URL,
            latest_notes="",
            error=str(exc),
        )

    latest_version = _clean_version(str(payload.get("tag_name", "")))
    update_available = _is_newer_version(latest_version, current_version)
    return UpdateInfo(
        current_version=current_version,
        latest_version=latest_version,
        update_available=update_available,
        latest_url=_optional_str(payload.get("html_url")),
        changelog_url=CHANGELOG_URL,
        latest_notes=str(payload.get("body", "") or ""),
        error=None,
    )


def render_update_info(info: UpdateInfo) -> str:
    latest = info.latest_version or "not checked"
    if info.update_available is True:
        status = "update available"
    elif info.update_available is False:
        status = "up to date"
    elif info.error:
        status = "could not check latest release"
    else:
        status = "remote check skipped"

    lines = [
        f"Current version: {info.current_version}",
        f"Latest version: {latest}",
        f"Status: {status}",
        f"Changelog: {info.changelog_url}",
    ]

    if info.latest_url:
        lines.append(f"Latest release: {info.latest_url}")
    if info.error:
        lines.append(f"Check error: {info.error}")
    if info.latest_notes:
        lines.extend(["", "Latest release notes:", info.latest_notes.strip()])

    return "\n".join(lines)


def _fetch_latest_release(url: str, timeout: float) -> Mapping[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"log-to-playbook/{__version__}",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _clean_version(version: str) -> str:
    return version.strip().removeprefix("v")


def _is_newer_version(candidate: str, current: str) -> bool:
    return _version_tuple(candidate) > _version_tuple(current)


def _version_tuple(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for part in _clean_version(version).split("."):
        digits = ""
        for character in part:
            if not character.isdigit():
                break
            digits += character
        parts.append(int(digits or "0"))
    return tuple(parts)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
