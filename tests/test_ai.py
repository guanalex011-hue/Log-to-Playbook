from __future__ import annotations

import json

import pytest

from log_to_playbook.ai import (
    AIProviderConfig,
    AIProviderError,
    build_chat_completions_url,
    build_explanation_messages,
    call_chat_completion,
    load_ai_config,
    mask_secret,
    save_ai_config,
    set_default_model,
    test_ai_provider,
)
from log_to_playbook.analyzer import analyze_log


def test_save_and_load_ai_config(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("LOG2PLAYBOOK_CONFIG", str(config_path))

    config = AIProviderConfig(
        provider_name="openai-compatible",
        base_url="https://api.example.com/v1",
        default_model="example-model",
        api_key_env="EXAMPLE_API_KEY",
        api_key=None,
        api_key_required=True,
        timeout=12.5,
    )

    save_ai_config(config)

    assert load_ai_config() == config
    assert json.loads(config_path.read_text(encoding="utf-8"))["default_model"] == (
        "example-model"
    )


def test_set_default_model_updates_existing_config(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("LOG2PLAYBOOK_CONFIG", str(tmp_path / "config.json"))
    save_ai_config(
        AIProviderConfig(
            provider_name="local",
            base_url="http://localhost:1234/v1",
            default_model="old-model",
            api_key_env="LOCAL_API_KEY",
            api_key=None,
            api_key_required=False,
            timeout=5,
        )
    )

    updated = set_default_model("new-model")

    assert updated.default_model == "new-model"
    assert load_ai_config().default_model == "new-model"


def test_build_chat_completions_url_accepts_base_or_full_url() -> None:
    assert build_chat_completions_url("https://api.example.com/v1") == (
        "https://api.example.com/v1/chat/completions"
    )
    assert build_chat_completions_url(
        "https://api.example.com/v1/chat/completions"
    ) == "https://api.example.com/v1/chat/completions"


def test_call_chat_completion_uses_openai_compatible_payload(monkeypatch) -> None:
    monkeypatch.setenv("EXAMPLE_API_KEY", "test-key")
    seen: dict[str, object] = {}

    def requester(
        url: str,
        payload: dict[str, object],
        headers: dict[str, str],
        timeout: float,
    ) -> dict[str, object]:
        seen["url"] = url
        seen["payload"] = payload
        seen["headers"] = headers
        seen["timeout"] = timeout
        return {"choices": [{"message": {"content": "provider ok"}}]}

    config = AIProviderConfig(
        provider_name="example",
        base_url="https://api.example.com/v1",
        default_model="example-model",
        api_key_env="EXAMPLE_API_KEY",
        api_key=None,
        api_key_required=True,
        timeout=9,
    )

    content = call_chat_completion(
        config,
        [{"role": "user", "content": "hello"}],
        requester=requester,
    )

    assert content == "provider ok"
    assert seen["url"] == "https://api.example.com/v1/chat/completions"
    assert seen["payload"] == {
        "model": "example-model",
        "messages": [{"role": "user", "content": "hello"}],
        "temperature": 0.2,
    }
    assert seen["headers"] == {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-key",
    }
    assert seen["timeout"] == 9


def test_call_chat_completion_allows_local_provider_without_key() -> None:
    def requester(
        _url: str,
        _payload: dict[str, object],
        headers: dict[str, str],
        _timeout: float,
    ) -> dict[str, object]:
        assert "Authorization" not in headers
        return {"choices": [{"message": {"content": "local ok"}}]}

    config = AIProviderConfig(
        provider_name="local",
        base_url="http://localhost:1234/v1",
        default_model="local-model",
        api_key_env="LOCAL_API_KEY",
        api_key=None,
        api_key_required=False,
        timeout=5,
    )

    assert (
        call_chat_completion(
            config,
            [{"role": "user", "content": "hi"}],
            requester=requester,
        )
        == "local ok"
    )


def test_call_chat_completion_requires_key_when_configured(monkeypatch) -> None:
    monkeypatch.delenv("MISSING_API_KEY", raising=False)
    config = AIProviderConfig(
        provider_name="example",
        base_url="https://api.example.com/v1",
        default_model="example-model",
        api_key_env="MISSING_API_KEY",
        api_key=None,
        api_key_required=True,
        timeout=5,
    )

    with pytest.raises(AIProviderError, match="API key"):
        call_chat_completion(config, [{"role": "user", "content": "hi"}])


def test_test_ai_provider_returns_success(monkeypatch) -> None:
    monkeypatch.setenv("EXAMPLE_API_KEY", "test-key")

    def requester(
        _url: str,
        _payload: dict[str, object],
        _headers: dict[str, str],
        _timeout: float,
    ) -> dict[str, object]:
        return {"choices": [{"message": {"content": "pong"}}]}

    result = test_ai_provider(
        AIProviderConfig(
            provider_name="example",
            base_url="https://api.example.com/v1",
            default_model="example-model",
            api_key_env="EXAMPLE_API_KEY",
            api_key=None,
            api_key_required=True,
            timeout=5,
        ),
        requester=requester,
    )

    assert result.ok is True
    assert result.model == "example-model"
    assert result.message == "pong"


def test_build_explanation_messages_include_analysis_context() -> None:
    analysis = analyze_log("ModuleNotFoundError: No module named 'pandas'")

    messages = build_explanation_messages(analysis, "ModuleNotFoundError")

    assert messages[0]["role"] == "system"
    assert "safe debugging assistant" in messages[0]["content"]
    assert "Python module not found" in messages[1]["content"]
    assert "ModuleNotFoundError" in messages[1]["content"]


def test_mask_secret() -> None:
    assert mask_secret("sk-abcdef123456") == "sk-a...3456"
    assert mask_secret(None) == "not stored"
