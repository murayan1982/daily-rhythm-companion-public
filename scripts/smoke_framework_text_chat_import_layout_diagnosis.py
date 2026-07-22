r"""Day23 smoke for framework text chat import layout diagnosis.

Default mode uses a temporary fake framework checkout to verify that the
framework package and a package-local registry module can be diagnosed without
creating sessions, sending messages, or calling provider APIs.

Strict operator mode can diagnose the configured real framework checkout:

    python scripts\smoke_framework_text_chat_import_layout_diagnosis.py --require-real-framework
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
from app.services.framework_text_chat_import_layout_diagnosis import (
    FrameworkTextChatImportLayoutDiagnosisService,
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
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        framework_dir = root / "framework"
        framework_dir.mkdir()
        (framework_dir / "__init__.py").write_text(
            "PUBLIC_API_VISIBLE = True\n",
            encoding="utf-8",
        )
        (framework_dir / "registry.py").write_text(
            "REGISTRY_VISIBLE = True\n",
            encoding="utf-8",
        )

        result = FrameworkTextChatImportLayoutDiagnosisService(
            _fake_config(str(root))
        ).run()

    if result.status != "resolved":
        raise AssertionError(f"Expected resolved, got {result.status!r}")
    if "<configured-framework-root>/framework/registry.py" not in result.registry_file_shapes:
        raise AssertionError("Expected registry.py shape under framework package")

    by_name = {candidate.candidate_name: candidate for candidate in result.candidates}
    root_only = by_name["configured-root-only"]
    package_only = by_name["framework-package-dir-only"]
    combined = by_name["configured-root-plus-framework-package-dir"]

    if root_only.framework_spec_status != "found":
        raise AssertionError("Expected framework spec from configured root")
    if root_only.registry_spec_status != "missing":
        raise AssertionError("Expected registry to be missing from configured root only")
    if package_only.framework_spec_status != "missing":
        raise AssertionError("Expected framework to be missing from package dir only")
    if package_only.registry_spec_status != "found":
        raise AssertionError("Expected registry to be found from package dir only")
    if combined.framework_spec_status != "found" or combined.registry_spec_status != "found":
        raise AssertionError("Expected combined layout to resolve both specs")
    if "adapter sys.path" not in result.recommendation:
        raise AssertionError("Expected adapter sys.path recommendation")

    print("[smoke-framework-text-chat-import-layout-diagnosis] OK")


def _run_real_diagnosis() -> None:
    config = load_config()
    result = FrameworkTextChatImportLayoutDiagnosisService(config).run()

    print("[smoke-framework-text-chat-import-layout-diagnosis-configured] RESULT")
    print("status:", result.status)
    print("project_root_shape:", result.project_root_shape)
    print("registry_file_shapes:")
    for shape in result.registry_file_shapes:
        print("  -", shape)
    for candidate in result.candidates:
        print("candidate:", candidate.candidate_name)
        print("  sys_path_shapes:", ", ".join(candidate.sys_path_shapes))
        print("  framework_spec_status:", candidate.framework_spec_status)
        print("  registry_spec_status:", candidate.registry_spec_status)
        print("  safe_message:", candidate.safe_message)
    print("recommendation:", result.recommendation)
    print("No session was created and no ask, ask_stream, or provider call was made.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat import layout diagnosis."
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
                "before running strict import layout diagnosis."
            )
        _run_real_diagnosis()
        return

    _run_fake_diagnosis()


if __name__ == "__main__":
    main()
