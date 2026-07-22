r"""Day28 smoke for public-safe framework session-created evidence.

Default mode uses a temporary fake framework module. It verifies that Day28 can
render the session-created evidence shape without exposing secrets and without
calling ask, ask_stream, or provider APIs.

Optional local mode only runs the public-safe evidence renderer after strict
operator session diagnosis prerequisites are configured:

    python scripts\smoke_framework_text_chat_session_created_evidence.py --require-real-framework
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig, load_config
from app.services.framework_text_chat_session_created_evidence import (
    FrameworkTextChatSessionCreatedEvidenceService,
    render_session_created_evidence,
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


def _run_fake_diagnosis():
    previous_framework = sys.modules.pop("framework", None)
    previous_registry = sys.modules.pop("registry", None)
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            framework_dir = root / "framework"
            framework_dir.mkdir()
            (framework_dir / "registry.py").write_text(
                "class RegistryMarker:\n    pass\n",
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

            return FrameworkTextChatSessionDiagnosisService(
                _fake_config(str(root))
            ).run()
    finally:
        sys.modules.pop("framework", None)
        sys.modules.pop("registry", None)
        if previous_framework is not None:
            sys.modules["framework"] = previous_framework
        if previous_registry is not None:
            sys.modules["registry"] = previous_registry


def _assert_public_safe(rendered: str) -> None:
    forbidden_patterns = [
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
        r"Authorization:\s*Bearer",
        r"refresh_token\s*[:=]\s*['\"][^'\"]+",
        r"access_token\s*[:=]\s*['\"][^'\"]+",
        r"client_secret\s*[:=]\s*['\"][^'\"]+",
        r"[A-Za-z]:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, rendered, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value found in evidence: {pattern}")


def _run_source_tree_smoke() -> None:
    result = _run_fake_diagnosis()
    evidence = FrameworkTextChatSessionCreatedEvidenceService().from_diagnosis(result)
    rendered = render_session_created_evidence(evidence)

    if result.status != "created":
        raise AssertionError(f"Expected created diagnosis, got {result.status!r}")
    if evidence.status != "created":
        raise AssertionError(f"Expected created evidence, got {evidence.status!r}")
    if evidence.created_attempt_name != "framework-root-cwd":
        raise AssertionError("Expected framework-root-cwd to be the created attempt")
    if evidence.current_cwd_exception_type != "FacadeConfigError":
        raise AssertionError("Expected current-cwd FacadeConfigError evidence")
    if not evidence.session_created or not evidence.has_session_info:
        raise AssertionError("Expected session_created and has_session_info evidence")
    if "design-explicit-live-text-chat-message-gate" not in rendered:
        raise AssertionError("Expected next-step gate in rendered evidence")
    if any(needle in rendered for needle in [".ask(", ".ask_stream(", "provider response"]):
        raise AssertionError("Rendered evidence must not imply message/provider execution")
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-session-created-evidence] OK")


def _run_real_evidence() -> None:
    config = load_config()
    result = FrameworkTextChatSessionDiagnosisService(config).run()
    evidence = FrameworkTextChatSessionCreatedEvidenceService().from_diagnosis(result)
    rendered = render_session_created_evidence(evidence)
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-session-created-evidence-configured] RESULT")
    print(rendered)
    print("No ask, ask_stream, or provider call was made by this evidence renderer.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat session-created evidence smoke."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help="Run evidence rendering against the configured real framework checkout.",
    )
    args = parser.parse_args()

    if args.require_real_framework:
        if os.getenv("DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1 "
                "before running strict session-created evidence."
            )
        _run_real_evidence()
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
