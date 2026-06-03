from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from log_to_playbook.models import AnalysisResult

DEFAULT_PROVIDER_NAME = "openai-compatible"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_MODEL = "gpt-4o-mini"

AIRequester = Callable[
    [str, dict[str, object], dict[str, str], float],
    Mapping[str, object],
]


class AIProviderError(RuntimeError):
    """Raised when an AI provider cannot be configured or called."""


@dataclass(frozen=True)
class AIProviderConfig:
    provider_name: str = DEFAULT_PROVIDER_NAME
    base_url: str = DEFAULT_BASE_URL
    default_model: str = DEFAULT_MODEL
    api_key_env: str = DEFAULT_API_KEY_ENV
    api_key: str | None = None
    api_key_required: bool = True
    timeout: float = 30.0


@dataclass(frozen=True)
class AITestResult:
    ok: bool
    provider_name: str
    base_url: str
    model: str
    message: str
    error: str | None = None


def get_config_path() -> Path:
    """Return the AI config path, allowing tests and automation to override it."""
    override = os.environ.get("LOG2PLAYBOOK_CONFIG")
    if override:
        return Path(override)

    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "log-to-playbook" / "config.json"


def load_ai_config(path: Path | None = None) -> AIProviderConfig:
    config_path = path or get_config_path()
    if not config_path.exists():
        raise AIProviderError(
            "AI provider is not configured. Run `log2playbook ai configure` first."
        )

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return AIProviderConfig(
        provider_name=str(raw.get("provider_name", DEFAULT_PROVIDER_NAME)),
        base_url=str(raw.get("base_url", DEFAULT_BASE_URL)),
        default_model=str(raw.get("default_model", DEFAULT_MODEL)),
        api_key_env=str(raw.get("api_key_env", DEFAULT_API_KEY_ENV)),
        api_key=_optional_str(raw.get("api_key")),
        api_key_required=bool(raw.get("api_key_required", True)),
        timeout=float(raw.get("timeout", 30.0)),
    )


def save_ai_config(config: AIProviderConfig, path: Path | None = None) -> Path:
    config_path = path or get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(asdict(config), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return config_path


def set_default_model(model: str, path: Path | None = None) -> AIProviderConfig:
    current = load_ai_config(path)
    updated = AIProviderConfig(
        provider_name=current.provider_name,
        base_url=current.base_url,
        default_model=model,
        api_key_env=current.api_key_env,
        api_key=current.api_key,
        api_key_required=current.api_key_required,
        timeout=current.timeout,
    )
    save_ai_config(updated, path)
    return updated


def build_chat_completions_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def resolve_api_key(config: AIProviderConfig) -> str | None:
    if config.api_key:
        return config.api_key
    return os.environ.get(config.api_key_env)


def call_chat_completion(
    config: AIProviderConfig,
    messages: Sequence[Mapping[str, str]],
    *,
    requester: AIRequester | None = None,
    temperature: float = 0.2,
) -> str:
    api_key = resolve_api_key(config)
    if config.api_key_required and not api_key:
        raise AIProviderError(
            "API key is required. "
            f"Set {config.api_key_env} or reconfigure the provider."
        )

    payload: dict[str, object] = {
        "model": config.default_model,
        "messages": [dict(message) for message in messages],
        "temperature": temperature,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = requester or _post_json
    try:
        response = request(
            build_chat_completions_url(config.base_url),
            payload,
            headers,
            config.timeout,
        )
    except (HTTPError, OSError, URLError) as exc:
        raise AIProviderError(str(exc)) from exc

    return _extract_chat_content(response)


def test_ai_provider(
    config: AIProviderConfig,
    *,
    requester: AIRequester | None = None,
) -> AITestResult:
    try:
        message = call_chat_completion(
            config,
            [
                {
                    "role": "user",
                    "content": "Reply with a short provider health check message.",
                }
            ],
            requester=requester,
            temperature=0,
        )
    except AIProviderError as exc:
        return AITestResult(
            ok=False,
            provider_name=config.provider_name,
            base_url=config.base_url,
            model=config.default_model,
            message="Provider test failed.",
            error=str(exc),
        )

    return AITestResult(
        ok=True,
        provider_name=config.provider_name,
        base_url=config.base_url,
        model=config.default_model,
        message=message,
        error=None,
    )


test_ai_provider.__test__ = False  # type: ignore[attr-defined]


def build_explanation_messages(
    result: AnalysisResult,
    redacted_log: str,
) -> list[dict[str, str]]:
    checks = "\n".join(
        f"- {check.label}: {check.command or 'no command'} (risk: {check.risk})"
        for check in result.checks
    )
    avoid = "\n".join(f"- {item}" for item in result.avoid)
    return [
        {
            "role": "system",
            "content": (
                "You are a safe debugging assistant. Explain the log in plain "
                "language, keep advice practical, and do not invent destructive "
                "commands."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Detected playbook: {result.title}\n"
                f"Risk: {result.risk}\n"
                f"Summary: {result.summary}\n"
                f"Checks:\n{checks or '- No checks available'}\n"
                f"Avoid:\n{avoid or '- Prefer read-only diagnosis first'}\n"
                f"Redacted log:\n{redacted_log[:4000]}\n\n"
                "Return a short explanation and 3 safe next steps."
            ),
        },
    ]


def explain_analysis(
    result: AnalysisResult,
    redacted_log: str,
    config: AIProviderConfig | None = None,
) -> str:
    provider_config = config or load_ai_config()
    return call_chat_completion(
        provider_config,
        build_explanation_messages(result, redacted_log),
    )


def mask_secret(secret: str | None) -> str:
    if not secret:
        return "not stored"
    if len(secret) <= 8:
        return "***"
    return f"{secret[:4]}...{secret[-4:]}"


def _post_json(
    url: str,
    payload: dict[str, object],
    headers: dict[str, str],
    timeout: float,
) -> Mapping[str, object]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        raw: object = json.loads(response.read().decode("utf-8"))
    if not isinstance(raw, dict):
        raise AIProviderError("Provider returned a non-object JSON response.")
    return raw


def _extract_chat_content(response: Mapping[str, object]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AIProviderError("Provider response did not include choices.")

    first = choices[0]
    if not isinstance(first, dict):
        raise AIProviderError("Provider response choice is invalid.")

    message = first.get("message")
    if not isinstance(message, dict):
        raise AIProviderError("Provider response did not include message content.")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise AIProviderError("Provider response content is empty.")
    return content.strip()


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
