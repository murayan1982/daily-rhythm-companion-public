from __future__ import annotations

import argparse
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig, load_config


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _display_value(value: str | None) -> str:
    return value if value else "<unset>"


def _print_config_summary(config: AppConfig) -> None:
    print("[framework-local-config-check]")
    print(f"conversation_engine={config.conversation_engine}")
    print(f"framework_project_root={_display_value(config.framework_project_root)}")
    print(f"framework_preset={config.framework_preset}")
    print(f"framework_character={config.framework_character}")
    print(f"framework_adapter_mode={config.framework_adapter_mode}")
    print(f"GEMINI_API_KEY: set={bool(config.gemini_api_key)}")
    print(f"XAI_API_KEY: set={bool(config.xai_api_key)}")


def _resolve_framework_root(config: AppConfig, *, require_config: bool) -> Path | None:
    root = config.framework_project_root

    if not root:
        message = "FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is not configured."
        if require_config:
            raise AssertionError(message)

        print(f"[framework-local-config-check-v0.30.0] SKIP {message}")
        return None

    framework_root = Path(root).expanduser().resolve()

    _expect(
        framework_root.exists(),
        f"FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT does not exist: {framework_root}",
    )
    _expect(
        framework_root.is_dir(),
        f"FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is not a directory: {framework_root}",
    )

    facade_path = framework_root / "framework" / "facade.py"
    _expect(
        facade_path.exists(),
        f"framework/facade.py was not found under: {framework_root}",
    )

    return framework_root


def _load_create_text_chat_session(framework_root: Path) -> Any:
    framework_root_str = str(framework_root)

    if framework_root_str not in sys.path:
        sys.path.insert(0, framework_root_str)

    try:
        facade_module = import_module("framework.facade")
        create_text_chat_session = getattr(facade_module, "create_text_chat_session")
    except Exception as exc:
        raise AssertionError(
            "Failed to import framework.facade.create_text_chat_session."
        ) from exc

    return create_text_chat_session


def _create_session_without_asking(
    *,
    framework_root: Path,
    config: AppConfig,
    create_text_chat_session: Any,
) -> Any:
    previous_cwd = Path.cwd()

    try:
        os.chdir(framework_root)
        session = create_text_chat_session(
            preset=config.framework_preset,
            character_name=config.framework_character,
        )
    finally:
        os.chdir(previous_cwd)

    _expect(
        Path.cwd() == previous_cwd,
        "current working directory should be restored after session creation",
    )

    return session


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Check optional AI Character Framework local configuration. "
            "By default, this script only validates config and facade import. "
            "It does not call session.ask()."
        )
    )
    parser.add_argument(
        "--create-session",
        action="store_true",
        help="Also create a text chat session. This still does not call ask().",
    )
    parser.add_argument(
        "--require-config",
        action="store_true",
        help="Fail instead of SKIP when FRAMEWORK_ROOT is not configured.",
    )
    args = parser.parse_args()

    config = load_config()
    _print_config_summary(config)

    framework_root = _resolve_framework_root(
        config,
        require_config=args.require_config,
    )
    if framework_root is None:
        return

    create_text_chat_session = _load_create_text_chat_session(framework_root)

    print(f"framework_root={framework_root}")
    print("facade_importable=True")

    if args.create_session:
        session = _create_session_without_asking(
            framework_root=framework_root,
            config=config,
            create_text_chat_session=create_text_chat_session,
        )
        print(f"session_created=True")
        print(f"session_type={type(session).__name__}")
    else:
        print("session_created=False")

    print("[framework-local-config-check-v0.30.0] OK")


if __name__ == "__main__":
    main()
