from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from log_to_playbook import __version__
from log_to_playbook.ai import (
    AIProviderConfig,
    AIProviderError,
    build_chat_completions_url,
    explain_analysis,
    get_config_path,
    load_ai_config,
    mask_secret,
    save_ai_config,
    set_default_model,
    test_ai_provider,
)
from log_to_playbook.analyzer import analyze_log
from log_to_playbook.loader import load_builtin_playbooks
from log_to_playbook.redactor import redact_text
from log_to_playbook.renderer import render_json, render_markdown, render_text
from log_to_playbook.updates import (
    get_packaged_changelog,
    get_update_info,
    render_update_info,
)

FORMATS = {
    "json": render_json,
    "markdown": render_markdown,
    "text": render_text,
}

PLAYBOOK_TEMPLATE = """id: your-playbook-id
title: Your playbook title
category: linux
severity: low
risk: low

patterns:
  - "exact phrase from the log"

keywords:
  - keyword

summary: >
  Short diagnosis written in plain language.

causes:
  - First likely cause.

checks:
  - label: Safe diagnostic step
    command: "echo inspect first"
    risk: low

avoid:
  - "Avoid destructive commands as the first step."

references:
  - "https://example.com"
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="log2playbook",
        description="Turn logs and stack traces into practical debugging playbooks.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"log2playbook {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser("analyze", help="Analyze a log file or stdin.")
    analyze.add_argument(
        "path",
        nargs="?",
        default="-",
        help="Path to a log file. Use '-' or omit to read from stdin.",
    )
    analyze.add_argument(
        "--format",
        choices=sorted(FORMATS),
        default="text",
        help="Output format.",
    )
    analyze.add_argument(
        "--category",
        choices=["docker", "laravel", "linux", "node", "python"],
        help="Limit matching to a category.",
    )
    analyze.add_argument(
        "--privacy",
        action="store_true",
        help="Also redact email addresses.",
    )
    analyze.add_argument(
        "--show-redacted",
        action="store_true",
        help="Include the redacted input log in supported outputs.",
    )
    analyze.add_argument(
        "--output",
        help="Write the rendered report to a file instead of stdout.",
    )
    analyze.add_argument(
        "--ai",
        action="store_true",
        help="Add an AI suggestion using the configured OpenAI-compatible provider.",
    )

    subparsers.add_parser(
        "validate-playbooks",
        help="Validate built-in playbooks and print the loaded count.",
    )

    new_playbook = subparsers.add_parser(
        "new-playbook",
        help="Print or write a starter YAML playbook template.",
    )
    new_playbook.add_argument(
        "--output",
        help="Write the template to a file instead of stdout.",
    )

    changelog = subparsers.add_parser(
        "changelog",
        help="Show the packaged changelog.",
    )
    changelog.add_argument(
        "--output",
        help="Write the changelog to a file instead of stdout.",
    )

    update_info = subparsers.add_parser(
        "update-info",
        help="Show current version, latest release, and changelog links.",
    )
    update_info.add_argument(
        "--no-network",
        action="store_true",
        help="Skip the GitHub release check and show local update information.",
    )
    update_info.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format.",
    )
    update_info.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Network timeout in seconds for the GitHub release check.",
    )

    ai = subparsers.add_parser(
        "ai",
        help="Configure and test OpenAI-compatible AI providers.",
    )
    ai_subparsers = ai.add_subparsers(dest="ai_command")

    configure = ai_subparsers.add_parser(
        "configure",
        help="Save an OpenAI-compatible provider configuration.",
    )
    configure.add_argument("--provider-name", default="openai-compatible")
    configure.add_argument("--base-url", required=True)
    configure.add_argument("--model", required=True)
    configure.add_argument("--api-key-env", default="OPENAI_API_KEY")
    configure.add_argument("--api-key")
    configure.add_argument(
        "--no-api-key-required",
        action="store_true",
        help="Allow local or gateway providers that do not require a bearer token.",
    )
    configure.add_argument("--timeout", type=float, default=30.0)

    ai_subparsers.add_parser("show", help="Show the saved AI provider config.")

    set_model = ai_subparsers.add_parser(
        "set-model",
        help="Set the default model for the configured provider.",
    )
    set_model.add_argument("model")

    test_provider = ai_subparsers.add_parser(
        "test",
        help="Test the configured provider.",
    )
    test_provider.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and show the target URL without making a request.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return _analyze(args)
    if args.command == "validate-playbooks":
        playbooks = load_builtin_playbooks()
        print(f"Validated {len(playbooks)} playbooks.")
        return 0
    if args.command == "new-playbook":
        return _write_output(PLAYBOOK_TEMPLATE, args.output)
    if args.command == "changelog":
        return _write_output(get_packaged_changelog(), args.output)
    if args.command == "update-info":
        info = get_update_info(
            check_remote=not args.no_network,
            timeout=args.timeout,
        )
        if args.format == "json":
            rendered = json.dumps(asdict(info), indent=2, ensure_ascii=False)
        else:
            rendered = render_update_info(info)
        return _write_output(rendered, None)
    if args.command == "ai":
        return _ai(args)

    parser.print_help()
    return 0


def _analyze(args: argparse.Namespace) -> int:
    text = _read_input(args.path)
    result = analyze_log(
        text,
        category=args.category,
        privacy=args.privacy,
        include_redacted_log=args.show_redacted,
    )
    if args.ai:
        redacted_log = redact_text(text, privacy=args.privacy).text
        try:
            result.ai_suggestion = explain_analysis(result, redacted_log)
        except AIProviderError as exc:
            result.ai_suggestion = f"AI suggestion unavailable: {exc}"
    rendered = FORMATS[args.format](result)
    return _write_output(rendered, args.output)


def _ai(args: argparse.Namespace) -> int:
    if args.ai_command == "configure":
        config = AIProviderConfig(
            provider_name=args.provider_name,
            base_url=args.base_url,
            default_model=args.model,
            api_key_env=args.api_key_env,
            api_key=args.api_key,
            api_key_required=not args.no_api_key_required,
            timeout=args.timeout,
        )
        path = save_ai_config(config)
        print(f"Saved AI provider config: {path}")
        print(f"Provider: {config.provider_name}")
        print(f"Base URL: {config.base_url}")
        print(f"Default model: {config.default_model}")
        return 0

    if args.ai_command == "show":
        try:
            config = load_ai_config()
        except AIProviderError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(_render_ai_config(config))
        return 0

    if args.ai_command == "set-model":
        try:
            config = set_default_model(args.model)
        except AIProviderError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"Default model: {config.default_model}")
        return 0

    if args.ai_command == "test":
        try:
            config = load_ai_config()
        except AIProviderError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        if args.dry_run:
            print("Configuration OK")
            print(f"Provider: {config.provider_name}")
            print(f"Model: {config.default_model}")
            print(f"Endpoint: {build_chat_completions_url(config.base_url)}")
            return 0
        result = test_ai_provider(config)
        if result.ok:
            print("Provider test passed.")
            print(f"Provider: {result.provider_name}")
            print(f"Model: {result.model}")
            print(f"Response: {result.message}")
            return 0
        print(result.message, file=sys.stderr)
        if result.error:
            print(result.error, file=sys.stderr)
        return 1

    print("Run `log2playbook ai --help` for available AI commands.")
    return 0


def _render_ai_config(config: AIProviderConfig) -> str:
    return "\n".join(
        [
            f"Provider: {config.provider_name}",
            f"Base URL: {config.base_url}",
            f"Chat completions URL: {build_chat_completions_url(config.base_url)}",
            f"Default model: {config.default_model}",
            f"API key env: {config.api_key_env}",
            f"Stored API key: {mask_secret(config.api_key)}",
            f"API key required: {config.api_key_required}",
            f"Timeout: {config.timeout}",
            f"Config path: {get_config_path()}",
        ]
    )


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _write_output(content: str, output: str | None) -> int:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
