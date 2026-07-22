r"""Day27 smoke for provider env local opt-in instructions.

Default mode is source-tree only and uses fake in-memory environment mappings.
It verifies that a locally configured provider env name can move readiness from
blocked to ready without exposing any secret value.

Optional local mode only prints set/unset status for the operator environment:

    python scripts\smoke_framework_text_chat_provider_env_operator_opt_in.py --check-local --required-env GOOGLE_API_KEY
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

_SECRET_SENTINEL = "configured-but-hidden-local-test-value"


def _fake_config() -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root="<configured-framework-root>",
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_session_preflight_enabled=True,
    )


def _assert_no_secret_rendered(text: str) -> None:
    if _SECRET_SENTINEL in text:
        raise AssertionError("Provider env opt-in smoke rendered a secret-like value")


def _run_source_tree_smoke() -> None:
    config = _fake_config()
    blocked = FrameworkTextChatProviderEnvReadinessService(
        config,
        environ={},
    ).run(required_env_names=("GOOGLE_API_KEY",))
    ready = FrameworkTextChatProviderEnvReadinessService(
        config,
        environ={"GOOGLE_API_KEY": _SECRET_SENTINEL},
    ).run(required_env_names=("GOOGLE_API_KEY",))

    if blocked.status != "blocked":
        raise AssertionError(f"Expected blocked with no provider env, got {blocked.status!r}")
    if ready.status != "ready":
        raise AssertionError(f"Expected ready with local provider env, got {ready.status!r}")
    if ready.configured_provider_env_names != ("GOOGLE_API_KEY",):
        raise AssertionError("Expected GOOGLE_API_KEY to be the configured provider env name")

    rendered = "\n".join(
        [
            blocked.safe_message,
            ready.safe_message,
            *(status.safe_message for status in ready.env_statuses),
        ]
    )
    _assert_no_secret_rendered(rendered)

    print("[smoke-framework-text-chat-provider-env-operator-opt-in] OK")


def _run_local_check(required_env_names: tuple[str, ...]) -> None:
    config = load_config()
    result = FrameworkTextChatProviderEnvReadinessService(config).run(
        required_env_names=required_env_names,
    )

    print("[smoke-framework-text-chat-provider-env-operator-opt-in-configured] RESULT")
    print("status:", result.status)
    print("required_env_names:", ", ".join(result.required_env_names))
    print("configured_provider_env_names:", ", ".join(result.configured_provider_env_names))
    print("safe_message:", result.safe_message)
    for status in result.env_statuses:
        print("env:", status.name, "set=", status.is_set)
    print("No env values were printed. No framework session or provider call was made.")


def _parse_required_env_names(raw_values: list[str]) -> tuple[str, ...]:
    names: list[str] = []
    for raw in raw_values:
        for part in raw.replace(",", " ").split():
            name = part.strip().upper()
            if name and name not in names:
                names.append(name)
    return tuple(names) or ("GOOGLE_API_KEY",)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Provider env local opt-in smoke for FW text chat preflight."
    )
    parser.add_argument(
        "--check-local",
        action="store_true",
        help="Read local operator env/backend/.env and print set/unset status only.",
    )
    parser.add_argument(
        "--required-env",
        action="append",
        default=[],
        help="Required provider env name. Can be repeated or comma-separated.",
    )
    args = parser.parse_args()

    required = _parse_required_env_names(args.required_env)
    if args.check_local:
        _run_local_check(required)
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
