r"""Day26 smoke for FW text chat provider env readiness.

Default mode is fully source-tree safe. It checks env var names and boolean
presence only. Strict/local mode can be used by an operator after setting local
provider env vars, but it still never prints values, imports the real framework,
creates sessions, calls ask/ask_stream, or calls provider APIs.

Examples:

    python scripts\smoke_framework_text_chat_provider_env_readiness.py
    python scripts\smoke_framework_text_chat_provider_env_readiness.py --required-env GOOGLE_API_KEY
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig, load_config
from app.services.framework_text_chat_provider_env_readiness import (
    FrameworkTextChatProviderEnvReadinessService,
)


def _fake_config() -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root="<configured-framework-root>",
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_session_preflight_enabled=True,
    )


def _run_source_tree_smoke() -> None:
    blocked = FrameworkTextChatProviderEnvReadinessService(
        _fake_config(),
        environ={},
    ).run(required_env_names=("GOOGLE_API_KEY",))
    if blocked.status != "blocked":
        raise AssertionError(f"Expected blocked, got {blocked.status!r}")
    if blocked.required_env_names != ("GOOGLE_API_KEY",):
        raise AssertionError("Expected GOOGLE_API_KEY requirement")
    if any(status.is_set for status in blocked.env_statuses):
        raise AssertionError("Expected fake env to be unset")

    ready = FrameworkTextChatProviderEnvReadinessService(
        _fake_config(),
        environ={"GOOGLE_API_KEY": "configured-but-hidden"},
    ).run(required_env_names=("GOOGLE_API_KEY",))
    if ready.status != "ready":
        raise AssertionError(f"Expected ready, got {ready.status!r}")
    if "configured-but-hidden" in ready.safe_message:
        raise AssertionError("Readiness safe message must not expose env values")
    rendered = "\n".join(
        [ready.safe_message] + [status.safe_message for status in ready.env_statuses]
    )
    if "configured-but-hidden" in rendered:
        raise AssertionError("Env values must never be rendered")

    multi = FrameworkTextChatProviderEnvReadinessService(
        _fake_config(),
        environ={"GEMINI_API_KEY": "present-but-hidden"},
    ).run(required_env_names=("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    if multi.status != "blocked":
        raise AssertionError("Expected readiness to block when one required env is unset")
    if "present-but-hidden" in multi.safe_message:
        raise AssertionError("Multi-provider check must not expose env values")

    print("[smoke-framework-text-chat-provider-env-readiness] OK")


def _run_local_readiness(required_env_names: tuple[str, ...]) -> None:
    config = load_config()
    result = FrameworkTextChatProviderEnvReadinessService(config).run(
        required_env_names=required_env_names,
    )
    print("[smoke-framework-text-chat-provider-env-readiness-configured] RESULT")
    print("status:", result.status)
    print("required_env_names:", ", ".join(result.required_env_names))
    print("configured_provider_env_names:", ", ".join(result.configured_provider_env_names))
    print("safe_message:", result.safe_message)
    for status in result.env_statuses:
        print("env:", status.name, "set=", status.is_set)
    print("No env values were printed. No framework session or provider call was made.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FW text chat provider env readiness without exposing values."
    )
    parser.add_argument(
        "--required-env",
        action="append",
        default=[],
        help="Required provider env var name. Can be repeated. Defaults to GOOGLE_API_KEY.",
    )
    args = parser.parse_args()

    required = tuple(args.required_env) if args.required_env else ("GOOGLE_API_KEY",)
    if args.required_env:
        _run_local_readiness(required)
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
