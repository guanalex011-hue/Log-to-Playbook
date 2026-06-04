from __future__ import annotations

import platform
import sys
from collections.abc import Iterable
from dataclasses import dataclass

from log_to_playbook import __version__
from log_to_playbook.ai import (
    AIProviderConfig,
    AIProviderError,
    build_chat_completions_url,
    get_config_path,
    load_ai_config,
    resolve_api_key,
)
from log_to_playbook.loader import load_builtin_playbooks
from log_to_playbook.updates import CHANGELOG_URL, get_update_info

CheckStatus = str


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    label: str
    status: CheckStatus
    message: str
    details: dict[str, object]


@dataclass(frozen=True)
class DoctorReport:
    status: CheckStatus
    version: str
    python_version: str
    checks: list[DoctorCheck]


def run_doctor(*, check_remote: bool = True, timeout: float = 5.0) -> DoctorReport:
    """Run local project health checks and return a structured report."""
    checks = [
        _check_package(),
        _check_playbooks(),
        _check_ai_provider(),
        _check_updates(check_remote=check_remote, timeout=timeout),
    ]
    return DoctorReport(
        status=_overall_status(check.status for check in checks),
        version=__version__,
        python_version=platform.python_version(),
        checks=checks,
    )


def render_doctor_report(report: DoctorReport) -> str:
    lines = [
        "Log-to-Playbook Doctor",
        "",
        f"Overall: {report.status}",
        f"Version: {report.version}",
        f"Python: {report.python_version}",
        "",
        "Checks:",
    ]
    for check in report.checks:
        lines.append(f"- {check.label}: {check.status}")
        lines.append(f"  {check.message}")
    return "\n".join(lines)


def _check_package() -> DoctorCheck:
    return DoctorCheck(
        name="package",
        label="Package",
        status="ok",
        message=f"log-to-playbook {__version__} is importable.",
        details={
            "version": __version__,
            "python": platform.python_version(),
            "executable": sys.executable,
        },
    )


def _check_playbooks() -> DoctorCheck:
    try:
        playbooks = load_builtin_playbooks()
    except Exception as exc:
        return DoctorCheck(
            name="playbooks",
            label="Built-in playbooks",
            status="error",
            message=f"Built-in playbooks could not be loaded: {exc}",
            details={"error": str(exc)},
        )

    categories = sorted({playbook.category for playbook in playbooks})
    return DoctorCheck(
        name="playbooks",
        label="Built-in playbooks",
        status="ok",
        message=f"Loaded {len(playbooks)} built-in playbooks.",
        details={
            "count": len(playbooks),
            "categories": categories,
        },
    )


def _check_ai_provider() -> DoctorCheck:
    config_path = get_config_path()
    try:
        config = load_ai_config(config_path)
    except AIProviderError as exc:
        return DoctorCheck(
            name="ai_provider",
            label="AI provider",
            status="warning",
            message=str(exc),
            details={"config_path": str(config_path)},
        )

    api_key_status = _api_key_status(config)
    status = "warning" if api_key_status == "missing" else "ok"
    if status == "ok":
        message = "AI provider configuration is ready for dry-run validation."
    else:
        message = f"AI provider is configured, but {config.api_key_env} is missing."

    return DoctorCheck(
        name="ai_provider",
        label="AI provider",
        status=status,
        message=message,
        details={
            "provider": config.provider_name,
            "base_url": config.base_url,
            "endpoint": build_chat_completions_url(config.base_url),
            "model": config.default_model,
            "api_key": api_key_status,
            "api_key_env": config.api_key_env,
            "api_key_required": config.api_key_required,
            "config_path": str(config_path),
            "timeout": config.timeout,
        },
    )


def _check_updates(*, check_remote: bool, timeout: float) -> DoctorCheck:
    if not check_remote:
        return DoctorCheck(
            name="update_check",
            label="Update check",
            status="skipped",
            message="Remote release check skipped.",
            details={
                "latest_version": None,
                "changelog_url": CHANGELOG_URL,
            },
        )

    info = get_update_info(check_remote=True, timeout=timeout)
    details: dict[str, object] = {
        "current_version": info.current_version,
        "latest_version": info.latest_version,
        "update_available": info.update_available,
        "changelog_url": info.changelog_url,
        "latest_url": info.latest_url,
        "error": info.error,
    }
    if info.error:
        return DoctorCheck(
            name="update_check",
            label="Update check",
            status="warning",
            message=f"Could not check the latest GitHub release: {info.error}",
            details=details,
        )
    if info.update_available:
        return DoctorCheck(
            name="update_check",
            label="Update check",
            status="warning",
            message=f"Version {info.latest_version} is available.",
            details=details,
        )
    return DoctorCheck(
        name="update_check",
        label="Update check",
        status="ok",
        message="Installed version is current.",
        details=details,
    )


def _api_key_status(config: AIProviderConfig) -> str:
    if not config.api_key_required:
        return "not required"
    if config.api_key:
        return "stored"
    if resolve_api_key(config):
        return f"env:{config.api_key_env}"
    return "missing"


def _overall_status(statuses: Iterable[CheckStatus]) -> CheckStatus:
    status_list = list(statuses)
    if "error" in status_list:
        return "error"
    if "warning" in status_list:
        return "warning"
    return "ok"
