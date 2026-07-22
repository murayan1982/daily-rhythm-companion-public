r"""Day25 smoke for FW text chat provider environment diagnosis.

The smoke is source-tree safe. It classifies sanitized session-creation failure
messages and checks env var presence by name only. It never imports the real
framework checkout, creates sessions, calls ask/ask_stream, or calls provider
APIs.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig
from app.services.framework_text_chat_provider_env_diagnosis import (
    FrameworkTextChatProviderEnvDiagnosisService,
    classify_framework_text_chat_session_failure,
    extract_provider_env_names,
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


def main() -> None:
    message = "GOOGLE_API_KEY is not defined."
    if extract_provider_env_names(message) != ("GOOGLE_API_KEY",):
        raise AssertionError("Expected GOOGLE_API_KEY extraction")
    if (
        classify_framework_text_chat_session_failure(
            exception_type="OSError",
            safe_message=message,
        )
        != "provider-env-missing"
    ):
        raise AssertionError("Expected provider-env-missing classification")

    missing_result = FrameworkTextChatProviderEnvDiagnosisService(
        _fake_config(),
        environ={},
    ).run_for_session_failure(
        exception_type="OSError",
        safe_message=message,
    )
    if missing_result.status != "blocked":
        raise AssertionError(f"Expected blocked, got {missing_result.status!r}")
    if missing_result.failure_kind != "provider-env-missing":
        raise AssertionError("Expected provider-env-missing failure kind")
    if missing_result.required_env_names != ("GOOGLE_API_KEY",):
        raise AssertionError("Expected GOOGLE_API_KEY requirement")
    if missing_result.env_statuses[0].is_set:
        raise AssertionError("Expected GOOGLE_API_KEY to be unset in fake env")
    if "configured-but-hidden" in missing_result.safe_message:
        raise AssertionError("Expected public-safe message without env values")

    configured_result = FrameworkTextChatProviderEnvDiagnosisService(
        _fake_config(),
        environ={"GOOGLE_API_KEY": "configured-but-hidden"},
    ).run_for_session_failure(
        exception_type="OSError",
        safe_message=message,
    )
    if configured_result.status != "configured":
        raise AssertionError(f"Expected configured, got {configured_result.status!r}")
    if not configured_result.env_statuses[0].is_set:
        raise AssertionError("Expected GOOGLE_API_KEY to be present in fake env")
    rendered = "\n".join(
        [configured_result.safe_message]
        + [status.safe_message for status in configured_result.env_statuses]
    )
    if "configured-but-hidden" in rendered:
        raise AssertionError("Env values must never be rendered")

    inventory = FrameworkTextChatProviderEnvDiagnosisService(
        _fake_config(),
        environ={"GEMINI_API_KEY": "present-but-hidden"},
    ).run_known_env_inventory()
    if inventory.failure_kind != "provider-env-inventory":
        raise AssertionError("Expected provider env inventory result")
    if "present-but-hidden" in inventory.safe_message:
        raise AssertionError("Inventory must not expose values")

    print("[smoke-framework-text-chat-provider-env-diagnosis] OK")


if __name__ == "__main__":
    main()
