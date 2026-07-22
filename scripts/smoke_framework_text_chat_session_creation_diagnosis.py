r"""Day21/Day24 smoke for framework text chat session creation diagnosis.

Default mode uses a Temporary fake framework module to verify that diagnosis can
keep the configured import layout active while it creates a session. The fake
framework uses framework/registry.py and performs a lazy top-level ``import registry`` inside
create_text_chat_session, which guards the Day24 regression.

Strict operator mode can diagnose the configured real framework checkout:

    python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig, load_config
from app.services.framework_text_chat_provider_env_diagnosis import (
    extract_provider_env_names,
)
from app.services.framework_text_chat_provider_env_readiness import (
    FrameworkTextChatProviderEnvReadinessService,
)
from app.services.framework_text_chat_session_diagnosis import (
    FrameworkTextChatSessionDiagnosisService,
)


def _fake_config(project_root: str | None) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=project_root,
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_smoke_enabled=True,
        framework_text_chat_preflight_enabled=True,
        framework_text_chat_session_preflight_enabled=True,
    )


def _run_fake_diagnosis() -> None:
    previous_framework = sys.modules.pop("framework", None)
    previous_registry = sys.modules.pop("registry", None)
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            framework_dir = root / "framework"
            framework_dir.mkdir()
            (framework_dir / "registry.py").write_text(
                "\n".join(
                    [
                        "class RegistryMarker:",
                        "    pass",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (framework_dir / "__init__.py").write_text(
                "\n".join(
                    [
                        "from pathlib import Path",
                        "",
                        "class TextChatSessionInfo:",
                        "    pass",
                        "",
                        "class FakeTextChatSession:",
                        "    def get_session_info(self):",
                        "        return TextChatSessionInfo()",
                        "    def ask(self, *args, **kwargs):",
                        "        raise AssertionError('ask must not be called')",
                        "    def ask_stream(self, *args, **kwargs):",
                        "        raise AssertionError('ask_stream must not be called')",
                        "",
                        "class FacadeConfigError(Exception):",
                        "    pass",
                        "",
                        "def create_text_chat_session(*args, **kwargs):",
                        "    import registry",
                        "    if registry is None:",
                        "        raise AssertionError('registry import failed')",
                        "    if not Path('presets/text_chat.json').exists():",
                        "        raise FacadeConfigError('Preset file not found: presets/text_chat.json')",
                        "    return FakeTextChatSession()",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            presets = root / "presets"
            presets.mkdir()
            (presets / "text_chat.json").write_text("{}", encoding="utf-8")

            result = FrameworkTextChatSessionDiagnosisService(
                _fake_config(str(root))
            ).run()
    finally:
        sys.modules.pop("framework", None)
        sys.modules.pop("registry", None)
        if previous_framework is not None:
            sys.modules["framework"] = previous_framework
        if previous_registry is not None:
            sys.modules["registry"] = previous_registry

    if result.status != "created":
        raise AssertionError(f"Expected created, got {result.status!r}")
    if not result.likely_cwd_dependency:
        raise AssertionError("Expected likely_cwd_dependency=True")
    if len(result.attempts) != 2:
        raise AssertionError("Expected two diagnosis attempts")
    if result.attempts[0].exception_type != "FacadeConfigError":
        raise AssertionError("Expected current-CWD attempt FacadeConfigError")
    if result.attempts[1].status != "created":
        raise AssertionError("Expected framework-root-CWD attempt to create session")
    if "framework-package-dir-fallback" not in result.attempts[1].safe_message:
        raise AssertionError("Expected Day24 import setup fallback to remain active")
    if any(attempt.exception_type == "ModuleNotFoundError" for attempt in result.attempts):
        raise AssertionError("Day24 import setup should avoid false registry import misses")

    print("[smoke-framework-text-chat-session-diagnosis] OK")


def _run_real_diagnosis() -> None:
    config = load_config()
    result = FrameworkTextChatSessionDiagnosisService(config).run()

    print("[smoke-framework-text-chat-session-diagnosis-configured] RESULT")
    print("status:", result.status)
    print("module:", result.module_name)
    print("project_root_shape:", result.project_root_shape)
    print("likely_cwd_dependency:", result.likely_cwd_dependency)
    for attempt in result.attempts:
        print("attempt:", attempt.attempt_name)
        print("  status:", attempt.status)
        print("  cwd_shape:", attempt.cwd_shape)
        print("  exception_type:", attempt.exception_type)
        print("  safe_message:", attempt.safe_message)
        print("  failure_kind:", attempt.failure_kind)
        print("  session_created:", attempt.session_created)
        print("  has_session_info:", attempt.has_session_info)
        if attempt.failure_kind == "provider-env-missing":
            _print_provider_env_readiness(config, attempt.safe_message)
    print("No ask, ask_stream, or provider call was made.")


def _print_provider_env_readiness(config: AppConfig, safe_message: str) -> None:
    required = extract_provider_env_names(safe_message) or ("GOOGLE_API_KEY",)
    readiness = FrameworkTextChatProviderEnvReadinessService(config).run(
        required_env_names=required
    )
    print("  provider_env_readiness_status:", readiness.status)
    print("  provider_env_required_names:", ", ".join(readiness.required_env_names))
    print("  provider_env_safe_message:", readiness.safe_message)
    for status in readiness.env_statuses:
        print("  provider_env:", status.name, "set=", status.is_set)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat session creation diagnosis."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help="Diagnose the configured real framework checkout instead of fake framework.",
    )
    args = parser.parse_args()

    if args.require_real_framework:
        if os.getenv("DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1 "
                "before running strict session diagnosis."
            )
        _run_real_diagnosis()
        return

    _run_fake_diagnosis()


if __name__ == "__main__":
    main()
